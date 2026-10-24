# Binance Copy Trader Intelligence
Read-only dashboard for Binance copy-trader profile discovery, stored historical records, approximate MAE/MFE path analysis, PDF reports and CSV exports.

The deployed container restores the source bundle at build time. For easier editing, use the full source ZIP attached to the related ChatGPT delivery instead of editing the bundle file manually.

## Data caveats
- Futures listing and closed-position history use undocumented Binance website endpoints; they can change, rate-limit or stop working.
- Discovery scans leaderboard pages/rankings; it cannot prove that it found every lead trader.
- Spot copy-trading routes are unverified. A Spot result is accepted only if the source returns a recognized structure.
- Candle-derived MAE/MFE estimates use OHLC bars, not tick-by-tick trade replay. Intrabar order is unknown and candle-window boundaries can overstate excursions.
- No Binance account API key is required. The app does not place orders.

## Render
The repository includes a Dockerfile and a Render Blueprint. Configure APP_PASSWORD before exposing the dashboard. For persistent future monitoring, set DATABASE_URL to a dedicated persistent PostgreSQL database and use a non-sleeping service plan. Do not reuse a database from another project. Free web services sleep and their local SQLite data is not durable across redeploys.
