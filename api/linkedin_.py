import requests
from django.conf import settings
from datetime import datetime, date
import re
from api.models import (
    Country, 
    CampaignLinkendin, 
    CreativeLinkedin, 
    AdAnalyticsLinkedin, 
    Seniority, 
    JobTitle, 
    StaffCountRange,
    Industry
)
CUSTOMER_ID = 512626204

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
    # print(token_data.get("access_token"))
    return token_data.get("access_token")

# def get_active_campaigns():


def get_linkedin_ad_analytics():
    try:
        auth = get_auth_token()
        time_granularity = 'ALL'
        start_date = None
        end_date = None
        account = CUSTOMER_ID

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
            f'&dateRange=(start:(year:2025,month:08,day:1))'
            f'&accounts={accounts_param}'
            f'&fields=clicks,impressions,pivotValues,dateRange'
        )

        headers = {
            'Authorization': f'Bearer {auth}',
            'Linkedin-Version': '202411',
            'X-Restli-Protocol-Version': '2.0.0',
        }

        response = requests.get(linkedin_url, headers=headers)
        # print(response.json())
        if response.status_code == 200:
            return response.json().get("elements")
        else:
            print(f"Error: {response.status_code} - {response.json()}")
            return None    
    except Exception as e:
        print(f"Error fetching LinkedIn ad analytics: {str(e)}")

def flatten_targeting_criteria(data):
    flattened = {}

    include = data.get("include", {})
    include_groups = include.get("and", [])

    for or_condition in include_groups:
        or_block = or_condition.get("or", {})
        for facet, values in or_block.items():
            key = facet.split(":")[-1]
            if key not in flattened:
                flattened[key] = []
            flattened[key].extend(values)

    return flattened

def get_campaign_details(campaign_id, account_id, auth):
    try:
        linkedin_url = f'https://api.linkedin.com/rest/adAccounts/{account_id}/adCampaigns/{campaign_id}'
        headers = {
            'Authorization': f'Bearer {auth}',
            'Linkedin-Version': '202411',
            'X-Restli-Protocol-Version': '2.0.0',
        }

        response = requests.get(linkedin_url, headers=headers)
        if response.status_code == 200:
            return response.json()
        if response.status_code in [401, 403]:
            auth = get_auth_token()
            get_campaign_details(campaign_id, account_id, auth)
            return None
        else:
            print(f"Error: {response.status_code} - {response.json()}")
            return None
    except Exception as e:
        print(f"Error fetching LinkedIn campaign details: {str(e)}")

def get_creative_details(creative_id, account_id, auth):
    try:
        linkedin_url = f'https://api.linkedin.com/rest/adAccounts/{account_id}/creatives/urn%3Ali%3AsponsoredCreative%3A{creative_id}'
        headers = {
            'Authorization': f'Bearer {auth}',
            'Linkedin-Version': '202411'
        }

        response = requests.get(linkedin_url, headers=headers)
        if response.status_code == 200:
            # print(response.json())
            return response.json()
        if response.status_code in [401, 403]:
            auth = get_auth_token()
            get_creative_details(creative_id, account_id, auth)
            return None
        else:
            print(f"Error: {response.status_code} - {response.json()}")
            return None
    except Exception as e:
        print(f"Error fetching LinkedIn campaign details: {str(e)}")

def get_title(id,auth):
    try:
        linkedin_url = f'https://api.linkedin.com/v2/titles/{id}?locale=en_US'
        headers = {
            'Authorization': f'Bearer {auth}'
        }
        response = requests.get(linkedin_url, headers=headers)
        return response.json().get("name").get("localized").get("en_US") if response.status_code == 200 else None
    except Exception as e:
        print(f"Error fetching job title: {str(e)}")
        return None
    
def get_industry(id,auth):
    try:
        linkedin_url = f'https://api.linkedin.com/v2/industries/{id}?locale.language=en&locale.country=US'
        headers = {
            'Authorization': f'Bearer {auth}'
        }
        response = requests.get(linkedin_url, headers=headers)
        return response.json().get("name").get("localized").get("en_US") if response.status_code == 200 else None
    except Exception as e:
        print(f"Error fetching job title: {str(e)}")
        return None

def get_seniority(id,auth):
    try:
        linkedin_url = f'https://api.linkedin.com/v2/seniorities/{id}?locale.language=en&locale.country=US'
        headers = {
            'Authorization': f'Bearer {auth}'
        }
        response = requests.get(linkedin_url, headers=headers)
        return response.json().get("name").get("localized").get("en_US") if response.status_code == 200 else None
    except Exception as e:
        print(f"Error fetching job seniority: {str(e)}")
        return None

def get_country(id,auth):
    try:
        linkedin_url = f'https://api.linkedin.com/v2/geo/{id}'
        headers = {
            'Authorization': f'Bearer {auth}'
        }
        response = requests.get(linkedin_url, headers=headers)
        return response.json().get("defaultLocalizedName").get("value") if response.status_code == 200 else None
    except Exception as e:
        print(f"Error fetching job country: {str(e)}")
        return None

def create_date(date_):
    if not date_:
        return None
    return date(year=date_.get('year'), month=date_.get('month'), day=date_.get('day'))

def linkedin_ad_analytics():
    data = get_linkedin_ad_analytics()
    auth = get_auth_token()
    if not data:
        print("No data fetched from LinkedIn.")
        return
    print("Total data fetched",len(data))
    data__ = []
    for i in range(0,len(data)):
        # print(data[i])
        print('_' * 25)
        pivot_values = data[i].get("pivotValues", [])
        campaign_id = pivot_values[1].split(":")[-1] if len(pivot_values) > 1 else "Unknown"

        creative_id = pivot_values[0].split(":")[-1] if len(pivot_values) > 0 else "Unknown"
        campaign_data = get_campaign_details(campaign_id, CUSTOMER_ID, auth) if campaign_id != "Unknown" else None
        campaign_name = campaign_data.get('name') if campaign_data else ''
        if not campaign_data or campaign_data.get("status") != "ACTIVE":
            print("Campaign Status",campaign_data.get("status"))
            print(f"Skipping record {i} due to Campaign Status not Active.")
            continue
        # if campaign_data:
        #     campaign , _= CampaignLinkendin.objects.get_or_create(
        #         campaign_id=campaign_id,
        #         name = campaign_data.get("name")
        #     )
        # else:
        #     print(f"Skipping record {i} due to missing campaign ID.")
        #     continue
        creative_data = get_creative_details(creative_id, CUSTOMER_ID, auth) if creative_id != "Unknown" else None
        creative_name = creative_data.get('name') if creative_data else ''
        if not creative_data or creative_data.get("intendedStatus") != "ACTIVE":
            print("Creative Status",creative_data.get("status"))
            print(f"Skipping record {i} due to Creative Status not Active.")
            continue
        # if creative_data:
        #     creative , _= CreativeLinkedin.objects.get_or_create(
        #         campaign=campaign,
        #         creative_id=creative_id,
        #         name = creative_data.get("name")
        #     )
        # else:
        #     print(f"Skipping record {i} due to missing creative ID.")
        #     continue
        clicks = data[i].get("clicks", 0)
        impressions = data[i].get("impressions", 0)
        date_range = data[i].get("dateRange", {})
        if not pivot_values or not date_range:
            print(f"Skipping record {i} due to missing pivot values or date range.")
            continue
        device = pivot_values[2] or "Unknown"
        date = create_date(date_range.get("start"))
        targeting_criteria = flatten_targeting_criteria(campaign_data.get("targetingCriteria", {}))
        print(targeting_criteria)
        country = get_country_data(targeting_criteria.get("locations", []))
        job_title = get_jobtitle_data(targeting_criteria.get("titles", []))
        seniority = get_seniority_data(targeting_criteria.get("seniorities", []))
        industries = get_industry_data(targeting_criteria.get("industries", []))
        staff_range = get_staff_range_data(targeting_criteria.get("staffCountRanges", []))
        data__.append({
            'campaign_id':campaign_id,
            'campaign_name':campaign_name,
            'creative_id':creative_id,
            'creative_name':creative_name,
            'clicks':clicks,
            'impressions':impressions,
            'device':device,
            'country':country,
            'job_title':job_title,
            'seniority':seniority,
            'industries':industries,
            'staff_range':staff_range,
            'date':date
        }
        )
    return data__

def get_country_data(data):
    auth = get_auth_token()
    data_=[]
    for item in data:
        country_id = item.split(":")[-1]
        country_name = get_country(country_id, auth)

        if country_name:
            data_.append(country_name)
        else:
            print(f"Failed to fetch country for ID: {country_id}")
    return data_

def get_jobtitle_data(data):
    auth = get_auth_token()
    data_=[]
    for item in data:
        job_title_id = item.split(":")[-1]
        job_title_name = get_title(job_title_id, auth)

        if job_title_name:
            data_.append(job_title_name)
        else:
            print(f"Failed to fetch job title for ID: {job_title_id}")
    return data_

def get_seniority_data(data):
    auth = get_auth_token()
    data_ = []
    for item in data:
        seniority_id = item.split(":")[-1]
        seniority_name = get_seniority(seniority_id, auth)

        if seniority_name:
            data_.append(seniority_name)
        else:
            print(f"Failed to fetch seniority for ID: {seniority_id}")
    return data_

def get_industry_data(data):
    auth = get_auth_token()
    data_=[]
    for item in data:
        industry_id = item.split(":")[-1]
        industry_name = get_industry(industry_id, auth)

        if industry_name:
           data_.append(industry_name) 
        else:
            print(f"Failed to fetch industry for ID: {industry_name}")
    return data_

def get_staff_range_data(data):
    data_=[]
    for urn in data:
        match = re.search(r'\((\d+),(\d+)\)', urn)
        if match:
            min_val = int(match.group(1))
            max_val = int(match.group(2))
            data_.append(f'{min_val} - {max_val}')
    return data_