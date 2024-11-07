from django.urls import path

from users.views import Login, SignUp, Logout

urlpatterns = [
    path("signup/", SignUp.as_view()),
    path("login/", Login.as_view()),
    path("logout/", Logout.as_view()),
]
