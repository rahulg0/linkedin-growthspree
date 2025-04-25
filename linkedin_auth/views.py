import requests
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

class LinkedInAuthRedirect(APIView):
    def get(self, request):
        base_url = "https://www.linkedin.com/oauth/v2/authorization"
        scope = "openid%20r_ads_reporting%20profile%20r_organization_social%20rw_organization_admin%20w_member_social%20r_ads%20w_organization_social%20rw_ads%20r_basicprofile%20r_organization_admin%20r_1st_connections_size%20email"
        params = {
            "response_type": "code",
            "client_id": settings.LINKEDIN_CLIENT_ID,
            "redirect_uri": settings.LINKEDIN_REDIRECT_URI,
            "scope": scope,
            "state": "randomstatestring123"
        }
        url = f"{base_url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
        print(url)
        return Response({'redirect-url':url})
    

class LinkedInCallback(APIView):
    def get(self, request):
        code = request.GET.get("code")

        token_url = "https://www.linkedin.com/oauth/v2/accessToken"
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": settings.LINKEDIN_REDIRECT_URI,
            "client_id": settings.LINKEDIN_CLIENT_ID,
            "client_secret": settings.LINKEDIN_CLIENT_SECRET,
        }

        response = requests.post(token_url, data=data)
        token_data = response.json()

        if "access_token" not in token_data:
            return Response(token_data, status=400)

        return Response({
            "token_data": token_data,
        }, status=status.HTTP_200_OK)
    

class LinkedInRefreshToken(APIView):
    def post(self, request):
        refresh_token = request.data.get("refresh_token")

        if not refresh_token:
            return Response({"error": "refresh_token is required"}, status=400)

        token_url = settings.LINKEDIN_BASE_URL + "oauth/v2/accessToken"
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": settings.LINKEDIN_CLIENT_ID,
            "client_secret": settings.LINKEDIN_CLIENT_SECRET,
        }

        response = requests.post(token_url, data=data)
        token_data = response.json()

        if "access_token" not in token_data:
            return Response(token_data, status=400)

        return Response({
            "token_data":token_data
        }, status=status.HTTP_200_OK)

