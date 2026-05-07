# Addition

Adds two numeric values together. Either input can be a literal number, a string representation of a number, or a link from another node (e.g. a `Random Uniform` or `Sweep` node).

## Inputs

- **Input A**: First value (default: `0`)
- **Input B**: Second value (default: `0`)

## Outputs

- **Sum**: The result of `Input A + Input B`

## Example use

Connect a `Fixed Location Engine` altitude to `Input A` and a `Random Uniform` offset to `Input B` to randomise platform altitude around a base value.
