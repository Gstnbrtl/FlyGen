import asyncio
import json
from datetime import date
from playwright.async_api import async_playwright

URL = "https://www.negropadel.com/"

MONTHS_ES = {
    'ene': 1, 'feb': 2, 'mar': 3, 'abr': 4, 'may': 5, 'jun': 6,
    'jul': 7, 'ago': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dic': 12
}


async def _scrape(target_date: date, debug: bool = False) -> dict:
    api_data = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--no-zygote',
                '--single-process',
                '--disable-extensions',
                '--disable-background-networking',
                '--disable-default-apps',
                '--mute-audio',
            ]
        )
        page = await browser.new_page()

        # Capture any API responses that might contain slot data
        async def on_response(response):
            url = response.url.lower()
            if any(k in url for k in ('turno', 'slot', 'reserva', 'disponib', 'cancha')):
                try:
                    body = await response.json()
                    api_data.append({'url': response.url, 'body': body})
                except Exception:
                    pass

        page.on('response', on_response)

        await page.set_viewport_size({"width": 1280, "height": 900})
        await page.goto(URL, wait_until='networkidle', timeout=60000)
        await page.wait_for_timeout(5000)

        # If we intercepted an API, use it (faster and more reliable)
        if api_data and not debug:
            await browser.close()
            return {'source': 'api', 'data': api_data}

        # Build the JS payload as a plain string to avoid f-string escape issues
        js_code = """() => {
            const targetDay   = TARGET_DAY;
            const targetMonth = TARGET_MONTH;
            const MONTHS = {
                'ene':1,'enero':1,'feb':2,'febrero':2,'mar':3,'marzo':3,
                'abr':4,'abril':4,'may':5,'mayo':5,'jun':6,'junio':6,
                'jul':7,'julio':7,'ago':8,'agosto':8,'sep':9,'septiembre':9,
                'oct':10,'octubre':10,'nov':11,'noviembre':11,'dic':12,'diciembre':12
            };

            const allEls = Array.from(document.querySelectorAll('*'));

            // ---- 1. Find day headers (flexible children count) ----
            const dayHeaders = allEls.filter(el => {
                if (el.children.length > 5) return false;
                const t = el.textContent.trim().toLowerCase();
                return /^(lunes|martes|mi|jueves|viernes|s[aá]bado|domingo)/i.test(t);
            });

            // ---- 2. Match by day number + month (flexible format) ----
            let targetHeader = null;
            for (const h of dayHeaders) {
                const t = h.textContent.trim().toLowerCase();
                // Try "26 abr", "26 abril", "abr 26", "26/04", etc.
                const m1 = t.match(/(\\d{1,2})\\s*[/\\-\\s]?\\s*(ene(?:ro)?|feb(?:rero)?|mar(?:zo)?|abr(?:il)?|may(?:o)?|jun(?:io)?|jul(?:io)?|ago(?:sto)?|sep(?:tiembre)?|oct(?:ubre)?|nov(?:iembre)?|dic(?:iembre)?)/i);
                const m2 = t.match(/(ene(?:ro)?|feb(?:rero)?|mar(?:zo)?|abr(?:il)?|may(?:o)?|jun(?:io)?|jul(?:io)?|ago(?:sto)?|sep(?:tiembre)?|oct(?:ubre)?|nov(?:iembre)?|dic(?:iembre)?)\\s*(\\d{1,2})/i);
                const m3 = t.match(/(\\d{1,2})\\/(\\d{1,2})/);
                let d = null, mo = null;
                if (m1) {
                    d  = parseInt(m1[1]);
                    mo = MONTHS[m1[2].replace(/[^a-z]/g,'').substring(0,3).toLowerCase()];
                } else if (m2) {
                    d  = parseInt(m2[2]);
                    mo = MONTHS[m2[1].replace(/[^a-z]/g,'').substring(0,3).toLowerCase()];
                } else if (m3) {
                    d  = parseInt(m3[1]);
                    mo = parseInt(m3[2]);
                }
                if (d === targetDay && mo === targetMonth) {
                    targetHeader = h;
                    break;
                }
            }

            if (!targetHeader) {
                return {
                    error: 'day_not_found',
                    available_headers: dayHeaders.map(h => h.textContent.trim()).slice(0, 15),
                    page_text_sample: document.body.innerText.substring(0, 500)
                };
            }

            // ---- 2. Use bounding rect to find the X range of today's column ----
            const hRect = targetHeader.getBoundingClientRect();
            const colLeft  = hRect.left;
            const colRight = hRect.right;
            const colMid   = (colLeft + colRight) / 2;

            // ---- 3. Find all slot elements that visually fall within this column ----
            // A "slot card" is an element that contains a time AND a status word,
            // whose center X is within today's column bounds.
            const slotCards = allEls.filter(el => {
                const t = el.textContent.trim();
                if (!/(DISPONIBLE|RESERVADO|EN CURSO|FINALIZADO)/i.test(t)) return false;
                if (!/\\d{2}:\\d{2}/.test(t)) return false;
                if (el.children.length > 6) return false;   // not a root container
                const r = el.getBoundingClientRect();
                if (r.width < 50 || r.height < 20) return false;
                const cx = (r.left + r.right) / 2;
                return cx >= colLeft && cx <= colRight;
            });

            // Deduplicate: keep the smallest card that contains each time slot
            const seen = new Set();
            const slots = [];
            for (const card of slotCards) {
                const text = card.textContent.trim();
                const timeMatch   = text.match(/(\\d{2}:\\d{2})/);
                const priceMatch  = text.match(/\\$([\\d.,]+)/);
                const statusMatch = text.match(/(DISPONIBLE|RESERVADO|EN CURSO|FINALIZADO)/i);
                if (!timeMatch) continue;
                const key = timeMatch[1];
                if (seen.has(key)) continue;
                seen.add(key);
                slots.push({
                    time:   timeMatch[1],
                    price:  priceMatch  ? '$' + priceMatch[1] : null,
                    status: statusMatch ? statusMatch[1].toUpperCase() : 'UNKNOWN'
                });
            }

            // Sort by time
            slots.sort((a, b) => a.time.localeCompare(b.time));

            return { source: 'dom', slots };
        }"""

        js_code = js_code.replace('TARGET_DAY',   str(target_date.day))
        js_code = js_code.replace('TARGET_MONTH', str(target_date.month))

        result = await page.evaluate(js_code)

        if debug:
            result['api_intercepted'] = api_data

        await browser.close()
        return result


def get_available_slots(target_date: date = None, debug: bool = False) -> list:
    """Return a list of DISPONIBLE slots for the given date (defaults to today)."""
    if target_date is None:
        target_date = date.today()

    raw = asyncio.run(_scrape(target_date, debug=debug))

    if debug:
        print(json.dumps(raw, indent=2, ensure_ascii=False, default=str))

    if 'error' in raw:
        raise RuntimeError(f"Scraper: {raw['error']} -- {raw}")

    if raw.get('source') == 'api':
        raise NotImplementedError("API source detected -- inspeccionar raw['data'] para parsear.")

    slots = raw.get('slots', [])
    return [s for s in slots if s['status'] == 'DISPONIBLE' and s['time'] >= '14:30']


if __name__ == '__main__':
    import sys
    debug_mode = '--debug' in sys.argv
    slots = get_available_slots(debug=debug_mode)
    if slots:
        print(f"\nTurnos disponibles hoy ({date.today().strftime('%d/%m/%Y')}):")
        for s in slots:
            print(f"  {s['time']}  {s['price'] or ''}")
    else:
        print("No hay turnos disponibles hoy.")
