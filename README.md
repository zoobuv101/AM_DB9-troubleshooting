# Aston Martin DB9 V12 — Owner's Log

Source for **[db9v12.co.uk](https://db9v12.co.uk/)**: a real owner's log of living with and
working on a 5.9-litre Aston Martin DB9 V12, plus the workshop knowledge that isn't in the
official manual.

## What's on the site

- **[Owner's log](https://db9v12.co.uk/)** — every job done on the car, with photos.
- **[The DB9](https://db9v12.co.uk/db9.html)** — the car itself: design, engineering, the glass ECU key, the 2009 spec and model history.
- **[Workshop reference](https://db9v12.co.uk/reference.html)** — DIY guides from real work on this car:
  - [ZF 6HP26 Touchtronic gearbox service](https://db9v12.co.uk/ref-gearbox-service.html)
  - [Rear diff oil specs and alternatives](https://db9v12.co.uk/ref-diff-oil.html)
  - [V12 cylinder numbering and twin-ECU mapping](https://db9v12.co.uk/ref-cylinder-numbering.html)
  - [Misfire fault codes — real vs ghost](https://db9v12.co.uk/ref-fault-codes.html)
  - [Misfire relearn (coast-down)](https://db9v12.co.uk/ref-misfire-relearn.html)
  - [Dead-cylinder checklist](https://db9v12.co.uk/ref-dead-cylinder.html)
  - [Ultrasonic injector cleaning](https://db9v12.co.uk/ref-injector-cleaning.html)
  - [Rear light condensation fix](https://db9v12.co.uk/ref-rear-light-condensation.html)
  - [SmarTire TPMS pinout and defeat cable](https://db9v12.co.uk/ref-tpms-defeat.html)
  - [ThinkDiag numbering caveats](https://db9v12.co.uk/ref-thinkdiag.html)
  - [VIN decoder](https://db9v12.co.uk/ref-vin-decoder.html) — engine code, gearbox and model from any 2005–18 Gaydon-era VIN, decoded in the browser. Letter tables live in `scripts/build_vin_spec.py` (run it, then `scripts/build_guides.py`)
- **[Misfire diagnosis case file](https://db9v12.co.uk/misfire-diagnostic.html)** — the blocked-injector saga, start to finish.
- **[AstonPi](https://db9v12.co.uk/astonpi.html)** — a Raspberry Pi 5 wireless CarPlay head unit built for the car.
- **[MOT history](https://db9v12.co.uk/mot-history.html)** — refreshed weekly from the DVSA MOT History API.
- **[Friends](https://db9v12.co.uk/friends.html)** — meets and drives with other Gaydon-era Astons.

## How it's built

Plain static HTML served by GitHub Pages — no build step. `mot-history.json` is refreshed by
a weekly GitHub Action (`scripts/fetch_mot.py`); the API credentials and the registration live
in repository secrets and the registration/VIN are stripped before anything is written.

After every GitHub Pages build, the IndexNow Action (`scripts/indexnow.py`) tells Bing, Yandex,
Seznam, Naver and Yep which pages changed since its last successful run. The key is the
`<32 hex>.txt` file at the site root. Run the workflow by hand with "Submit every page" ticked to
resubmit the whole sitemap. Google doesn't use IndexNow; use Search Console for it.

Every page's footer links to my other sites (hifisounds.co.uk, only-vans.uk, uv101.uk) with
hover descriptions; the styles are `.sister-sites` in `assets/site-fx.css`. Pages load that
stylesheet as `site-fx.css?v=YYYYMMDD`, so bump the date on every page after changing it.

© 2026 db9v12.co.uk — all rights reserved; see [LICENSE](LICENSE). The guides are shared as-is from
one owner's experience. Work on your own car at your own risk.
