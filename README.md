# Fansale Ticket Alert Bot

Bot di monitoraggio per [Fansale.it](https://www.fansale.it) che avvisa in tempo reale quando compaiono nuovi biglietti per un evento.

## Come funziona

Lo script si connette al tuo Chrome tramite il **Chrome DevTools Protocol (CDP)**, ricarica la pagina ogni 15 secondi e confronta la lista dei biglietti disponibili. Quando compaiono nuovi `data-offer-id`, porta Chrome in primo piano e mostra un popup di sistema.

Poiché usa il tuo browser reale già aperto, il sito non rileva alcuna attività automatizzata.

## Requisiti

- Python 3.10+
- Google Chrome installato

## Installazione

```powershell
python -m venv .venv
.venv\Scripts\pip install playwright
.venv\Scripts\python.exe -m playwright install chromium
```

## Utilizzo

### 1. Avvia Chrome con il debug port

Chiudi Chrome completamente, poi esegui in PowerShell:

```powershell
Stop-Process -Name chrome -Force -ErrorAction SilentlyContinue
Start-Process "C:\Program Files\Google\Chrome\Application\chrome.exe" `
  -ArgumentList "--remote-debugging-port=9222 --user-data-dir=C:\Temp\chrome-debug-profile"
```

Verifica che funzioni aprendo nel browser: `http://localhost:9222/json`

### 2. Avvia lo script

Passa l'URL della pagina Fansale come argomento:

```powershell
.venv\Scripts\python.exe ticketAlert.py "https://www.fansale.it/tickets/all/artista/000000/00000000"
```

Con intervallo di aggiornamento personalizzato (es. 30 secondi):

```powershell
.venv\Scripts\python.exe ticketAlert.py "https://www.fansale.it/tickets/all/artista/000000/00000000" --interval 30
```

Per uscire usa `Ctrl+C`.

## Comportamento

| Situazione | Azione |
|---|---|
| Pagina senza biglietti | Monitora silenziosamente |
| Nuovi biglietti trovati | Porta Chrome in primo piano + popup di sistema |
| Caricamento fallito | Riprova al ciclo successivo senza modificare la lista |
| Premi un tasto dopo il popup | Il monitoraggio riprende |

## Opzioni CLI

| Argomento | Descrizione | Obbligatorio |
|---|---|---|
| `url` | URL della pagina Fansale da monitorare | Sì |
| `--interval` | Secondi tra un aggiornamento e l'altro (default: `15`) | No |
