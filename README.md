# RedstoneReporter

🔴 **AI Agent Test Reporter** - Una alternativa personalizzata a Monocart Reporter per raccogliere, storicizzare e visualizzare i risultati dei test End-to-End eseguiti da agenti AI autonomi.

## Caratteristiche Principali

- ✅ **API REST completa** per l'invio dei risultati di test da agenti AI
- 📊 **Dashboard Web moderna** con aggiornamenti real-time (HTMX)
- 🔄 **Sistema di Checkpoint** per il recupero dopo crash dell'agente
- 📸 **Gestione Screenshot** con upload multipart e visualizzazione integrata
- 🎯 **Reporting Granulare** - ogni test case viene salvato immediatamente
- 🗄️ **Database SQLite** auto-creato per portabilità e semplicità
- 🎨 **UI Responsive** con TailwindCSS e indicatori visivi intuitivi

## Stack Tecnologico

- **Backend:** Python 3.10+, FastAPI, SQLModel, SQLite
- **Frontend:** Jinja2 (SSR), TailwindCSS, HTMX
- **Storage:** Filesystem per screenshot, SQLite per metadati

## Installazione Rapida

### Prerequisiti

- Python 3.10 o superiore
- pip

### Setup

```bash
# 1. Clone del repository (se necessario)
cd RedstoneReporter

# 2. Crea virtual environment
python -m venv venv

# 3. Attiva virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 4. Installa dipendenze
pip install -r requirements.txt

# 5. (Opzionale) Configura environment variables
cp .env.example .env
# Modifica .env se necessario

# 6. Avvia il server
python run.py
```

Il server sarà disponibile su: **http://localhost:8000**

- Dashboard: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## Utilizzo

### Per l'AI Agent (Client)

L'agente AI utilizza le API REST per comunicare con RedstoneReporter:

#### 1. Inizia una nuova Test Run

```bash
curl -X POST http://localhost:8000/api/runs/start \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Suite 1"}'
```

Risposta:
```json
{
  "id": 1,
  "name": "Test Suite 1",
  "status": "running",
  "start_time": "2024-01-26T10:00:00",
  ...
}
```

#### 2. Reporta un Test Case (con screenshot opzionale)

```bash
curl -X POST http://localhost:8000/api/runs/1/report \
  -F 'data={
    "name": "Login Test",
    "status": "passed",
    "duration": 1500,
    "steps": [
      {"description": "Open page", "status": "passed"},
      {"description": "Click login", "status": "passed"}
    ]
  }' \
  -F 'screenshot=@screenshot.png'
```

#### 3. Query Checkpoint (per crash recovery)

```bash
curl http://localhost:8000/api/runs/1/checkpoint
```

Risposta:
```json
{
  "run_id": 1,
  "completed_test_names": ["Login Test", "Payment Test"],
  "total_completed": 2
}
```

L'agente può usare questa lista per saltare i test già completati dopo un restart.

#### 4. Chiudi la Test Run

```bash
curl -X POST http://localhost:8000/api/runs/1/finish
```

### Per l'Utente Umano (Viewer)

1. Apri il browser su **http://localhost:8000**
2. Visualizza la **Dashboard** con tutte le test run
3. Clicca su una run per vedere i **dettagli dei test case**
4. Espandi un test case per vedere:
   - Sequenza degli step eseguiti
   - Messaggi di errore e stack trace
   - Screenshot associati
5. Usa il filtro **"Failed Only"** per vedere solo i test falliti

## Struttura del Progetto

```
RedstoneReporter/
├── app/
│   ├── api/              # REST API endpoints
│   ├── database/         # Database configuration
│   ├── models/           # SQLModel entities
│   ├── schemas/          # Pydantic request/response
│   ├── services/         # Business logic
│   ├── templates/        # Jinja2 templates
│   ├── web/              # Web UI routes
│   ├── config.py         # Configuration
│   └── main.py           # FastAPI app
├── data/
│   ├── redstone.db       # SQLite database (auto-created)
│   └── screenshots/      # Screenshot storage
├── static/               # Static files (CSS/JS)
├── tests/                # Test suite
├── requirements.txt      # Python dependencies
├── run.py                # Entry point
└── README.md
```

## API Endpoints

### Gestione Test Runs

| Endpoint | Method | Descrizione |
|----------|--------|-------------|
| `/api/runs/start` | POST | Crea una nuova test run |
| `/api/runs/{id}` | GET | Ottieni info su una run |
| `/api/runs/{id}/report` | POST | Reporta un test case (multipart) |
| `/api/runs/{id}/checkpoint` | GET | Query checkpoint per recovery |
| `/api/runs/{id}/finish` | POST | Chiudi la run |

### Web UI

| Endpoint | Descrizione |
|----------|-------------|
| `/` | Dashboard principale |
| `/runs/{id}` | Dettaglio run con filtri |
| `/api/htmx/runs` | Partial per auto-refresh |
| `/api/htmx/cases/{id}/details` | Partial per espansione case |

Documentazione completa disponibile su: **http://localhost:8000/docs** (Swagger UI)

## Configurazione

Le impostazioni possono essere configurate tramite:

1. **File `.env`** (copia da `.env.example`)
2. **Environment variables**

Variabili disponibili:

```bash
DATABASE_URL=sqlite:///./data/redstone.db  # Path database
SCREENSHOT_DIR=./data/screenshots          # Directory screenshot
HOST=127.0.0.1                            # Server host
PORT=8000                                 # Server port
MAX_UPLOAD_SIZE=10485760                  # Limite upload (10MB)
AUTO_REFRESH_INTERVAL=5                   # Intervallo refresh (secondi)
```

## Deployment Production

### Con Uvicorn (Multiple Workers)

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Con Docker Compose (Raccomandato)

Il modo più semplice per testare in locale con Docker:

```bash
# Build e avvio in una sola volta
docker-compose up --build

# Oppure in background
docker-compose up -d --build

# Visualizza i logs
docker-compose logs -f

# Stop
docker-compose down
```

L'applicazione sarà disponibile su **http://localhost:8000**

I dati (database e screenshot) sono persistiti nella directory locale `./data/` grazie ai volumi Docker.

### Con Docker Manualmente

```bash
# Build dell'immagine
docker build -t redstone-reporter .

# Run del container
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  --name redstone-reporter \
  redstone-reporter

# Visualizza logs
docker logs -f redstone-reporter

# Stop e rimozione
docker stop redstone-reporter
docker rm redstone-reporter
```

**Note Docker:**
- Il database SQLite e gli screenshot sono salvati in `./data/` (volume montato)
- La porta 8000 è esposta sull'host
- Health check configurato per monitoraggio automatico
- Auto-restart configurato (con docker-compose)

## Caratteristiche Tecniche

### Database

- **SQLite con WAL mode** per migliori performance
- **Auto-creazione schema** al primo avvio
- **Tre tabelle principali:**
  - `test_runs` - Sessioni di test
  - `test_cases` - Singoli test case
  - `test_steps` - Step all'interno dei test

### Screenshot Storage

- **Salvati su filesystem** (non in database) per performance
- **Struttura organizzata:** `data/screenshots/{run_id}/{case_name}_{timestamp}.png`
- **Serviti staticamente** via FastAPI StaticFiles
- **Upload asincrono** (non blocca il thread principale)

### Real-time Updates

- **HTMX polling** ogni 5 secondi sulla dashboard
- **Aggiornamenti dinamici** senza ricaricamento pagina
- **Espansione lazy** dei dettagli test case

## Risoluzione Problemi

### Il database non viene creato

Il database viene auto-creato al primo avvio. Verifica:
- Che la directory `data/` sia scrivibile
- I log di avvio per eventuali errori

### Gli screenshot non vengono visualizzati

Verifica:
- Che la directory `data/screenshots/` esista
- Che i permessi di scrittura siano corretti
- Nel browser, controlla la console per errori 404

### Errore "Address already in use"

La porta 8000 è già in uso. Opzioni:
1. Cambia porta in `.env`: `PORT=8001`
2. Termina il processo che usa la porta 8000

## Sviluppo

### Eseguire i test

```bash
pytest -v tests/
```

### Modalità development con auto-reload

```bash
python run.py  # Auto-reload abilitato di default
```

### Struttura logging

```python
import logging
logger = logging.getLogger(__name__)
logger.info("Test run created")
```

## Contributi

Il progetto segue le specifiche definite in `CLAUDE.md`.

## Licenza

Progetto interno per test automation con AI agents.

## Contatti

Per supporto o domande, consulta la documentazione API su http://localhost:8000/docs

---

**Built with ❤️ for AI Agents**
