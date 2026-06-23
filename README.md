# 🛰️ ISS Live Location Tracker

A modern, high-performance, and visually stunning web dashboard and CLI tool to track the International Space Station (ISS) in real-time. 

This project integrates real-time satellite telemetry, interactive maps, precise geocoding, offline proximity mapping, and NASA's Astronomy Picture of the Day.

---

## ✨ Features

- 🛰️ **Live Telemetry & Tracking:** Monitors geocentric coordinates of the ISS with dynamic 5-second updates.
- 🗺️ **Interactive World Map:** Visualizes the ISS position on an interactive map using **Leaflet.js** and CartoDB Dark Matter tiles, complete with custom satellite icon animations and orbital trajectory paths.
- 📍 **Precise Geocoding:** Reverse-geocodes coordinates via OpenStreetMap's **Nominatim API** to show exact administrative addresses (City, Country) when passing over land.
- 🌊 **Maritime Tracking:** Identifies ocean names when the ISS is cruising over water using bounding-box calculations.
- 🗺️ **Offline Proximity Fallback:** Computes the distance (in km) and bearing to the nearest landmass using a local KD-tree implementation (**Reverse Geocoder**), ensuring information is available even when Nominatim is rate-limited.
- 🌌 **Aesthetic Space Panels:** Features a modern glassmorphic dashboard (`backdrop-filter`) overlaid on NASA's APOD (Astronomy Picture of the Day).
- ⚡ **Performance & Safety Caching:**
  - Implements a **5-second combined cache** for ISS coordinates and geocoding to prevent API rate-limiting violations (Nominatim's 1 req/sec policy).
  - Uses standard FastAPI thread-pooling to prevent network requests from blocking the async event loop.

---

## 🛠️ Tech Stack

- **Backend:** FastAPI, Uvicorn, Jinja2, Requests
- **Data & Mapping:** Geopy, Reverse Geocoder, Numpy, Scipy
- **Frontend:** Vanilla HTML5, CSS3 (Glassmorphism), JavaScript (AJAX/Fetch, Leaflet.js)

---

## 📂 Architecture

The project maintains a clean separation of concerns:

```
├── app.py              # FastAPI Web Application & API endpoints
├── main.py             # Console-based Command Line Interface (CLI)
├── tracker.py          # Shared Core Logic, Caching, and Telemetry API
├── requirements.txt    # Python dependencies
├── .gitignore          # Excluded system, local env, and virtual env files
└── templates/
    └── index.html      # Responsive Glassmorphic Single Page Dashboard
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/prat3010/ISS_Tracker.git
   cd ISS_Tracker
   ```

2. Set up a virtual environment and activate it:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the CLI
Run the standalone console tracking script:
```bash
python main.py
```

### Running the Web Server
Launch the FastAPI development server:
```bash
python app.py
```
Open your browser and navigate to **`http://127.0.0.1:8000`** to view the live dashboard.

---

## ⚙️ Configuration

To use your own NASA API key for the APOD background instead of the public demo key:
1. Create a `.env` file in the root directory:
   ```env
   NASA_API_KEY=your_actual_nasa_api_key_here
   ```
2. The application will automatically detect and load this key at startup.
