from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from .settings import SWAGGER_URL, REDOC_URL, APP_NAME
from fastapi.middleware.cors import CORSMiddleware
from fastapi_health import health
from datetime import datetime
from email_service.settings import HOST_ADDRESS



def healthy_condition():
    return {
    "status": "UP",
    "success":True,
    "currentDT": datetime.now().strftime("%s"),
    "serverIp":HOST_ADDRESS
   
    
    }


def sick_condition():
    return { "status": "DOWN", 
    "success":False,
    "currentDT": datetime.now().strftime("%s"),
    "serverIp":HOST_ADDRESS}

# CODE BELOW



tags_metadata = [
    {
        "name": 'emails',
        "description": "send emails, create email _templates_ and sending emails in bulk with unsubscribing options"
    }
]

app = FastAPI(openapi_tags=tags_metadata, redoc_url=REDOC_URL, docs_url=SWAGGER_URL)




app.add_api_route("/email/health", health([healthy_condition]))

origins = ["*"]


app.add_middleware(


    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=APP_NAME,
        version="1.0.0",
        description="__ED-EMAIL-SERVICE__ is part of project ECHO upcoming product __ECHO Digital__, This micro service is based on python 3+ langugage with fastapi rest framework used to build\
         the service, service is used for mass communication with users using email, for documentation please refer readme docs",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://echodigital.org/img/echo-logo.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi