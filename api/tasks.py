import requests
from django.conf import settings

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
    print(token_data.get("access_token"))
    return token_data.get("access_token")

def get_linkedin_ad_analytics():
    try:
        auth = get_auth_token()
        time_granularity = 'ALL'
        start_date = None
        end_date = None
        account = '504692795'

        accounts_param = f"List(urn%3Ali%3AsponsoredAccount%3A{account})"

        if start_date:
            start_date_range_param = f"start:(year:{start_date.get('year')},month:{start_date.get('month')},day:{start_date.get('day')})"
        if end_date:
            end_date_range_param = f"end:(year:{end_date.get('year')},month:{end_date.get('month')},day:{end_date.get('day')})"

        date_range_param = f"({start_date_range_param})" if start_date else (f"({end_date_range_param})" if end_date else (f"({start_date_range_param},{end_date_range_param})" if start_date and end_date else ""))

        linkedin_url = (
            f'https://api.linkedin.com/rest/adAnalytics'
            f'?q=statistics'
            f'&pivots=List(CREATIVE,CAMPAIGN,IMPRESSION_DEVICE_TYPE)'
            f'&timeGranularity={time_granularity}'
            f'&dateRange=(start:(year:2021,month:1,day:1))'
            f'&accounts={accounts_param}'
            f'&fields=clicks,impressions,pivotValues,dateRange'
        )

        headers = {
            'Authorization': f'Bearer {auth}',
            'Linkedin-Version': '202411',
            'X-Restli-Protocol-Version': '2.0.0',
        }

        response = requests.get(linkedin_url, headers=headers)
        
        return(response.json())
        
    except Exception as e:
        print(f"Error fetching LinkedIn ad analytics: {str(e)}")
