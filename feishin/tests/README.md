# Frontend Test Structure

Recommended split:

- `tests/unit`: pure utility and config tests
- `tests/integration`: router and screen wiring tests
- `tests/mobile`: low-end Android and Telegram-focused smoke coverage

Current priority areas:

- runtime config parsing
- platform landing route selection
- hidden server bootstrap flow
- consumer shell rendering under narrow/mobile widths
