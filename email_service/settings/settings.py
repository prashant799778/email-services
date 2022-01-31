from urllib.parse import quote
import os



# from botocore.credentials import InstanceMetadataProvider, InstanceMetadataFetcher
# provider = InstanceMetadataProvider(iam_role_fetcher=InstanceMetadataFetcher(timeout=1000, num_attempts=2))
# credentials = provider.load()
# access_key = credentials.access_key
# secret_key = credentials.secret_key








# if (access_key and secret_key):
#     AWS_ACCESS_KEY=access_key
#     AWS_SECRET_ACCESS_KEY=secret_key

# if not (access_key and secret_key):

AWS_ACCESS_KEY=os.getenv("AWS_ACCESS_KEY_COMMUNICATION",None)
AWS_SECRET_ACCESS_KEY=os.getenv("AWS_SECRET_ACCESS_KEY_COMMUNICATION",None)




# CODE BELOW


# Celery Configuration Files

ACCEPT_CONTENT = ['application/json']
TASK_SERIALIZER = 'json'
RESULT_SERIALIZER = 'json'
broker_transport = 'sqs'

result_expires=18000*4


APP_NAME = 'ed-email-service'
MAX_MAIL_SEND_QUEUE = os.getenv("MAX_MAIL_SEND_QUEUE",1000) #Send max mail in single queue request
HOST_ADDRESS = os.getenv("HOST_ADDRESS", "127.0.0.1")

# Project Documentation URL




SWAGGER_URL = "/swagger-ui.html/"
REDOC_URL = "/docs/"
ENVIRONMENT = os.getenv("ENVIRONMENT")

entityId='EMAIL'



AWS_REGION_NAME=os.getenv("REGION_NAME",None)
AWS_QUEUE_NAME=os.getenv("QUEUE_NAME_EMAIL",None)
AWS_QUEUE_URL=os.getenv("QUEUE_EMAIL",None)


SES_EMAIL_FROM="no-reply@iecho.org"











if ENVIRONMENT not in ["dev", "prod", "qa","demo"]:
    raise TypeError(f"Incorrect {ENVIRONMENT} name, should be dev, prod or qa,demo")
