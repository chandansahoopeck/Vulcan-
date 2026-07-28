from src.preflight.engine import run_preflight_or_raise,run_preflight_and_notify
from src.config.health_config import HEALTH_CHECKS
from vulcanBusinessLogic import vulcanBusinessLogic
import logging
import time
import os


def scheduled_job():
    # ✅ Gate execution
   #while True:
      report=run_preflight_and_notify(HEALTH_CHECKS)
      print("Final Report",report)
 
   
      if report.overall == "OK":   
         print("Running Bussiness Logic")    
         vulcanBusinessLogic()
      else:
         print("Health check Up Failed. Please check mail for Issue")   

     # sleep_duration = 12 * 3600
      #logging.info(f"Sleeping for {sleep_duration / 3600} hours.")
     # time.sleep(sleep_duration)
    # ✅
