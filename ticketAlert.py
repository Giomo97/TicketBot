import argparse
import ctypes
import msvcrt
import time
from datetime import datetime

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

REFRESH_INTERVAL = 15  # secondi tra un aggiornamento e l'altro
CDP_URL = "http://localhost:9222"


def popup_avviso(nuovi: list[str]) -> None:
    """Mostra un popup di sistema con l'elenco dei nuovi biglietti."""
    messaggio = f"Trovati {len(nuovi)} nuovi biglietti!\n\nOffer ID:\n" + "\n".join(nuovi)
    ctypes.windll.user32.MessageBoxW(0, messaggio, "🎟 Fansale Alert", 0x40 | 0x1000)


def scrivi_riga(testo: str) -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {testo}")


def leggi_offer_ids(page) -> list[str]:
    """Ricarica la pagina e restituisce la lista dei data-offer-id."""
    page.reload(wait_until="domcontentloaded", timeout=60000)

    try:
        page.wait_for_selector(".EventEntryList.js-EventEntryList", timeout=15000)
    except PlaywrightTimeout:
        return []

    entries = page.query_selector_all("[data-offer-id]")
    return [
        eid for e in entries
        if (eid := e.get_attribute("data-offer-id")) and eid != "0"
    ]


def main(url: str) -> None:
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(CDP_URL)
        context = browser.contexts[0]
        page = context.pages[0]

        scrivi_riga(f"Connesso a Chrome. Navigazione verso: {url}")
        page.goto(url, wait_until="domcontentloaded", timeout=60000)

        # Accetta cookie se compare il banner
        try:
            page.click("text=Accetta tutti i Cookie", timeout=5000)
            page.wait_for_timeout(1000)
        except PlaywrightTimeout:
            pass

        old_ids: set[str] = set()
        scrivi_riga(f"Monitoraggio attivo. Aggiornamento ogni {REFRESH_INTERVAL}s. Ctrl+C per uscire.")

        while True:
            scrivi_riga("Aggiornamento pagina...")
            new_ids = set(leggi_offer_ids(page))

            if not new_ids:
                scrivi_riga("Nessun biglietto trovato (lista assente o caricamento fallito), riprovo...")
            else:
                nuovi = new_ids - old_ids
                if nuovi:
                    scrivi_riga(f"*** NUOVI BIGLIETTI TROVATI: {sorted(nuovi)} ***")
                    page.bring_to_front()
                    popup_avviso(sorted(nuovi))
                    print("\nPremi un tasto per riprendere il monitoraggio...")
                    msvcrt.getch()
                    scrivi_riga("Monitoraggio ripreso.")
                    old_ids = new_ids
                else:
                    scrivi_riga(f"Nessun nuovo biglietto. Totale: {len(new_ids)}")
                    old_ids = new_ids

            time.sleep(REFRESH_INTERVAL)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitora i biglietti su Fansale.it")
    parser.add_argument("url", help="URL della pagina Fansale da monitorare")
    parser.add_argument(
        "--interval",
        type=int,
        default=REFRESH_INTERVAL,
        help=f"Secondi tra un aggiornamento e l'altro (default: {REFRESH_INTERVAL})",
    )
    args = parser.parse_args()
    REFRESH_INTERVAL = args.interval
    main(args.url)
