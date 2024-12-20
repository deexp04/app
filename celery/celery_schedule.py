from celery.schedules import crontab
from flask import current_app as app
from application.celery.tasks import professional_email_reminder, check_service_requests, send_monthly_activity_reports

celery_app = app.extensions['celery']

@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):

    # daily message at 6:55 pm, everyday
    sender.add_periodic_task(crontab(hour=18, minute=55), professional_email_reminder.s('students@gmail', 'reminder to login', '<h1> hello everyone </h1>'), name='daily reminder' )

    # weekly messages
    sender.add_periodic_task(crontab(hour=18, minute=55, day_of_week='monday'), professional_email_reminder.s('students@gmail', 'reminder to login', '<h1> hello everyone </h1>'), name = 'weekly reminder' )

@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        60.0,  
        check_service_requests.s(),  
        name='Check service requests for professionals'
    )

    # sender.add_periodic_task(
    #     crontab(minute=0, hour=0, day_of_month=1),
    #     send_monthly_activity_reports.s(),
    #     name='Send Monthly Activity Reports'
    # )

    sender.add_periodic_task(
        60.0,
        send_monthly_activity_reports.s(),
        name='Send Monthly Activity Reports'
    )