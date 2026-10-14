MARKET COMPANION LIVE — REAL DATA CONNECTOR PROJECT

What this is
- A browser dashboard wired to request real candles and live ticks from OTCharts, an independent third-party read-only data provider.
- It is NOT affiliated with Pocket Option, Zentex, or Finorex.
- The blue outlined candle is only an estimate computed from recent data. Real market data cannot tell us the actual future candle in advance.
- The provider/API is third-party and can change. Check its current terms, supported symbols, timeframe limits, plan and pricing before relying on it.

Setup (computer required for this local starter)
1. Create an account and get an API key from https://otcharts.com/pocket-option-api (or its official API page https://otcharts.com/api).
2. Install Python 3.10+ if needed.
3. Put this folder somewhere on your computer.
4. Set the API key as an environment variable. Do not paste it into index.html or share it publicly.
   Windows PowerShell:
     $env:OTCHARTS_API_KEY="YOUR_KEY_HERE"
     python server.py
   macOS/Linux:
     export OTCHARTS_API_KEY="YOUR_KEY_HERE"
     python3 server.py
5. Open http://127.0.0.1:8000 in the browser on that same computer.
6. If provider symbol/timeframe identifiers differ for your plan, use the provider's current symbol catalogue/API documentation to adjust them.

Important
- This local starter does not itself create a public website link. For a permanent public link, deploy the frontend and a secure backend to a hosting service; never expose your provider key in frontend code.
- On Android alone, this local Python server setup may be inconvenient. A hosted backend is needed for an always-on public URL.
- The first version is read-only. It never asks for Pocket Option credentials and cannot place trades.
- If the feed API returns an error, check the server terminal and your provider dashboard.
