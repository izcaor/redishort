"""
YouTube API Authorization Script
--------------------------------
Simple OAuth flow - opens browser and asks for code manually.
Works with both Desktop and Web Application OAuth clients.
"""

import os
from pathlib import Path
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRETS_FILE = Path(os.getenv("YOUTUBE_SECRETS_FILE", "client_secret.json"))
TOKEN_FILE = Path("token.json")

if not CLIENT_SECRETS_FILE.exists():
    print(f"❌ Client secrets file not found: {CLIENT_SECRETS_FILE}")
    print("   Download it from Google Cloud Console and place it in project root.")
    exit(1)

print(f"\n{'='*60}")
print("   REDISHORT - YouTube Authorization")
print(f"{'='*60}\n")

# Create flow with out-of-band redirect (manual code entry)
flow = Flow.from_client_secrets_file(
    str(CLIENT_SECRETS_FILE),
    scopes=SCOPES,
    redirect_uri="urn:ietf:wg:oauth:2.0:oob"  # Special URI for manual code entry
)

auth_url, _ = flow.authorization_url(
    prompt="consent",
    access_type="offline",
    include_granted_scopes="true"
)

print("1. Open this URL in your browser:\n")
print(auth_url)
print("\n2. Login and authorize the application")
print("3. Copy the authorization code that appears")
print()

# Ask for code manually
auth_code = input("4. Paste the authorization code here: ").strip()

if not auth_code:
    print("\n❌ No code provided. Authorization cancelled.")
    exit(1)

try:
    flow.fetch_token(code=auth_code)
    creds = flow.credentials

    # Ensure the file has secure permissions if it already exists
    if TOKEN_FILE.exists():
        os.chmod(TOKEN_FILE, 0o600)
    # Securely open the file so only the owner can read/write
    fd = os.open(TOKEN_FILE, os.O_CREAT | os.O_WRONLY | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as token:
        token.write(creds.to_json())

    print(f"\n✅ Credentials saved successfully to {TOKEN_FILE}")
    print("   You can now run the bot with: docker-compose up -d")

except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nTry these fixes:")
    print("1. Make sure you're using the correct Google account")
    print("2. Copy the FULL authorization code")
    print("3. Run auth.py again")
