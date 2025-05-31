from django.shortcuts import get_object_or_404
import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.models import Campaign, CampaignChangeLog, AdAnalyticsLinkedin
from api.serializers import CampaignSerializer
from deepdiff import DeepDiff
from django.db.models import Q, Sum, F

class LinkedInAdAccountsAPIView(APIView):
    def get(self, request):
        try:
            access_token = request.headers.get('Authorization')
            if not access_token:
                return Response({'error': 'Authorization header missing.'}, status=status.HTTP_401_UNAUTHORIZED)

            url = "https://api.linkedin.com/rest/adAccounts?q=search&search=(type:(values:List(BUSINESS)),status:(values:List(ACTIVE,CANCELED)))"
            headers = {
                "Authorization": access_token,
                "LinkedIn-Version": settings.LINKEDIN_VERSION,
                "X-Restli-Protocol-Version": "2.0.0",
            }
            # params = {
            #     "q": "search",
            #     "search": "(type:(values:List(BUSINESS)),status:(values:List(ACTIVE,CANCELED)))",
            #     "sort":"(field:ID,order:DESCENDING)",
            #     "fields": "id,name,test,reference"
            # }

            response = requests.get(url, headers=headers)
            data = response.json()
            print(data)

            if response.status_code != 200:
                return Response(data, status=response.status_code)

            return Response(data, status=200)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)



class LinkedInAdAnalyticsView(APIView):
    def post(self, request):
        try:
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return Response({'error': 'Authorization header missing.'}, status=status.HTTP_401_UNAUTHORIZED)

            linkedin_version = request.headers.get('Linkedin-Version', '202411')

            time_granularity = request.data.get('timeGranularity', 'DAILY')
            start_date = request.data.get('start_date', None)
            end_date = request.data.get('end_date', None)
            account = request.data.get('account', None)

            if not account:
                return Response({'error': 'account id must be provided '}, status=status.HTTP_400_BAD_REQUEST)
            if not start_date or not isinstance(start_date, dict) or not end_date or not isinstance(end_date, dict):
                return Response({'error': 'start date or end date must be provided as a dictionary with year, month, and day.'}, status=status.HTTP_400_BAD_REQUEST)

            accounts_param = f"List(urn%3Ali%3AsponsoredAccount%3A{account})"

            if start_date:
                start_date_range_param = f"start:(year:{start_date.get('year')},month:{start_date.get('month')},day:{start_date.get('day')})"
            if end_date:
                end_date_range_param = f"end:(year:{end_date.get('year')},month:{end_date.get('month')},day:{end_date.get('day')})"
            
            # if start_date:
            #     date_range_param = f"({start_date_range_param})"
            # elif end_date:
            #     date_range_param = f"({end_date_range_param})"
            # elif start_date and end_date:
            #     date_range_param = f"({start_date_range_param},{end_date_range_param})"

            date_range_param = f"({start_date_range_param})" if start_date else (f"({end_date_range_param})" if end_date else (f"({start_date_range_param},{end_date_range_param})" if start_date and end_date else ""))

            linkedin_url = (
                f'https://api.linkedin.com/rest/adAnalytics'
                f'?q=statistics'
                f'&pivots=List(CREATIVE,CAMPAIGN,IMPRESSION_DEVICE_TYPE)'
                f'&timeGranularity={time_granularity}'
                f'&dateRange={date_range_param}'
                f'&accounts={accounts_param}'
                f'&fields=clicks,impressions,pivotValues,dateRange'
            )

            headers = {
                'Authorization': auth_header,
                'Linkedin-Version': linkedin_version,
                'X-Restli-Protocol-Version': '2.0.0',
            }

            response = requests.get(linkedin_url, headers=headers)

            if response.status_code == 200:
                return Response(response.json().get("elements"), status=response.status_code)
            else:
                return Response({'error': response.json()}, status=response.status_code)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LinkedinCampaignAPIView(APIView):
    def post(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return Response({'error': 'Authorization header missing.'}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = CampaignSerializer(data=request.data)
        if serializer.is_valid():
            campaign = serializer.save()
            return Response({"message": "Campaign created", "id": campaign.campaign_id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        campaign = get_object_or_404(Campaign, pk=pk)
        old_data = CampaignSerializer(campaign).data

        serializer = CampaignSerializer(campaign, data=request.data)
        if serializer.is_valid():
            serializer.save()

            new_data = serializer.data
            diff = DeepDiff(old_data, new_data, ignore_order=True).to_dict()

            CampaignChangeLog.objects.create(
                campaign=campaign,
                # changed_by=request.user.username if request.user.is_authenticated else "system",
                data=new_data,
                changes=diff
            )

            return Response(new_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return Response({'error': 'Authorization header missing.'}, status=status.HTTP_401_UNAUTHORIZED)
        linkedin_version = request.headers.get('Linkedin-Version', '202411')
        account_id = request.GET.get('account_id')
        headers = {
            'Authorization': auth_header,
            'Linkedin-Version': linkedin_version,
            'X-Restli-Protocol-Version': '2.0.0',
        }
        url = f"https://api.linkedin.com/rest/adAccounts/{account_id}/adCampaigns?q=search&search=(status:(values:List(ACTIVE)))&sortOrder=DESCENDING"
        # response = requests.get(linkedin_url, headers=headers)


class LinkedinStatisticsAPIView(APIView):
    FILTER_MAP = {
        'device': 'device__iexact',
        'date_from': 'date__gte',
        'date_to': 'date__lte',
        'campaign_name': 'creative__campaign__name__icontains',
        'creative_name': 'creative__name__icontains',
        'min_clicks': 'clicks__gte',
        'max_clicks': 'clicks__lte',
        'min_impressions': 'impressions__gte',
        'max_impressions': 'impressions__lte',
        'seniority': 'creative__seniorities__name__icontains',
        'job_title': 'creative__job_titles__name__icontains',
        'country': 'creative__countries__name__icontains',
        'industry': 'creative__industries__name__icontains',
        'staff_min': 'creative__staff_count_range__min_value__gte',
        'staff_max': 'creative__staff_count_range__max_value__lte',
    }

    def get(self, request):
        queryset = AdAnalyticsLinkedin.objects.select_related('creative__campaign')

        filters = Q()
        for param, value in request.GET.items():
            if not value:
                continue
            filter_field = self.FILTER_MAP.get(param)
            if filter_field:
                filters &= Q(**{filter_field: value})

        filtered_qs = queryset.filter(filters)

        data = (
            filtered_qs
            .values('creative__campaign__name','creative__name','device')
            .annotate(
                total_clicks=Sum('clicks'),
                total_impressions=Sum('impressions'),
            )
            .order_by('date')
        )
        data = list(data)

        return Response({"table_data": data}, status=status.HTTP_200_OK)        