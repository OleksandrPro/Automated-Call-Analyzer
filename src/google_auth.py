import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from constants import ConfigFiles


def authenticate_user(
    scopes: list[str],
    token_path: str = ConfigFiles.TOKEN_FILE,
    client_secret_path: str = ConfigFiles.CLIENT_SECRET_FILE,
):
    """
    Performs user authentication via OAuth 2.0.
    On first launch, it opens a browser to get permission
    and creates a token.json file for subsequent launches.

    Returns:
        An authorized credentials object for use with the API.
    """
    creds = None
    # The token.json file stores the user's access and refresh tokens.
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, scopes)

    # If the credentials are invalid or missing, start the login process.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired token...")
            creds.refresh(Request())
        else:
            print("Starting user authentication process...")
            # Use client_secret.json to start the authentication flow
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, scopes)
            # Starts a local server to get the authorization code
            creds = flow.run_local_server(port=0)

        # Save credentials to token.json for the next launch
        with open(token_path, "w") as token:
            token.write(creds.to_json())
            print(f"Credentials saved to file '{token_path}'.")

    print("User authentication successful.")
    return creds


def create_drive_service(credentials: Credentials):
    service = build("drive", "v3", credentials=credentials)
    return service
