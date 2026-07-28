import threading
import uvicorn
from src.api.health_api import app
from src.scheduler.scheduler import scheduled_job
import urllib3
import warnings

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore",category=UserWarning,module="requests")

def start_api():
    uvicorn.run(app, host="0.0.0.0", port=8000)

def start_scheduler():
    scheduled_job()

if __name__ == "__main__":

    threading.Thread(target=start_api, daemon=True).start()
    start_scheduler()
