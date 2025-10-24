import logging
import os.path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from constants import ConfigFiles
from google_drive.components_creator import GoogleComponentCreator
from utils import configure_logging

configure_logging()
logger = logging.getLogger(__name__)


class GoogleServicesProvider:
    def __init__(self, scopes: list[str]):
        self._scopes = scopes
        self._auth = GoogleAuth(scopes=self._scopes)
        self._creator = GoogleComponentCreator()
        self.drive_service = None
        self.gspread_client = None

    def get_clients(self) -> tuple:

        if self.drive_service and self.gspread_client:
            logger.info("Returning cached Google clients.")
            return self.drive_service, self.gspread_client

        logger.info("Setting up Google clients...")

        user_credentials = self._auth.get_credentials()

        logger.info("Creating Google Drive service...")
        self.drive_service = self._creator.create_drive_service(
            credentials=user_credentials
        )
        logger.info("Google Drive service is ready.")

        logger.info("Creating gspread client...")
        self.gspread_client = self._creator.create_gspread_client(user_credentials)
        logger.info("gspread client is ready.")

        return self.drive_service, self.gspread_client


class GoogleAuth:
    def __init__(
        self,
        scopes: list[str],
        token_path: str = ConfigFiles.TOKEN_FILE,
        client_secret_path: str = ConfigFiles.CLIENT_SECRET_FILE,
    ):
        self._scopes = scopes
        self._token_path = token_path
        self._client_secret_path = client_secret_path

    def _save_credentials(self, creds: Credentials):
        with open(self._token_path, "w") as token:
            token.write(creds.to_json())
            logger.info(f"Credentials saved to file '{self._token_path}'.")

    def _authenticate_user(self) -> Credentials:
        """
        Performs user authentication via OAuth 2.0.
        On the first run, it opens a browser to obtain permission
        and creates a token.json file for subsequent runs.
        """
        creds = None
        # The token.json file stores the user's access and refresh tokens.
        if os.path.exists(self._token_path):
            creds = Credentials.from_authorized_user_file(
                self._token_path, self._scopes
            )

        # If credentials are not valid or are missing, start the login process.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("Refreshing expired token...")
                creds.refresh(Request())
            else:
                logger.info("Starting user authentication process...")
                # Use client_secret.json to start the authentication flow
                flow = InstalledAppFlow.from_authorized_user_file(
                    self._client_secret_path, self._scopes
                )
                # Starts a local server to receive the authorization code
                creds = flow.run_local_server(port=0)

            # Save the new or refreshed credentials
            self._save_credentials(creds)

        logger.info("User authentication was successful.")
        return creds

    def get_credentials(self) -> Credentials:
        """
        Main public method.
        Gets (or refreshes) user credentials and returns them.
        """
        # _authenticate_user already handles getting, refreshing AND saving
        creds = self._authenticate_user()
        return creds
