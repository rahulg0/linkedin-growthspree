from django.urls import path
from .views import *

urlpatterns = [
    path("linkedin/list-adAccounts/", LinkedInAdAccountsAPIView.as_view(), name="linkedin-adAccounts"),
    path("linkedin/adAccounts-analytics", LinkedInAdAnalyticsView.as_view(), name="adAccounts-analytics")
]