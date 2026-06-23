from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn
import tracker

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    """
    Renders the main dashboard page.
    Using standard 'def' instead of 'async def' tells FastAPI to run this route 
    in a thread pool, preventing blocking of the main event loop by synchronous APIs.
    """
    state = tracker.get_cached_iss_state()
    apod_url = tracker.get_apod_url()

    return templates.TemplateResponse("index.html", {
        "request": request,
        "lat": state.get("lat"),
        "lon": state.get("lon"),
        "location_data": state.get("location_data"),
        "error": state.get("error"),
        "apod_url": apod_url
    })

@app.get("/api/position")
def get_position():
    """
    API endpoint returning cached ISS telemetry and reverse geocoded info.
    Throttles geocoding and external API queries.
    """
    return tracker.get_cached_iss_state()

if __name__ == '__main__':
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)