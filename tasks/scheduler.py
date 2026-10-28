# tasks/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from tasks.reminde import check_and_send_reminders

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_and_send_reminders, 'interval', minutes=1)
    scheduler.start()

