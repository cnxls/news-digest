from apscheduler.schedulers.blocking import BlockingScheduler

def scheduled_run(task, hour: int = 9, minute: int = 0):
    scheduler = BlockingScheduler()

    scheduler.add_job(task, 'cron', hour=hour, minute=minute , id='morning_run')
    scheduler.start()

