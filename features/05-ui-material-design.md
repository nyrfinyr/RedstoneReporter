# Feature 05: Redesign UI in stile Material Design

## 1. Contesto

L'interfaccia attuale di RedstoneReporter utilizza TailwindCSS via CDN con classi utility applicate direttamente nell'HTML e tutti gli stili custom definiti in un blocco `<style>` inline nel template `base.html`. La navigazione principale e' una barra orizzontale in alto a destra con link a Dashboard, Progetti e API Docs.

Questa feature introduce:
- Un **redesign completo** dell'interfaccia ispirato al Material Design, prendendo come riferimento visivo il file `features/references/material-ui.png`.
- L'**esternalizzazione di tutti gli stili CSS** in file `.css` dedicati, separando completamente struttura HTML e presentazione.
- Una **barra di navigazione verticale a sinistra** (sidebar) che sostituisce la navbar orizzontale attuale.
- Un **aggiornamento della palette colori** coerente con il Material Design, mantenendo il supporto dark/light mode.

---

## 2. Riferimento Visivo

Il file `features/references/material-ui.png` mostra un dashboard in stile Material Design con le seguenti caratteristiche chiave da replicare:

- **Sidebar verticale a sinistra**: sfondo scuro, logo in alto, voci di navigazione con icone SVG inline e testo, voce attiva evidenziata con sfondo colorato e bordo arrotondato, voci raggruppabili con sotto-menu espandibili (chevron).
- **Area contenuto principale**: sfondo leggermente diverso dalla sidebar, card con angoli arrotondati e ombre morbide, layout a griglia responsive.
- **Top bar minimale**: opzionale, solo nella zona contenuto, con eventuale titolo pagina e toggle dark/light mode.
- **Tipografia pulita**: font sans-serif, gerarchia chiara tra titoli, sottotitoli e testo.
- **Elevazione e ombre**: card e componenti con ombre che suggeriscono elevazione (Material Design elevation).

---

## 3. Requisiti Funzionali

### Modulo S: Esternalizzazione CSS

#### FR-S1 (File CSS principali)
Creare i seguenti file CSS nella directory `static/css/`:
- `main.css` — stili globali: reset/normalize, tipografia base, variabili CSS custom (CSS custom properties) per i colori del tema, classi utility riutilizzabili.
- `layout.css` — stili per il layout generale: sidebar, area contenuto principale, top bar, sistema a griglia responsive.
- `components.css` — stili per i componenti UI: card, badge di stato e priorita', bottoni, form, tabelle, breadcrumb, toggle, indicatori di progresso.
- `dark-mode.css` — tutti gli override per la modalita' scura, utilizzando le variabili CSS definite in `main.css`.

#### FR-S2 (Rimozione stili inline)
- Rimuovere completamente il blocco `<style>` dal template `base.html`.
- Rimuovere il caricamento di TailwindCSS via CDN (`<script src="https://cdn.tailwindcss.com"></script>`).
- Sostituire tutte le classi utility di Tailwind presenti nei template HTML con classi CSS semantiche definite nei file `.css` creati in FR-S1.
- Ogni template HTML deve contenere esclusivamente markup strutturale e classi CSS semantiche (es. `class="sidebar-nav-item active"` invece di `class="flex items-center px-3 py-2 text-sm font-medium text-indigo-600 bg-indigo-50 rounded-md"`).

#### FR-S3 (Inclusione CSS nel template base)
Il template `base.html` deve includere i file CSS nell'ordine:
```html
<link rel="stylesheet" href="/static/css/main.css">
<link rel="stylesheet" href="/static/css/layout.css">
<link rel="stylesheet" href="/static/css/components.css">
<link rel="stylesheet" href="/static/css/dark-mode.css">
```

#### FR-S4 (Variabili CSS per il theming)
In `main.css` definire variabili CSS custom sulla pseudo-classe `:root` per tutti i colori del tema, in modo da centralizzare la palette e facilitare la manutenzione:
```css
:root {
    --color-primary: ...;
    --color-primary-light: ...;
    --color-primary-dark: ...;
    --color-surface: ...;
    --color-background: ...;
    --color-text-primary: ...;
    --color-text-secondary: ...;
    --color-border: ...;
    --color-success: ...;
    --color-error: ...;
    --color-warning: ...;
    --color-info: ...;
    --shadow-sm: ...;
    --shadow-md: ...;
    --shadow-lg: ...;
    --radius-sm: ...;
    --radius-md: ...;
    --radius-lg: ...;
}
```
In `dark-mode.css`, la classe `html.dark` deve sovrascrivere queste variabili con i valori della palette scura.

---

### Modulo N: Navigazione Sidebar

#### FR-N1 (Struttura sidebar)
Sostituire la navbar orizzontale attuale (`<nav>` in `base.html`) con una sidebar verticale fissa a sinistra con le seguenti caratteristiche:
- Larghezza fissa (indicativamente 260px, collassabile a sola icona su schermi piccoli).
- Altezza 100% del viewport (`height: 100vh`), con `position: fixed` o equivalente.
- Sfondo con colore distinto dall'area contenuto (scuro in dark mode, chiaro in light mode), come da riferimento visivo.
- Overflow verticale con scroll se il contenuto eccede l'altezza.

#### FR-N2 (Header sidebar)
La parte superiore della sidebar deve contenere:
- Il logo dell'applicazione (`/static/img/redstone.png`).
- Il nome "RedstoneReporter" come testo accanto al logo.
- In modalita' collassata, mostrare solo il logo.

#### FR-N3 (Voci di navigazione)
La sidebar deve contenere le seguenti voci di navigazione principali, ciascuna con un'icona SVG inline e il testo:
- **Dashboard** — link a `/` (icona: griglia/dashboard).
- **Progetti** — link a `/projects` (icona: cartella/folder).
- **API Docs** — link a `/docs`, apertura in nuova scheda (icona: documento/code).

#### FR-N4 (Navigazione contestuale gerarchica)
Quando l'utente naviga nella gerarchia Progetto → Epic → Feature → Definition, la sidebar deve mostrare il contesto corrente:
- Sotto la voce "Progetti", se si e' all'interno di un progetto, mostrare il nome del progetto come sotto-voce evidenziata.
- Se si e' all'interno di un'epic, mostrare anche il nome dell'epic come ulteriore sotto-voce indentata.
- Se si e' all'interno di una feature, mostrare anche il nome della feature.
- Ogni sotto-voce deve essere cliccabile per navigare al livello corrispondente.
- La voce attiva (corrispondente alla pagina corrente) deve essere evidenziata visivamente (sfondo colorato con bordo arrotondato, come da riferimento).

#### FR-N5 (Toggle dark/light mode nella sidebar)
Il pulsante di toggle dark/light mode deve essere posizionato nella parte inferiore della sidebar (prima del bordo inferiore), mantenendo la stessa funzionalita' attuale (toggle classe `dark` su `<html>`, salvataggio in localStorage).

#### FR-N6 (Sidebar responsive)
- Su schermi con larghezza >= 1024px: sidebar sempre visibile, area contenuto con margine sinistro pari alla larghezza della sidebar.
- Su schermi con larghezza < 1024px: sidebar nascosta di default, apribile tramite un pulsante hamburger posizionato nell'area contenuto (in alto a sinistra). La sidebar si apre come overlay sopra il contenuto con un backdrop semitrasparente. Cliccando il backdrop o un link della sidebar, questa si chiude.

---

### Modulo M: Stile Material Design

#### FR-M1 (Palette colori — Light Mode)
Definire una palette colori ispirata al Material Design per la modalita' chiara:
- **Primary**: Indigo/Blu (simile a Material Design primary, es. `#5D87FF` o equivalente).
- **Surface/Card**: Bianco (`#FFFFFF`).
- **Background**: Grigio molto chiaro (es. `#F5F7FA`).
- **Text primary**: Grigio scuro (es. `#2A3547`).
- **Text secondary**: Grigio medio (es. `#5A6A85`).
- **Sidebar background**: Bianco o grigio chiaro.
- **Bordi**: Grigio tenue (es. `#E5ECF0`).
- I colori di stato (passed, failed, running, skipped, completed, aborted) e priorita' (critical, high, medium, low) devono restare semanticamente riconoscibili ma armonizzati con la palette Material.

#### FR-M2 (Palette colori — Dark Mode)
Definire una palette scura coerente con il riferimento visivo (`material-ui.png`):
- **Primary**: Blu/Indigo chiaro (es. `#5D87FF`).
- **Surface/Card**: Blu scuro (es. `#202940` o `#1E293B`).
- **Background**: Blu molto scuro (es. `#0F172A` o `#171D2E`).
- **Sidebar background**: Blu scurissimo (es. `#111C2D` o `#0C1425`), piu' scuro del background principale.
- **Text primary**: Bianco/Grigio chiaro (es. `#E2E8F0`).
- **Text secondary**: Grigio medio (es. `#94A3B8`).
- **Bordi**: Grigio-blu scuro (es. `#334155`).
- Stessi colori di stato e priorita' adattati per leggibilita' su sfondo scuro.

#### FR-M3 (Card e elevazione)
Tutti gli elementi contenitore (elenco progetti, dettaglio epic, elenco test case, statistiche, ecc.) devono essere stilizzati come **card Material Design**:
- Angoli arrotondati (border-radius coerente, es. 8-12px).
- Ombra morbida che suggerisca elevazione (box-shadow multi-livello).
- Padding interno uniforme.
- Separazione visiva chiara dallo sfondo tramite il colore surface.

#### FR-M4 (Bottoni)
I bottoni devono seguire lo stile Material Design:
- **Bottoni primari**: sfondo colore primary, testo bianco, angoli arrotondati, ombra leggera, hover con colore primary scurito.
- **Bottoni secondari/outline**: bordo colore primary, sfondo trasparente, testo colore primary.
- **Bottoni di pericolo** (es. elimina): sfondo rosso, stesse caratteristiche dei primari.
- Transizione fluida su hover e focus (transition CSS).

#### FR-M5 (Form e input)
I campi di input, textarea e select devono seguire lo stile Material Design:
- Bordo inferiore o bordo completo arrotondato con colore tenue.
- Al focus: bordo colore primary con transizione fluida.
- Label posizionate sopra il campo con colore secondary.
- Messaggi di errore in rosso sotto il campo (se applicabile).

#### FR-M6 (Tabelle e liste)
Le tabelle e le liste di elementi devono:
- Avere header con sfondo leggermente diverso.
- Righe con hover evidenziato (sfondo leggermente piu' scuro).
- Bordi tra le righe sottili e tenuissimi.
- Badge di stato e priorita' con bordi arrotondati (pill shape).

#### FR-M7 (Breadcrumb)
I breadcrumb gia' presenti nelle pagine di dettaglio devono essere stilizzati coerentemente con il Material Design:
- Separatore visivo tra i livelli (es. chevron `>` o `/`).
- Link con colore primary, elemento corrente in testo normale.
- Posizionati nell'area contenuto, non nella sidebar.

#### FR-M8 (Transizioni e animazioni)
- Tutte le transizioni di stato (hover, focus, apertura/chiusura sidebar mobile, toggle dark mode) devono avere durata e easing coerenti (es. `transition: all 0.2s ease`).
- Mantenere l'animazione pulse esistente per gli indicatori di stato "running".

#### FR-M9 (Tipografia)
- Utilizzare un font sans-serif coerente con il Material Design. Caricare **Inter** o **Roboto** da Google Fonts come font principale.
- Definire una scala tipografica coerente per titoli (h1-h4), testo corpo, testo piccolo/caption, attraverso le variabili e classi in `main.css`.

---

### Modulo L: Aggiornamento Layout Area Contenuto

#### FR-L1 (Layout principale)
L'area contenuto principale deve:
- Occupare lo spazio rimanente a destra della sidebar.
- Avere un padding interno uniforme.
- Avere una larghezza massima ragionevole (es. `max-width: 1200px`) o adattarsi fluidamente.
- Il colore di sfondo deve essere il background della palette (distinto dal surface delle card).

#### FR-L2 (Pagine esistenti)
Tutte le pagine esistenti devono essere aggiornate per utilizzare i nuovi stili:
- `dashboard.html` — lista delle test run con card e statistiche.
- `projects_list.html` — griglia dei progetti con card.
- `project_detail.html` — dettaglio progetto con lista epic.
- `epic_detail.html` — dettaglio epic con lista feature.
- `feature_detail.html` — dettaglio feature con lista test case definition.
- `definition_detail.html` — dettaglio definition con storico esecuzioni.
- `definition_form.html` — form creazione/modifica test case.
- `run_detail.html` — dettaglio run con test case.
- Template parziali HTMX: `partials/run_list.html`, `partials/run_detail_content.html`, `partials/test_step_list.html`.

#### FR-L3 (Consistenza visiva)
Tutti i template devono utilizzare le stesse classi CSS semantiche definite nei file `.css`. Non devono essere presenti stili inline (`style="..."`) ne' classi utility di Tailwind residue nei template HTML.

---

## 4. Requisiti Non Funzionali

### NFR-01 (Nessuna dipendenza da framework CSS)
Non utilizzare TailwindCSS, Bootstrap, o altri framework CSS. Tutto lo stile deve essere CSS puro scritto a mano nei file `.css`, eventualmente con variabili CSS custom. L'unica dipendenza esterna consentita e' il font da Google Fonts.

### NFR-02 (Compatibilita' browser)
Gli stili devono funzionare correttamente sui browser moderni (Chrome, Firefox, Edge, Safari nelle ultime 2 versioni). E' consentito l'uso di CSS custom properties, flexbox, grid, e altre feature CSS moderne.

### NFR-03 (Nessun flash di contenuto non stilizzato)
Il meccanismo di prevenzione del flash di dark mode (script nel `<head>` che applica la classe `dark` prima del rendering) deve essere mantenuto.

### NFR-04 (HTMX invariato)
La libreria HTMX e il suo funzionamento (auto-refresh, caricamento parziali) non devono essere modificati. I partial template devono continuare a funzionare correttamente con i nuovi stili.

### NFR-05 (Performance)
I file CSS combinati non devono superare i 50KB (non minificati). Non devono essere introdotte dipendenze JavaScript aggiuntive per lo stile (no CSS-in-JS, no preprocessori runtime).

### NFR-06 (Manutenibilita')
L'uso di variabili CSS custom per colori, ombre, raggi e spaziature deve garantire che un cambio di palette colori richieda modifiche solo nelle definizioni `:root` e `html.dark` senza toccare le regole dei componenti.

---

## 5. File Coinvolti

### File da creare
- `static/css/main.css`
- `static/css/layout.css`
- `static/css/components.css`
- `static/css/dark-mode.css`

### File da modificare
- `app/templates/base.html` — rimuovere `<style>` e TailwindCSS CDN, aggiungere link ai CSS, ristrutturare layout con sidebar.
- `app/templates/dashboard.html` — sostituire classi Tailwind con classi semantiche.
- `app/templates/projects_list.html` — sostituire classi Tailwind con classi semantiche.
- `app/templates/project_detail.html` — sostituire classi Tailwind con classi semantiche.
- `app/templates/epic_detail.html` — sostituire classi Tailwind con classi semantiche.
- `app/templates/feature_detail.html` — sostituire classi Tailwind con classi semantiche.
- `app/templates/definition_detail.html` — sostituire classi Tailwind con classi semantiche.
- `app/templates/definition_form.html` — sostituire classi Tailwind con classi semantiche.
- `app/templates/run_detail.html` — sostituire classi Tailwind con classi semantiche.
- `app/templates/partials/run_list.html` — sostituire classi Tailwind con classi semantiche.
- `app/templates/partials/run_detail_content.html` — sostituire classi Tailwind con classi semantiche.
- `app/templates/partials/test_step_list.html` — sostituire classi Tailwind con classi semantiche.

### File da rimuovere
- `static/css/.gitkeep` — non piu' necessario una volta creati i file CSS.

---

## 6. Note per l'implementazione

1. **Ordine suggerito**: iniziare da FR-S1 e FR-S4 (creare i file CSS con le variabili), poi FR-N1-N6 (sidebar), poi FR-M1-M9 (stili Material), poi FR-S2 (rimozione Tailwind da tutti i template), poi FR-L2 (aggiornamento pagine).
2. **Navigazione contestuale (FR-N4)**: per popolare la sidebar con il contesto gerarchico, potrebbe essere necessario passare dati aggiuntivi ai template tramite il context Jinja2 (es. progetto corrente, epic corrente). Verificare i route handler in `app/web/routes.py`, `app/web/project_routes.py` e `app/web/htmx_routes.py`.
3. **Test visivo**: dopo ogni modulo, verificare che tutte le pagine siano visivamente corrette sia in dark mode che in light mode.
4. **Riferimento**: il file `features/references/material-ui.png` mostra il target visivo per la dark mode. La light mode deve essere la controparte chiara coerente.
