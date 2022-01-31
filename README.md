
# ED-COMMUNICATION-EMAIL-SERVICE-PYTHON


[![N|Solid](https://echodigital.org/img/echo-logo.png)](https://echodigital.org/)
[![Build Status](https://travis-ci.org/joemccann/dillinger.svg?branch=master)](echoindia.in)

ED email service for sending email in bulk or raw html email using amazon SQS and celery.
Features of service are below

  - Sending emails in bulk or single
  - Create email template using jinja2 templating language (Email template model inspired by django post-office library)
  - Fetch list of available email templates from internal as well as external databases
  - Unsubcribe user

### Tech Used

Email Service runs on python version 3+:

* [FastAPI](https://fastapi.tiangolo.com) - FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.6+ based on standard Python type hints.
* [Celery](https://docs.celeryproject.org/en/stable/getting-started/introduction.html) - Celery is a task queue implementation for Python web applications used to asynchronously execute work outside the HTTP request-response cycle.


### Installation

Email service requires [python]([https://www.python.org/](https://www.python.org/)) v3+ to run.

Install the dependencies and devDependencies and start the server.

Go in directory where you want to setup project, Create virtual environment
```sh
$ virtualenv env -p python3
```
Clone Project
```sh
$ git clone [project_url]
```
Go to project directory
```sh
$ cd project_directory
$ pip install -r requirements.txt
```
Now everything is setup & ready to run
```sh
$ uvicorn main:fastApp --reload
```

Yay! app started successfully :smiley:
#### Happy Coding  :blush:

### Plugins
Currently No Plugin available to link

### Author :heavy_check_mark:
[Sonu Pal](https://github.com/sonupal129/)
Python Developer, ECHO India