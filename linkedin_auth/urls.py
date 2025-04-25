from django.urls import path
from .views import *

urlpatterns = [
    path("linkedin/login/", LinkedInAuthRedirect.as_view(), name="linkedin-login"),
    path("oauth/callback/", LinkedInCallback.as_view(), name="linkedin-callback"),
    path("refresh-token", LinkedInRefreshToken.as_view(), name="linkedin-token-refresh")
]