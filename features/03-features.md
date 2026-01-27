# Feature 03: Introduzione delle Feature e Operazioni di Eliminazione

## 1. Contesto

La feature 01 ha introdotto la gerarchia **Project → Epic → TestCaseDefinition**. In questa struttura, i Test Case Definition sono collegati direttamente alle Epic. Tuttavia, in molti contesti reali una Epic raccoglie più funzionalità (Feature) distinte, e i test case sono scritti per verificare una specifica Feature, non l'intera Epic.

Questa feature introduce:
- Un nuovo livello gerarchico **Feature** tra Epic e TestCaseDefinition.
- La possibilità di **eliminare** Test Case (risultati di esecuzione) e Feature.

---

## 2. Modello Dati

### Nuova Entità

1. **Feature:** Rappresenta una funzionalità specifica all'interno di un'Epic.
   - `id` (PK)
   - `epic_id` (FK → Epic, obbligatorio)
   - `name` (str, max 255)
   - `description` (str, opzionale, max 1000)
   - `created_at` (datetime)

### Modifiche alle Entità Esistenti

2. **TestCaseDefinition** (modifica):
   - Rimuovere il campo `epic_id` (FK → Epic)
   - Aggiungere il campo `feature_id` (FK → Feature, obbligatorio)
   - La relazione diventa: Feature 1──N TestCaseDefinition

3. **Epic** (modifica):
   - Aggiungere relazione verso Feature: Epic 1──N Feature
   - Rimuovere relazione diretta verso TestCaseDefinition

### Nuova Gerarchia

```
Project 1──N Epic 1──N Feature 1──N TestCaseDefinition
```

> **Nota:** La retrocompatibilità degli endpoint API esistenti deve essere mantenuta dove possibile. Gli endpoint che usavano `epic_id` per i TestCaseDefinition devono essere aggiornati per usare `feature_id`.

---

## 3. Requisiti Funzionali

### Modulo N: Gestione Feature

* **FR-N1 (CRUD Feature):** Il sistema deve permettere la creazione, visualizzazione, modifica e cancellazione di Feature all'interno di un'Epic, tramite API e interfaccia web.

* **FR-N2 (Vincolo Epic obbligatoria):** Ogni Feature deve appartenere a un'Epic. Il campo `epic_id` è obbligatorio e non può essere null.

* **FR-N3 (Vincolo di cancellazione Feature):** È possibile eliminare una Feature solo se non ha TestCaseDefinition associati. Il sistema deve mostrare un messaggio di errore chiaro in caso contrario.

* **FR-N4 (Migrazione TestCaseDefinition):** I TestCaseDefinition attualmente collegati a un'Epic devono essere migrati per puntare a una Feature. La migrazione deve:
  - Per ogni Epic con TestCaseDefinition, creare automaticamente una Feature con lo stesso nome dell'Epic.
  - Aggiornare tutti i TestCaseDefinition per puntare alla nuova Feature.

### Modulo O: Eliminazione Test Case ed Entità

* **FR-O1 (Eliminazione Test Case):** Deve essere possibile eliminare un singolo Test Case (risultato di esecuzione) tramite API. L'eliminazione è permanente (hard delete) e rimuove anche gli step e lo screenshot associati.

* **FR-O2 (Eliminazione Feature):** Deve essere possibile eliminare una Feature tramite API, con il vincolo descritto in FR-N3.

* **FR-O3 (Endpoint API eliminazione Test Case):** `DELETE /api/cases/{case_id}` — Elimina permanentemente un Test Case con tutti i dati associati (steps, screenshot). Restituisce 204 No Content in caso di successo, 404 se non trovato.

* **FR-O4 (Endpoint API eliminazione Feature):** `DELETE /api/features/{feature_id}` — Elimina una Feature. Restituisce 204 No Content in caso di successo, 404 se non trovata, 409 Conflict se ha TestCaseDefinition associati.

### Modulo P: Aggiornamento API e UI

* **FR-P1 (Endpoint Feature per Epic):** `POST /api/epics/{epic_id}/features` — Crea una nuova Feature nell'Epic. `GET /api/epics/{epic_id}/features` — Lista le Feature dell'Epic.

* **FR-P2 (Endpoint Feature CRUD):** `GET /api/features/{feature_id}` — Dettaglio Feature. `PUT /api/features/{feature_id}` — Modifica Feature.

* **FR-P3 (Aggiornamento TestCaseDefinition):** Gli endpoint di creazione TestCaseDefinition devono accettare `feature_id` al posto di `epic_id`. L'endpoint diventa: `POST /api/features/{feature_id}/test-cases`.

* **FR-P4 (Aggiornamento lista test case per progetto):** L'endpoint `GET /api/projects/{project_id}/test-cases` deve continuare a funzionare, attraversando la nuova gerarchia Project → Epic → Feature → TestCaseDefinition. Deve supportare un filtro opzionale `feature_id` in aggiunta a `epic_id`.

* **FR-P5 (UI Pagina Epic aggiornata):** La pagina Epic deve mostrare le Feature al posto dei TestCaseDefinition diretti. Ogni Feature deve essere espandibile per mostrare i propri TestCaseDefinition.

* **FR-P6 (UI Pagina Feature):** Creare una pagina dedicata alla Feature (`/features/{feature_id}`) che mostri: nome, descrizione, Epic di appartenenza (link), lista dei TestCaseDefinition associati.

---

## 4. Requisiti Non Funzionali

* **NFR-11 (Migrazione dati):** La migrazione da `epic_id` a `feature_id` sui TestCaseDefinition deve avvenire automaticamente all'avvio, senza perdita di dati.
* **NFR-12 (Retrocompatibilità API):** Gli endpoint esistenti devono essere aggiornati in modo coerente. L'endpoint `GET /api/projects/{project_id}/test-cases` deve continuare a funzionare.
* **NFR-13 (Consistenza UI):** Le nuove pagine Feature devono adottare lo stesso stile visivo delle pagine Epic e Project esistenti.

---

## 5. Endpoints API (Riepilogo)

### Nuovi Endpoint

| Metodo | Endpoint | Descrizione |
|--------|----------|-------------|
| `POST` | `/api/epics/{epic_id}/features` | Crea una nuova Feature nell'Epic |
| `GET` | `/api/epics/{epic_id}/features` | Lista Feature dell'Epic |
| `GET` | `/api/features/{feature_id}` | Dettaglio Feature |
| `PUT` | `/api/features/{feature_id}` | Modifica Feature |
| `DELETE` | `/api/features/{feature_id}` | Elimina Feature (con vincolo) |
| `POST` | `/api/features/{feature_id}/test-cases` | Crea TestCaseDefinition nella Feature |
| `DELETE` | `/api/cases/{case_id}` | Elimina Test Case (hard delete) |

### Endpoint Modificati

| Metodo | Endpoint | Modifica |
|--------|----------|----------|
| `GET` | `/api/projects/{project_id}/test-cases` | Attraversa Feature; supporta filtro `feature_id` |
| `DELETE` | `/api/epics/{epic_id}` | Vincolo aggiornato: non eliminabile se ha Feature |

---

## 6. Riepilogo Modifiche

| Area | Modifica |
|------|----------|
| Modello dati | Nuova entità Feature (epic_id, name, description) |
| Modello dati | TestCaseDefinition: `epic_id` → `feature_id` |
| Modello dati | Epic: relazione verso Feature (non più verso TestCaseDefinition) |
| API | Nuovi endpoint CRUD Feature |
| API | Nuovo endpoint eliminazione Test Case |
| API | Aggiornamento creazione TestCaseDefinition (sotto Feature) |
| API | Aggiornamento filtri lista test case per progetto |
| UI | Pagina Epic mostra Feature (non più TestCaseDefinition diretti) |
| UI | Nuova pagina Feature con lista TestCaseDefinition |
| Migrazione | Auto-creazione Feature per Epic con TestCaseDefinition esistenti |
