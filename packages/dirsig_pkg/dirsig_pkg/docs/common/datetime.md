# Datetime

Constructs a `datetime` object from individual year, month, day, hour, and minute components. The output is passed to the `Reference Datetime` input of the `Simulate` node to set the simulation start time.

Each field accepts a literal integer value or a link from a generator node (e.g. `Random Integer` or `Sweep np.arange`) to sweep or randomise the time of day or date across dataset runs.

## Inputs

- **Year** — integer, default `2023`
- **Month** — integer 1–12, default `1`
- **Day** — integer 1–31, default `1`
- **Hour** — integer 0–23, default `12`
- **Minute** — integer 0–59, default `0`

## Outputs

- **Datetime** — a Python `datetime` object in the scene's local timezone

## Example use

Link a `Sweep np.arange` node (start `6`, stop `20`, step `1`) to **Hour** to generate a time-of-day sweep from dawn to dusk across 14 dataset runs.
