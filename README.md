# Binance Copy Trader Intelligence

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/yashbajpaiknpindia-spec/adorefinal)

Read-only dashboard for Binance copy-trader profile discovery, stored historical records, approximate MAE/MFE trade-path analysis, detailed PDF reports, and CSV import/export.

The Docker deployment restores the application source from a split, checksum-verified compressed bundle. For easier editing, download the full source ZIP from the ChatGPT delivery and work from the normal, unbundled source files.

## Deploy

1. Click **Deploy to Render** above, sign in, connect the public GitHub repo if asked, and review the one web service in the Blueprint.
2. Set a strong value for the required `APP_PASSWORD` when prompted; Render generates `SECRET_KEY`.
3. Click **Apply** and follow the service's build/deploy logs. A successful creation request is not proof that the service is live—verify that `/health` returns `{"status":"ok"}`.
4. This free configuration is for an initial smoke test. SQLite on a free web service is not durable, and the service can sleep. For dependable future monitoring, configure a *dedicated* persistent PostgreSQL database and a non-sleeping service plan. Do not reuse another project's database.

## Data caveats

- Futures lead-trader discovery and closed-position history use undocumented Binance website endpoints; they can change, rate-limit, or stop working.
- Discovery covers the supported pages/rankings it can enumerate; it cannot prove it found **every** lead trader.
- Spot copy-trading routes are unverified. A Spot result is accepted only if a source returns a recognized data structure; unavailable history is reported, not fabricated.
- Candle-derived MAE/MFE uses OHLC bars, not tick-by-tick trade replay. Intrabar order is unknown and candle boundaries can overstate excursions.
- A historical record is only as complete as its source. Profile snapshots, realized closed positions, open positions, funding, fees, margin additions and liquidation state may have different coverage.
- The app requires no Binance account API key and does not place trades. Never add withdrawal permissions to an analytics project.
