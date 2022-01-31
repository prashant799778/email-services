from email_service import app as fastApp
from emails import views as email_view

# CODE BELOW


# Register Email Router
fastApp.include_router(email_view.router,
                    tags=["Emails"],
                       prefix="/email",
                    responses={404: {"error": "email router missing"}},
)

