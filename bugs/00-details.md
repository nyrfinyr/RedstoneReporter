quando clicco su show details non mi fa vedere i dettagli del test case. Non ci sono log di errore. Indagare.

## ✅ RISOLTO

**Root Cause:** Il div target `#case-details-{case_id}` aveva la classe CSS `hidden` (TailwindCSS) che applica `display: none`. Quando HTMX caricava il contenuto con `hx-swap="innerHTML"`, il contenuto veniva inserito correttamente nel div ma il div stesso rimaneva nascosto.

**Fix Applicato:**
- Aggiunto `onclick` al button che rimuove la classe `hidden` dal div target prima che HTMX carichi il contenuto
- Aggiunto feedback visivo "Loading..." durante il caricamento
- Il button viene disabilitato dopo il click per evitare doppi click

**File Modificato:** [app/templates/run_detail.html](../app/templates/run_detail.html) (linea 134)

**Test:**
```bash
# Creare un test case con steps
curl -X POST http://localhost:8000/api/runs/1/report \
  -F 'data={"name":"Test With Steps","status":"failed","duration":2500,"steps":[{"description":"Step 1","status":"passed"}]}'

# Visitare http://localhost:8000/runs/1
# Cliccare "Show Details" - ora mostra correttamente gli step
```

**Verificato:** ✅ Funzionante (26/01/2026)