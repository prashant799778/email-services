from .celery import (_test, _send_email)
from celery.result import AsyncResult
from celery.exceptions import InvalidTaskError
from functools import wraps
from email_service import settings
# CODE BELOW

def failedTaskQueueLogger(func):
    """If function failed it logs to db"""
    # Need to work more on it
    @wraps(func)
    def __wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            raise str(e)
    return __wrapper

@failedTaskQueueLogger
def test():
    return _test.delay()

   
def chunks(l, n):
    n = max(1, n)
    return (l[i:i+n] for i in range(0, len(l), n))

@failedTaskQueueLogger
def sendEmail(recipients,templateName, eta, **kwargs):
    print(recipients,'emailList')
    if not isinstance(recipients, list):
        raise TypeError("recipients should be in list or tuple")
    if len(recipients) <=100:
        _send_email.apply_async(args=[recipients, templateName, eta], kwargs=kwargs)
        return True

   
   

    chunks = lambda lst, sz: [lst[i:i+sz] for i in range(0, len(lst), sz)]
    for break_recipients in chunks(recipients,100):
        _send_email.apply_async(args=[break_recipients,templateName, eta], kwargs=kwargs)
       
    
    return True