from django.urls import path

from users.views import CertifiedEmail, Login, Logout, ResetPassword, SignUp

urlpatterns = [
    path("signup/", SignUp.as_view()),
    path("login/", Login.as_view()),
    path("logout/", Logout.as_view()),
    path("certified/email/<str:uid64>/<str:token>/", CertifiedEmail.as_view()),
    path("reset/password/", ResetPassword.as_view()),
    path("reset/password/<str:uid64>/<str:token>/", ResetPassword.as_view()),
]
