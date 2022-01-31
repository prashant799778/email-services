from celery import Celery
from celery.utils.log import get_task_logger
from email_service import settings



# CODE BELOW

# Celery App Intialization
celery_app = Celery('tasks')
celery_app.config_from_object(settings)

# Registered Celery Taks
# Please make sure registered celery tasks name should be same as in sqs pull service registered celery tasks
# Else system will break and nothing will work

@celery_app.task
def _test():
    pass

@celery_app.task
def _send_email(recipients,templateName, eta, **kwargs):
    pass