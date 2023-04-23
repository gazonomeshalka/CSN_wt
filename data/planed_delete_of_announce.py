from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import delete


scheduler = BackgroundScheduler()


def set_time_for_announce(id, time):
    scheduler.add_job(del_announce, 'date', run_date=time, args=[id])
    return


def del_announce(id):
    delete(Announce).where(Announce.id == id)
    return
