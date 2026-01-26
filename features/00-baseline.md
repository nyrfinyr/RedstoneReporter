# Progetto: AI Agent Test Reporter (Custom Monocart Alternative)

## 1. Scopo del Progetto

Realizzare un server backend in Python con interfaccia web integrata per raccogliere, storicizzare e visualizzare i risultati dei test End-to-End eseguiti da un Agente AI autonomo. Il sistema funge da alternativa personalizzata a "Monocart Reporter", supportando l'esecuzione non lineare dei test e la persistenza dei dati per il recupero in caso di crash.

## 2. Attori del Sistema

1. **AI Agent (Client):** Il sistema che esegue i test sul browser e invia i risultati tramite API.
2. **Utente Umano (Admin/Viewer):** La persona che consulta la Dashboard per analizzare l'esito dei test e debuggare gli errori.

## 3. Requisiti Funzionali (FR)

### Modulo A: Gestione Sessioni di Test (Run Management)

* **FR-A1 (Inizio Suite):** Il sistema deve esporre un endpoint API per creare una nuova "Test Run" (sessione di test). Deve accettare un nome/titolo per la suite e restituire un `run_id` univoco.
* **FR-A2 (Stato Run):** Ogni Test Run deve avere uno stato monitorabile (`running`, `completed`, `aborted`) e un timestamp di inizio/fine.
* **FR-A3 (Chiusura Suite):** Il sistema deve esporre un endpoint per marcare una Test Run come `completed`, permettendo il calcolo delle statistiche finali (durata totale, % successo).

### Modulo B: Ingestione Dati e Reporting (Data Ingestion)

* **FR-B1 (Reporting Granulare):** Il sistema deve accettare il risultato di un *singolo* Test Case immediatamente dopo la sua esecuzione (non alla fine di tutta la suite).
* **FR-B2 (Protocollo Multipart):** L'endpoint di reporting deve accettare richieste `multipart/form-data` per gestire simultaneamente:
1. Metadati JSON (nome test, esito, durata, steps, log errori).
2. File binario (Screenshot) opzionale.


* **FR-B3 (Struttura Test Case):** Il payload JSON deve supportare una lista ordinata di "Steps" (es. "Click Login", "Wait for element") con il relativo esito per ciascuno passo.
* **FR-B4 (Gestione Errori):** In caso di `status: failed`, il sistema deve registrare il messaggio di errore e lo stack trace fornito dall'agente.
* **FR-B5 (Storage Immagini):** Gli screenshot ricevuti non devono essere salvati nel database, ma su **Filesystem** locale in una directory dedicata. Nel database deve essere salvato solo il percorso relativo (path).

### Modulo C: Resilienza e Checkpointing (Recovery)

* **FR-C1 (Query Checkpoint):** Il sistema deve esporre un endpoint API (`GET /api/runs/{id}/checkpoint`) che restituisca la lista degli identificativi (nomi) dei Test Case già completati per quella specifica Run.
* **FR-C2 (Logica di Ripresa):** Questo endpoint deve permettere all'Agente, in caso di riavvio dopo un crash, di sapere esattamente quali test saltare perché già eseguiti e persistiti.

### Modulo D: Visualizzazione e Dashboard (UI)

* **FR-D1 (Dashboard Principale):** La Home Page deve mostrare l'elenco cronologico delle Test Runs, con indicatori visivi immediati (Verde/Rosso) e metriche di riepilogo (Totale test, Passati, Falliti).
* **FR-D2 (Dettaglio Run):** Cliccando su una Run, l'utente deve vedere la lista di tutti i Test Case associati.
* **FR-D3 (Ispezione Dettagliata):** L'interfaccia deve permettere di espandere un singolo Test Case per visualizzare:
* La sequenza degli Step eseguiti.
* I dettagli dell'errore (se presente).
* Lo screenshot associato (visualizzato direttamente nel browser).


* **FR-D4 (Aggiornamento Dinamico):** L'interfaccia deve supportare l'aggiornamento dei dati senza ricaricamento completo della pagina (pattern HTMX) o fornire un meccanismo di refresh rapido.
* **FR-D5 (Filtri):** Possibilità di filtrare la vista per mostrare solo i test "Failed".

---

## 4. Requisiti Non Funzionali (NFR)

* **NFR-01 (Stack Tecnologico):**
* **Linguaggio:** Python 3.10+
* **Framework Web:** FastAPI
* **Database:** SQLite (file singolo per portabilità)
* **ORM:** SQLModel (Pydantic + SQLAlchemy)
* **Frontend Rendering:** Jinja2 (Server Side Rendering)
* **Frontend Styling:** TailwindCSS (via CDN o statico)
* **Interattività:** HTMX (per interazioni dinamiche senza JS framework pesanti)


* **NFR-02 (UI/UX):** L'interfaccia deve essere "accattivante", moderna e responsive. Deve utilizzare codici colore standard (Verde=Successo, Rosso=Errore, Giallo=Warning).
* **NFR-03 (Performance):** L'upload degli screenshot non deve bloccare il thread principale del server (uso di `async/await`).
* **NFR-04 (Semplicità di Deployment):** Il sistema deve poter essere avviato con un singolo comando (es. `python main.py` o tramite Docker) e il database deve auto-generarsi se assente.

---

## 5. Modello Dati Preliminare (Entità)

1. **TestRun:** `id`, `name`, `start_time`, `end_time`, `status`.
2. **TestCase:** `id`, `run_id` (FK), `name`, `status`, `duration`, `error_message`, `screenshot_path`.
3. **TestStep:** `id`, `case_id` (FK), `description`, `status`, `order_index`.

---

## 6. Definizione delle API (Endpoints Chiave)

* `POST /api/runs/start` -> Crea Run ID.
* `GET /api/runs/{run_id}/checkpoint` -> Restituisce lista test completati.
* `POST /api/runs/{run_id}/report` -> Multipart (JSON + File). Salva Case e Step.
* `POST /api/runs/{run_id}/finish` -> Chiude la Run.
* `GET /` -> Dashboard HTML.