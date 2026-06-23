# ISS Tracker - Project Rules & Guidelines for AI Agents

Welcome! This document outlines code architecture, safety rules, and UI/UX patterns specific to the **ISS Tracker** project. Please adhere to these instructions when proposing edits or additions.

---

## 🏗️ Code Architecture

- **Separation of Concerns:** All telemetry calculations, Nominatim reverse geocoding, nearest-land KD-Tree lookups, APOD querying, and API caches **must** reside in [tracker.py](file:///Users/prateeksharma/Developer/ISS_Tracker_PythonAnywhere/tracker.py).
- **Thin Handlers:** Keep [app.py](file:///Users/prateeksharma/Developer/ISS_Tracker_PythonAnywhere/app.py) (FastAPI web routes) and [main.py](file:///Users/prateeksharma/Developer/ISS_Tracker_PythonAnywhere/main.py) (CLI tool) thin. They should import their business logic from `tracker.py` rather than duplicating it.
- **Dependency Guard:** Avoid adding heavy third-party packages to `requirements.txt` unless strictly necessary. For instance, `.env` variables should be parsed manually (as done in `tracker.py`) to avoid installing additional environment management libraries.

---

## 🔒 API Usage & Safety Constraints

- **Throttling & Nominatim Limits:** OpenStreetMap's Nominatim API has a strict usage limit of **1 request per second** and bans IPs for aggressive querying.
  - **Rule:** Never bypass or modify the 5-second combined cache in `tracker.get_cached_iss_state()`.
  - **Rule:** Do not query Nominatim on every HTTP request; always serve geocoded locations from the cache.
- **NASA APOD Cache:** NASA APOD requests must remain cached for at least **1 hour** to avoid hitting rate limits.
- **Secrets Management:** Never hardcode custom API keys. Read secrets from environment variables using `os.environ.get("NASA_API_KEY")`.

---

## ⚡ FastAPI Concurrency & Event Loop

- **Sync I/O in Routes:** Because network calls (`requests.get`) and geocoding operations in `tracker.py` are synchronous and blocking, they will stall FastAPI's async event loop.
  - **Rule:** Web routes that call these operations **must** be defined with a standard synchronous `def` rather than `async def`. This instructs FastAPI to run the handler on a background threadpool.
  - **Exception:** Only use `async def` if you refactor the entire networking layer to use an asynchronous HTTP client like `httpx` or `aiohttp`.

---

## 🎨 UI/UX & Styling Guidelines

- **Theme & Palette:** Maintain the space-themed dark glassmorphism aesthetic. The container panels must use CSS `backdrop-filter: blur(16px)` and translucent backgrounds over the APOD layer.
- **Mapping:** Always use a dark map tileset (such as CartoDB Dark Matter) to match the space theme. Maintain the custom pulsing SVG satellite marker.
- **No Page Flickers:** Never use meta-refreshes or full page reloads to update the map or telemetry. All updates **must** be fetched dynamically using Javascript `fetch()` polling to `/api/position`.
- **User Panning Detection:** Ensure that when users are zooming or panning on the map, the automatic map centering does not aggressively snap back to the satellite coordinates (use the custom `userPanning` event listeners implemented in `index.html`).
