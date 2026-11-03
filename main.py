import requests
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign

# 1. Fetch live user records from your Bubble.io database URL
BUBBLE_DATABASE_URL = 'https://budgetguard-saas-test.bubbleapps.io/version-test/api/1.1/obj
BUBBLE_DATABASE_URL = 'https://YOUR_BUBBLE_APP_NAME.bubbleapps.io/version-test/api/1.1/obj/User_Ad_Account'

try:
    response = requests.get(BUBBLE_DATABASE_URL)
    users_data = response.json()['response']['results']
    print(f"Successfully retrieved {len(users_data)} client records from the database.")
except Exception as e:
    print(f"Failed to connect to Bubble database: {e}")
    users_data = []

# 2. Loop through every single e-commerce client registered on your website
for client in users_data:
    try:
        # Pull their individual credentials from your Bubble columns
        token = client.get('Meta_Access_Token')
        ad_id = client.get('Ad_Account_ID')
        spend_limit = float(client.get('Max_Spend_Limit', 500.0))
        client_name = client.get('Client_Name', 'Unknown Client')
        
        if not token or not ad_id:
            print(f"Skipping {client_name}: Missing token or account ID.")
            continue
            
        # Initialize the Meta API engine for this specific client
        FacebookAdsApi.init(access_token=token)
        account = AdAccount(ad_id)
        
        # Fetch their live campaigns
        campaigns = account.get_campaigns(fields=['id', 'name', 'status', 'insights'])
        
        for campaign in campaigns:
            # Check for budget bleeding against their custom slider choice!
            if campaign['status'] == 'ACTIVE' and campaign.get('insights'):
                insights_data = campaign['insights']['data'][0]
                spend = float(insights_data.get('spend', 0.0))
                clicks = int(insights_data.get('clicks', 0))
                
                print(f"Checking {client_name} -> Campaign: {campaign['name']} | Spent: ₹{spend} | Clicks: {clicks}")
                
                # Apply the slider limit rule
                if spend > spend_limit and clicks < 3:
                    # Execute the remote shutdown on Meta's servers instantly
                    campaign[Campaign.Field.status] = Campaign.Status.paused
                    campaign.remote_update()
                    print(f"🔒 CRITICAL SAVE: Paused bleeding ad for {client_name} (Saved money!)")
                    
    except Exception as e:
        print(f"Error processing client account: {e}")
