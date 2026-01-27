# Feature 01: Progetti, Catalogo Test Case e API Agente

## 1. Contesto

La baseline (00-baseline) gestisce esclusivamente il **ciclo di esecuzione** dei test: una Run viene aperta, i risultati vengono inviati dall'agente, la Run viene chiusa. Non esiste il concetto di "test case predefinito" né di organizzazione per progetto.

Questa feature introduce:
- Un **catalogo di Test Case** definibili a priori dall'utente tramite interfaccia web.
- Un'**organizzazione gerarchica** tramite Progetti e Issue/Epic.
- Un **endpoint API** che permette a un Agente AI di interrogare i test case da eseguire.

---

## 2. Modello Dati

### Nuove Entità

1. **Project:** Rappresenta un progetto software o un'area funzionale.
   - `id` (PK)
   - `name` (str, univoco, max 255)
   - `description` (str, opzionale, max 1000)
   - `created_at` (datetime)

2. **Epic:** Rappresenta una epic, issue o raggruppamento funzionale all'interno di un progetto.
   - `id` (PK)
   - `project_id` (FK → Project)
   - `name` (str, max 255)
   - `description` (str, opzionale, max 1000)
   - `external_ref` (str, opzionale, max 255) — riferimento esterno (es. ID Jira, numero issue GitHub)
   - `created_at` (datetime)

3. **TestCaseDefinition:** Rappresenta la *specifica* di un test case, definita prima dell'esecuzione.
   - `id` (PK)
   - `epic_id` (FK → Epic)
   - `title` (str, max 255)
   - `description` (str, opzionale, max 2000) — descrizione in linguaggio naturale di cosa verificare
   - `preconditions` (str, opzionale, max 2000) — condizioni iniziali necessarie
   - `steps` (JSON) — lista ordinata di step previsti, ciascuno con `description` (str)
   - `expected_result` (str, opzionale, max 2000) — risultato atteso al termine del test
   - `priority` (str: `critical`, `high`, `medium`, `low`, default `medium`)
   - `is_active` (bool, default True) — permette di disattivare un test senza eliminarlo
   - `created_at` (datetime)
   - `updated_at` (datetime)

### Modifiche alle Entità Esistenti

4. **TestRun** (modifica): Aggiunta campo opzionale.
   - `project_id` (FK → Project, opzionale) — collega una Run a un progetto specifico

5. **TestCase** (modifica): Aggiunta campo opzionale.
   - `definition_id` (FK → TestCaseDefinition, opzionale) — collega il risultato di esecuzione alla definizione originale

### Relazioni

```
Project 1──N Epic 1──N TestCaseDefinition
Project 1──N TestRun (opzionale)
TestCaseDefinition 1──N TestCase (risultati di esecuzione, opzionale)
```

> **Nota:** I campi `project_id` su TestRun e `definition_id` su TestCase sono **opzionali** per mantenere la retrocompatibilità con il flusso baseline, dove l'agente può continuare a inviare risultati senza riferimenti a progetto o definizione.

---

## 3. Requisiti Funzionali

### Modulo E: Gestione Progetti (Project Management)

* **FR-E1 (CRUD Progetto):** Il sistema deve permettere la creazione, visualizzazione, modifica e cancellazione di Progetti tramite interfaccia web.
* **FR-E2 (Dashboard Progetti):** La pagina principale deve essere estesa con una sezione o una vista dedicata ai Progetti, mostrando per ciascuno il numero di Epic e di Test Case definiti.
* **FR-E3 (Vincolo di cancellazione):** Non deve essere possibile eliminare un Progetto che ha Epic o TestRun associati. Il sistema deve mostrare un messaggio di errore chiaro.

### Modulo F: Gestione Epic/Issue (Epic Management)

* **FR-F1 (CRUD Epic):** Il sistema deve permettere la creazione, visualizzazione, modifica e cancellazione di Epic all'interno di un Progetto.
* **FR-F2 (Riferimento esterno):** Ogni Epic può avere un riferimento esterno opzionale (es. link o ID di un issue tracker) per tracciabilità.
* **FR-F3 (Vincolo di cancellazione):** Non deve essere possibile eliminare un'Epic che ha TestCaseDefinition associati. Il sistema deve mostrare un messaggio di errore chiaro.

### Modulo G: Catalogo Test Case (Test Case Definitions)

* **FR-G1 (Creazione da form):** L'utente deve poter creare un Test Case Definition tramite un form web con i seguenti campi: titolo, descrizione, precondizioni, step previsti (lista ordinata, aggiungibili/rimuovibili dinamicamente), risultato atteso, priorità.
* **FR-G2 (Modifica e disattivazione):** L'utente deve poter modificare un Test Case Definition esistente e attivarlo/disattivarlo (soft delete).
* **FR-G3 (Vista catalogo):** All'interno di un'Epic, il sistema deve mostrare la lista dei Test Case Definition con indicatori visivi di priorità e stato (attivo/inattivo).
* **FR-G4 (Dettaglio definizione):** Cliccando su un Test Case Definition, l'utente deve visualizzare tutti i dettagli e lo storico delle esecuzioni collegate (TestCase con `definition_id` corrispondente).
* **FR-G5 (Collegamento ai risultati):** Se un TestCase (risultato di esecuzione) è collegato a una TestCaseDefinition, nella vista di dettaglio della Run deve apparire un link alla definizione originale, e viceversa.

### Modulo H: API per Agente AI (Agent API)

* **FR-H1 (Lista test case per progetto):** `GET /api/projects/{project_id}/test-cases` — Restituisce la lista di tutti i TestCaseDefinition attivi del progetto, attraversando le Epic. L'agente usa questo endpoint per sapere *cosa* deve testare.
* **FR-H2 (Filtri):** L'endpoint deve supportare filtri opzionali:
  - `epic_id` — filtrare per specifica Epic
  - `priority` — filtrare per priorità (es. `?priority=critical,high`)
* **FR-H3 (Dettaglio singolo test):** `GET /api/test-cases/{definition_id}` — Restituisce il dettaglio completo di un singolo TestCaseDefinition (step inclusi).
* **FR-H4 (Collegamento in fase di report):** L'endpoint esistente `POST /api/runs/{run_id}/report` deve accettare un campo opzionale `definition_id` nel payload JSON, per collegare il risultato alla definizione.
* **FR-H5 (Avvio Run con progetto):** L'endpoint esistente `POST /api/runs/start` deve accettare un campo opzionale `project_id` nel payload JSON, per associare la Run a un progetto.

---

## 4. Requisiti di Interfaccia (UI)

* **FR-UI1 (Navigazione):** Aggiungere una voce "Progetti" alla navigazione principale. La struttura di navigazione diventa: Dashboard (Run) | Progetti.
* **FR-UI2 (Pagina Progetto):** Vista dedicata al singolo progetto con: nome, descrizione, elenco delle Epic, statistiche aggregate (totale test definiti, attivi, ultima esecuzione).
* **FR-UI3 (Pagina Epic):** Vista dedicata all'Epic con: dettagli, lista dei TestCaseDefinition, form di creazione inline o modale.
* **FR-UI4 (Form Test Case):** Il form di creazione/modifica dei Test Case Definition deve:
  - Permettere l'aggiunta dinamica di step (add/remove) senza ricaricare la pagina.
  - Validare i campi obbligatori lato client.
  - Utilizzare lo stesso pattern HTMX della baseline per le interazioni.
* **FR-UI5 (Indicatori visivi di priorità):** Utilizzare codici colore per la priorità:
  - `critical` → Rosso
  - `high` → Arancione
  - `medium` → Blu
  - `low` → Grigio

---

## 5. Requisiti Non Funzionali

* **NFR-05 (Retrocompatibilità):** Tutti gli endpoint e le funzionalità della baseline devono continuare a funzionare invariati. I nuovi campi aggiunti alle entità esistenti (TestRun, TestCase) devono essere opzionali.
* **NFR-06 (Consistenza UI):** Le nuove pagine devono adottare lo stesso stile visivo (TailwindCSS, HTMX, codici colore) della baseline.
* **NFR-07 (Migrazione DB):** Lo schema del database deve aggiornarsi automaticamente all'avvio, senza perdita dei dati esistenti.

---

## 6. Endpoints API (Riepilogo)

| Metodo | Endpoint | Descrizione |
|--------|----------|-------------|
| `POST` | `/api/projects` | Crea un nuovo Progetto |
| `GET` | `/api/projects` | Lista tutti i Progetti |
| `GET` | `/api/projects/{id}` | Dettaglio Progetto |
| `PUT` | `/api/projects/{id}` | Modifica Progetto |
| `DELETE` | `/api/projects/{id}` | Elimina Progetto (con vincolo) |
| `POST` | `/api/projects/{project_id}/epics` | Crea una nuova Epic |
| `GET` | `/api/projects/{project_id}/epics` | Lista Epic del Progetto |
| `GET` | `/api/epics/{id}` | Dettaglio Epic |
| `PUT` | `/api/epics/{id}` | Modifica Epic |
| `DELETE` | `/api/epics/{id}` | Elimina Epic (con vincolo) |
| `POST` | `/api/epics/{epic_id}/test-cases` | Crea un TestCaseDefinition |
| `GET` | `/api/projects/{project_id}/test-cases` | Lista test case del progetto (per Agente) |
| `GET` | `/api/test-cases/{id}` | Dettaglio TestCaseDefinition |
| `PUT` | `/api/test-cases/{id}` | Modifica TestCaseDefinition |
| `DELETE` | `/api/test-cases/{id}` | Disattiva TestCaseDefinition (soft delete) |

### Modifiche agli endpoint esistenti

| Metodo | Endpoint | Modifica |
|--------|----------|----------|
| `POST` | `/api/runs/start` | Accetta campo opzionale `project_id` |
| `POST` | `/api/runs/{run_id}/report` | Accetta campo opzionale `definition_id` |
