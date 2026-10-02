# Aston Martin DB9 V12 — Owner's Log

Source for **[db9v12.co.uk](https://db9v12.co.uk/)**: a real owner's log of living with and
working on a 5.9-litre Aston Martin DB9 V12, plus the workshop knowledge that isn't in the
official manual.

## What's on the site

- **[Owner's log](https://db9v12.co.uk/)** — every job done on the car, with photos.
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
- **[Misfire diagnosis case file](https://db9v12.co.uk/misfire-diagnostic.html)** — the blocked-injector saga, start to finish.
- **[AstonPi](https://db9v12.co.uk/astonpi.html)** — a Raspberry Pi 5 wireless CarPlay head unit built for the car.
- **[MOT history](https://db9v12.co.uk/mot-history.html)** — refreshed weekly from the DVSA MOT History API.

## How it's built

Plain static HTML served by GitHub Pages — no build step. `mot-history.json` is refreshed by
a weekly GitHub Action (`scripts/fetch_mot.py`); the API credentials and the registration live
in repository secrets and the registration/VIN are stripped before anything is written.

The guides are shared as-is from one owner's experience. Work on your own car at your own risk.
