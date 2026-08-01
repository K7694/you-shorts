import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",   # pinned comments
    # Retention/impressions live in the ANALYTICS API, not the Data API.
    # Without this scope we can only see views and likes — while the
    # algorithm actually ranks on swipe-away and completion rate, so we
    # were optimising a proxy and could never tell WHY a video flopped.
    # Read-only. Adding it requires one re-auth (delete youtube_token.json,
    # run this script, update the YOUTUBE_TOKEN_JSON secret).
    "https://www.googleapis.com/auth/yt-analytics.readonly",
]
YOUTUBE_SECRETS_FILE = "client_secrets.json"
YOUTUBE_TOKEN_FILE = "youtube_token.json"

def authenticate():
    creds = None
    if os.path.exists(YOUTUBE_TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(YOUTUBE_TOKEN_FILE, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("\n🚨 A BROWSER WINDOW WILL OPEN NOW.")
            print("Please sign in with the Google Account for your YouTube channel.")
            flow = InstalledAppFlow.from_client_secrets_file(YOUTUBE_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=8090)
            
        with open(YOUTUBE_TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
            print("\n✅ SUCCESS: youtube_token.json created!")
    else:
        print("\n✅ Already authenticated!")

if __name__ == "__main__":
    authenticate()
