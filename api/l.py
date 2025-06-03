import requests
from django.conf import settings
from datetime import datetime, date


def get_auth_token():
    print("Refreshing LinkedIn access token...")
    refresh_token = settings.LINKEDIN_REFRESH_TOKEN
    token_url = settings.LINKEDIN_BASE_URL + "oauth/v2/accessToken"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": settings.LINKEDIN_CLIENT_ID,
        "client_secret": settings.LINKEDIN_CLIENT_SECRET,
    }

    response = requests.post(token_url, data=data)
    token_data = response.json()
    # print(token_data)
    print(token_data.get("access_token"))
    return token_data.get("access_token")