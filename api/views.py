import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class LinkedInAdAccountsAPIView(APIView):
    def get(self, request):
        access_token = request.data.get("access_token")
        if not access_token:
            return Response({"error": "Missing access_token"}, status=400)

        url = "https://api.linkedin.com/rest/adAccounts?q=search&search=(type:(values:List(BUSINESS)),status:(values:List(ACTIVE,CANCELED)))"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "LinkedIn-Version": settings.LINKEDIN_VERSION,
            "X-Restli-Protocol-Version": "2.0.0",
        }
        params = {
            "q": "search",
            "search": "(type:(values:List(BUSINESS)),status:(values:List(ACTIVE,CANCELED)))",
            # "sort":"(field:ID,order:DESCENDING)"
            # "fields": "id,name,test,reference"
        }

        response = requests.get(url, headers=headers)
        data = response.json()
        print(data)

        if response.status_code != 200:
            return Response(data, status=response.status_code)

        return Response(data, status=200)
