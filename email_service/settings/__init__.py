from .settings import *




if ENVIRONMENT not in ["dev", "qa", "prod",'demo']:
    raise TypeError("Incorrect environment shoule be dev, prod or qa")

_MANDATORY_SETTINGS = [AWS_REGION_NAME, AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY, SES_EMAIL_FROM,
                        AWS_QUEUE_NAME, AWS_QUEUE_URL, ENVIRONMENT]

if not all(_MANDATORY_SETTINGS):
    local_keys = list(filter(lambda key: key.isupper(), locals().keys()))
    for key in local_keys:
        var = eval(key)
        if var in _MANDATORY_SETTINGS and var in [None, ""]:
            raise ValueError(f"setting {key} variable can not be blank or {var}")


# CELERY Broker Settings
task_default_queue = AWS_QUEUE_NAME

broker_transport_options = {
    'predefined_queues': {
        task_default_queue : {
            'url': AWS_QUEUE_URL,
            'access_key_id': AWS_ACCESS_KEY,
            'secret_access_key': AWS_SECRET_ACCESS_KEY,
            'visibility_timeout':60,
            'polling_interval': 1
             
        },
    },
    'region': AWS_REGION_NAME
}

MAX_MAIL_SEND_QUEUE=1000
broker_url = 'sqs://{access_key}:{secret_key}@'.format(
    access_key=quote(AWS_ACCESS_KEY, safe=''),
    secret_key=quote(AWS_SECRET_ACCESS_KEY, safe=''),
)
broker_user = AWS_ACCESS_KEY
broker_password = AWS_SECRET_ACCESS_KEY