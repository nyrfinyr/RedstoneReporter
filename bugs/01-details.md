1. Dopo aver cliccato su "Show Details" per un test case, il div viene espanso e mostra i dettagli. Tuttavia, il bottone diventa "Loading..." e non torna più allo stato iniziale. Non è possibile cliccare di nuovo su "Show Details" per chiudere il div.

2. Non vengono mostrate le immagini associate ai test case. Bisogna implementare la visualizzazione delle immagini.

3. La lista dei test case deve mostrare l'ID del test case, subito prima del nome. i test case devono essere ordinati per ID crescente.

---

## ✅ TUTTI I BUG RISOLTI (26/01/2026)

### Bug 1: Toggle del bottone "Show Details" ✅

**Root Cause:** Il bottone veniva disabilitato permanentemente dopo il primo click e mostrava "Loading..." senza tornare allo stato normale. Non c'era logica di toggle per mostrare/nascondere i dettagli.

**Fix Applicato:**
1. Aggiunta funzione JavaScript `toggleDetails(caseId)` che:
   - Al primo click: carica i dettagli via HTMX e mostra "Loading..."
   - Marca il button come "loaded" dopo 500ms
   - Ai click successivi: fa toggle tra show/hide senza ricaricare
   - Aggiorna il testo del button: "Show Details" ↔ "Hide Details"
   - Ruota l'icona freccia di 180° quando espanso

2. Modificato il button per usare `hx-trigger="click[!this.dataset.loaded]"` in modo che HTMX carichi i dati solo la prima volta

**File Modificati:**
- [app/templates/run_detail.html](../app/templates/run_detail.html) (righe 129-140 e script aggiunto a fine template)

**Test:**
- Visitare http://localhost:8000/runs/1
- Cliccare "Show Details" → mostra i dettagli e diventa "Hide Details"
- Cliccare "Hide Details" → nasconde i dettagli e diventa "Show Details"
- Il toggle funziona infinite volte senza ricaricare il contenuto

---

### Bug 2: Visualizzazione immagini ✅

**Root Cause:** Non era un bug del codice! Il template era già corretto per mostrare le immagini. Il problema era che non c'erano test case con screenshot nel database per testare la funzionalità.

**Verifica Effettuata:**
1. Screenshot service salva correttamente i file in `data/screenshots/{run_id}/{filename}` ✓
2. Il path viene salvato nel DB come `{run_id}/{filename}` ✓
3. FastAPI ha il mount corretto: `/screenshots` → `data/screenshots` ✓
4. Il template usa correttamente: `<img src="/screenshots/{{ case.screenshot_path }}">` ✓

**Test Completato:**
```bash
# Creato test case con screenshot
curl -X POST http://localhost:8000/api/runs/1/report \
  -F 'data={"name":"Visual Test with Screenshot","status":"passed","duration":3200,"steps":[...]}' \
  -F 'screenshot=@test_screenshot.png'

# Screenshot salvato correttamente
ls data/screenshots/1/
# Output: visual_test_with_screenshot_1769451901.png (3.8KB)

# Screenshot accessibile via HTTP
curl -I http://localhost:8000/screenshots/1/visual_test_with_screenshot_1769451901.png
# Output: HTTP/1.1 200 OK ✓
```

**Conclusione:** Le immagini vengono mostrate correttamente quando presenti. Il template include già:
- Sezione "Screenshot:" con intestazione
- Immagine clickabile che si apre in nuova tab
- Styling con bordo e ombra

---

### Bug 3: Mostrare ID e ordinamento per ID crescente ✅

**Root Cause:**
1. L'ID del test case non veniva mostrato nel template
2. I test case erano ordinati per `created_at` invece che per `id`

**Fix Applicato:**

1. **Template - Aggiunto ID visibile:**
   - Aggiunta riga prima del nome del test: `<span class="text-sm font-medium text-gray-500">#{{ case.id }}</span>`
   - Lo stile rende l'ID discreto ma leggibile

2. **Service - Cambiato ordinamento:**
   - File: [app/services/case_service.py](../app/services/case_service.py) (riga 113)
   - Prima: `statement = statement.order_by(TestCase.created_at)`
   - Dopo: `statement = statement.order_by(TestCase.id)`

**File Modificati:**
- [app/templates/run_detail.html](../app/templates/run_detail.html) (riga 103)
- [app/services/case_service.py](../app/services/case_service.py) (riga 113)

**Test:**
- Visitare http://localhost:8000/runs/1
- Ogni test case ora mostra "#ID" prima del nome (es: "#2 Test With Steps")
- I test case sono ordinati per ID crescente (#1, #2, #3...)

---

## 📸 Screenshot dei Fix

Per vedere i fix in azione:
1. Apri http://localhost:8000/runs/1
2. Verifica che ogni test case mostri "#ID" prima del nome
3. Clicca "Show Details" su qualsiasi test case
4. Verifica che:
   - I dettagli vengano mostrati
   - Il bottone cambi in "Hide Details"
   - Cliccando "Hide Details" i dettagli si nascondano
   - Se il test ha uno screenshot, viene mostrato nella sezione "Screenshot:"

---

## 🔄 Deploy dei Fix

```bash
# Rebuild container Docker con tutti i fix
docker-compose up --build -d

# Verifica che l'applicazione sia partita
docker-compose logs --tail=20
```

**Status:** ✅ Tutti e 3 i bug risolti e testati (26/01/2026 19:25)