# Feature 04: Migrazione da SQLite a MongoDB 8.0

## Panoramica

Migrazione completa del layer di persistenza da SQLite (via SQLModel/SQLAlchemy) a MongoDB 8.0, utilizzando **Motor** (driver async ufficiale) e **Beanie** (ODM async basato su Pydantic v2, compatibile nativamente con FastAPI).

---

## Motivazioni

- SQLite non supporta accessi concorrenti in scrittura; MongoDB gestisce nativamente la concorrenza.
- Il modello a documenti di MongoDB si adatta naturalmente ai dati annidati gia' presenti (steps JSON nei TestCaseDefinition, test steps nei TestCase).
- Scalabilita' orizzontale futura (replica set, sharding).
- Query aggregate native per statistiche sui run.

---

## Modulo Q: Infrastruttura MongoDB

### FR-Q1 (Docker Compose)
Il file `docker-compose.yml` deve:
- Aggiungere un servizio `mongodb` basato sull'immagine `mongo:8.0`.
- Esporre la porta `27017` solo sulla rete interna `redstone-network`.
- Montare un volume persistente `mongo-data` su `/data/db`.
- Configurare le variabili `MONGO_INITDB_DATABASE=redstone_reporter`.
- Il servizio `redstone-reporter` deve dipendere da `mongodb` con `depends_on` e `condition: service_healthy`.
- Healthcheck MongoDB: `mongosh --eval "db.adminCommand('ping')"`.

### FR-Q2 (Configurazione)
Il file `app/config.py` deve:
- Sostituire `DATABASE_URL` (SQLite) con `MONGODB_URI` (default: `mongodb://mongodb:27017`).
- Aggiungere `MONGODB_DATABASE` (default: `redstone_reporter`).
- Rimuovere la creazione della directory `data/` per il file SQLite (non piu' necessaria; la directory screenshots resta).

### FR-Q3 (Dipendenze)
Il file `requirements.txt` deve:
- Rimuovere `sqlmodel`.
- Aggiungere `motor>=3.6` (driver async MongoDB).
- Aggiungere `beanie>=1.26` (ODM Pydantic v2 per MongoDB).

---

## Modulo R: Modelli Documento (Beanie)

Tutti i modelli devono estendere `beanie.Document` e usare `PydanticObjectId` come tipo per l'ID.

### FR-R1 (Project)
Collezione: `projects`
```
{
  _id: ObjectId,
  name: string (max 200, required, unique index),
  description: string | null,
  created_at: datetime
}
```

### FR-R2 (Epic)
Collezione: `epics`
```
{
  _id: ObjectId,
  project_id: ObjectId (required, index),
  name: string (max 255, required),
  description: string | null,
  external_ref: string | null,
  created_at: datetime
}
```
- Indice: `project_id`.

### FR-R3 (Feature)
Collezione: `features`
```
{
  _id: ObjectId,
  epic_id: ObjectId (required, index),
  name: string (max 255, required),
  description: string | null,
  created_at: datetime
}
```
- Indice: `epic_id`.

### FR-R4 (TestCaseDefinition)
Collezione: `test_case_definitions`
```
{
  _id: ObjectId,
  feature_id: ObjectId (required, index),
  title: string (max 255, required),
  description: string | null,
  preconditions: string | null,
  steps: [ { description: string, order: int } ],
  expected_result: string | null,
  priority: string (enum: critical|high|medium|low, default "medium"),
  is_active: boolean (default true),
  created_at: datetime,
  updated_at: datetime
}
```
- Indice: `feature_id`.
- Il campo `steps` resta un array di oggetti embedded (naturale in MongoDB).

### FR-R5 (TestRun)
Collezione: `test_runs`
```
{
  _id: ObjectId,
  name: string (max 255, required, index),
  status: string (enum: running|completed|aborted, default "running"),
  start_time: datetime,
  end_time: datetime | null,
  project_id: ObjectId | null (index)
}
```
- Indice: `name`, `project_id`.

### FR-R6 (TestCase)
Collezione: `test_cases`
```
{
  _id: ObjectId,
  run_id: ObjectId (required, index),
  name: string (max 255, index),
  status: string (enum: passed|failed|skipped),
  duration: int | null (ms),
  error_message: string | null,
  error_stack: string | null,
  screenshot_path: string | null,
  created_at: datetime,
  definition_id: ObjectId | null (index),
  steps: [
    {
      description: string,
      status: string (enum: passed|failed|skipped),
      order_index: int
    }
  ]
}
```
- **Test steps sono embedded** nel documento TestCase (sempre caricati insieme, numero limitato per caso).
- Indici: `run_id`, `name`, `definition_id`.
- Il modello `TestStep` come Document separato viene eliminato; gli step diventano un sotto-modello Pydantic (`BaseModel`) embedded nell'array `steps`.

### FR-R7 (Proprieta' calcolate)
I modelli Document devono esporre le stesse proprieta' calcolate esistenti:
- `TestRun`: `duration`, `test_count`, `passed_count`, `failed_count`, `skipped_count`.
- `Project`: `epic_count`, `test_definition_count`, `active_test_definition_count`.
- `Epic`: `feature_count`, `test_definition_count`, `active_test_definition_count`.
- `Feature`: `test_definition_count`, `active_test_definition_count`.
- `TestCaseDefinition`: `execution_count`.
- `TestCase`: `has_screenshot`, `step_count`.

Nota: a differenza di SQLModel (dove le proprieta' navigano le relazioni ORM in memoria), in MongoDB queste proprieta' devono eseguire query aggregate o count. Per le proprieta' frequentemente usate nelle liste (es. `epic_count` su Project), valutare l'uso di **metodi async** anziche' property, oppure pre-calcolare i conteggi con pipeline di aggregazione nei service.

### FR-R8 (Enums)
Le enum `RunStatus`, `TestStatus`, `Priority` restano invariate in `app/models/__init__.py`. Non dipendono da SQLModel.

---

## Modulo S: Layer Database

### FR-S1 (Connessione e inizializzazione)
Sostituire `app/database/engine.py` con:
- Creare un client Motor async: `AsyncIOMotorClient(settings.MONGODB_URI)`.
- Inizializzare Beanie con `init_beanie(database, document_models=[...])` al startup.
- Beanie crea automaticamente le collezioni e gli indici dichiarati nei modelli.

### FR-S2 (Session / Dependency Injection)
Sostituire `app/database/session.py`:
- La dependency FastAPI `get_session()` (che fornisce una `sqlmodel.Session`) non e' piu' necessaria.
- Beanie opera direttamente sui Document (es. `await Project.find_all().to_list()`), senza bisogno di una sessione esplicita.
- Rimuovere `Depends(get_session)` da tutti gli endpoint e service.
- Se necessario per le transazioni, usare `async with await client.start_session() as session`.

### FR-S3 (Migrazione startup)
Sostituire `run_migrations()`:
- La funzione non e' piu' necessaria (le migrazioni SQLite non si applicano a MongoDB).
- Al primo avvio, Beanie crea automaticamente le collezioni e gli indici.
- Rimuovere la chiamata a `run_migrations()` dal startup dell'app.

### FR-S4 (Modulo database __init__)
Aggiornare `app/database/__init__.py` per esportare la funzione di init Beanie invece di `create_db_and_tables` e `run_migrations`.

---

## Modulo T: Service Layer

Tutti i service devono essere convertiti da operazioni sincrone con `sqlmodel.Session` a operazioni **async** con Beanie.

### FR-T1 (Pattern generale)
Ogni funzione di servizio:
- Diventa `async def` (era `def`).
- Rimuove il parametro `session: Session`.
- Usa i metodi Beanie sul Document:
  - `await Document.get(id)` al posto di `session.get(Model, id)`.
  - `await Document.find(query).to_list()` al posto di `session.exec(select(...))`.
  - `await document.insert()` al posto di `session.add(); session.commit(); session.refresh()`.
  - `await document.save()` al posto di `session.add(); session.commit()`.
  - `await document.delete()` al posto di `session.delete(); session.commit()`.

### FR-T2 (Servizi da convertire)
I seguenti service devono essere convertiti:
- `project_service.py`
- `epic_service.py`
- `feature_service.py`
- `definition_service.py`
- `run_service.py`
- `case_service.py`
- `screenshot_service.py`
- `stats_service.py`

### FR-T3 (Query cross-collection)
Le query che attualmente usano JOIN SQL devono usare query sequenziali o aggregation pipeline:
- `definition_service.list_definitions_by_project(project_id, epic_id, feature_id, priority)`:
  - Risalire: Project -> Epics (by project_id) -> Features (by epic_ids) -> Definitions (by feature_ids).
  - Applicare filtri opzionali.
- `stats_service.calculate_run_statistics(run_id)`:
  - Usare aggregation pipeline su `test_cases` filtrate per `run_id` con `$group` per contare i vari stati.

### FR-T4 (Conversione ID)
Tutti gli ID passano da `int` (autoincrement SQLite) a `PydanticObjectId` (ObjectId MongoDB):
- I parametri dei service e degli endpoint che accettano ID diventano `PydanticObjectId`.
- Le risposte API serializzano `ObjectId` come stringa.
- Le exception custom (`RunNotFoundError`, `CaseNotFoundError`, ecc.) devono accettare `PydanticObjectId` o `str` invece di `int`.

---

## Modulo U: API Layer

### FR-U1 (Endpoint signatures)
Tutti gli endpoint API e web:
- Diventano `async def` (molti lo sono gia', ma le chiamate ai service devono usare `await`).
- Rimuovono `session: Session = Depends(get_session)`.
- I path parameter con ID diventano `str` (MongoDB ObjectId serializzato).

### FR-U2 (Schemi risposta)
Gli schemi in `app/schemas/`:
- I campi `id`, `project_id`, `epic_id`, `feature_id`, `run_id`, `definition_id`, `case_id` diventano `str` (serializzazione di ObjectId).
- Aggiungere validatore Pydantic per accettare sia `str` che `PydanticObjectId`.

### FR-U3 (Startup)
In `app/main.py`:
- Sostituire l'evento startup:
  - Rimuovere `create_db_and_tables()` e `run_migrations()`.
  - Aggiungere `init_beanie(database, document_models=[Project, Epic, Feature, TestCaseDefinition, TestRun, TestCase])`.
- Usare il lifespan handler FastAPI (raccomandato) al posto di `@app.on_event("startup")`.

---

## Modulo V: Script di migrazione dati

### FR-V1 (Script one-shot)
Creare `scripts/migrate_sqlite_to_mongo.py`:
- Legge tutti i record dal database SQLite esistente.
- Li inserisce nella corrispondente collezione MongoDB.
- Mappa gli ID integer SQLite -> ObjectId MongoDB, mantenendo una tabella di mapping in memoria per risolvere le foreign key.
- Ordine di migrazione: Project -> Epic -> Feature -> TestCaseDefinition -> TestRun -> TestCase (con steps embedded).
- Lo script deve essere idempotente: se eseguito piu' volte, non duplica i dati (usa upsert o controlla l'esistenza).

### FR-V2 (Esecuzione)
Lo script deve:
- Accettare parametri CLI per `--sqlite-path` e `--mongodb-uri`.
- Stampare un riepilogo: numero di record migrati per collezione.
- Gestire errori senza interrompere l'intera migrazione (log errore e continua).

---

## Requisiti Non Funzionali

### NFR-14 (Retrocompatibilita' API)
Le API REST devono mantenere gli stessi path e la stessa struttura di risposta JSON. L'unica differenza visibile e' il formato degli ID (da integer a stringa ObjectId di 24 caratteri hex).

### NFR-15 (Zero downtime)
La migrazione dei dati (Modulo V) puo' essere eseguita offline. Non e' richiesta migrazione a caldo.

### NFR-16 (Persistenza dati)
Il volume Docker `mongo-data` deve garantire la persistenza dei dati tra restart del container.

### NFR-17 (Performance)
Gli indici MongoDB devono garantire performance comparabili o superiori a SQLite per le query principali:
- Lista runs (ordinati per start_time desc).
- Test cases per run_id.
- Definitions per feature_id.
- Epics per project_id.
- Features per epic_id.

---

## Riepilogo File

| Azione | File |
|--------|------|
| Modificare | `docker-compose.yml` |
| Modificare | `Dockerfile` |
| Modificare | `requirements.txt` |
| Modificare | `app/config.py` |
| Riscrivere | `app/database/engine.py` |
| Riscrivere | `app/database/session.py` |
| Modificare | `app/database/__init__.py` |
| Riscrivere | `app/models/project.py` |
| Riscrivere | `app/models/epic.py` |
| Riscrivere | `app/models/feature.py` |
| Riscrivere | `app/models/test_case_definition.py` |
| Riscrivere | `app/models/test_run.py` |
| Riscrivere | `app/models/test_case.py` |
| Eliminare | `app/models/test_step.py` |
| Modificare | `app/models/__init__.py` |
| Riscrivere | `app/services/project_service.py` |
| Riscrivere | `app/services/epic_service.py` |
| Riscrivere | `app/services/feature_service.py` |
| Riscrivere | `app/services/definition_service.py` |
| Riscrivere | `app/services/run_service.py` |
| Riscrivere | `app/services/case_service.py` |
| Riscrivere | `app/services/screenshot_service.py` |
| Riscrivere | `app/services/stats_service.py` |
| Modificare | `app/services/exceptions.py` |
| Modificare | `app/schemas/project_schemas.py` |
| Modificare | `app/schemas/epic_schemas.py` |
| Modificare | `app/schemas/feature_schemas.py` |
| Modificare | `app/schemas/definition_schemas.py` |
| Modificare | `app/schemas/case_schemas.py` |
| Modificare | `app/schemas/run_schemas.py` |
| Modificare | `app/api/runs.py` |
| Modificare | `app/api/projects.py` |
| Modificare | `app/api/features.py` |
| Modificare | `app/web/project_routes.py` |
| Modificare | `app/web/routes.py` |
| Modificare | `app/web/htmx_routes.py` |
| Modificare | `app/main.py` |
| Creare | `scripts/migrate_sqlite_to_mongo.py` |

**Totale: 1 file da creare, 1 file da eliminare, ~35 file da modificare/riscrivere**
