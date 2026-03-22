from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime

def scheduled_run(task):
    scheduler = BlockingScheduler()

    scheduler.add_job(task, trigger='interval', hours = 8, id='pipeline_run', next_run_time=datetime.now())
    scheduler.start()

