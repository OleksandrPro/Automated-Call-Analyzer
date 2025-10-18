from googleapiclient.discovery import build
from google.oauth2 import service_account
from google.auth.credentials import Credentials as AuthCredentials
from google.oauth2.credentials import Credentials as Oauth2credentials


class ComponentCreator:
    def __init__(self):
        pass

    def create_credantials(self, credentials_path: str, scopes: list[str]):
        try:
            creds = service_account.Credentials.from_service_account_file(
                credentials_path, scopes=scopes
            )
            print("Authentication to Google Drive successful.")
            return creds
        except FileNotFoundError:
            print(f"Error: Credentials file not found at path '{credentials_path}'.")
            return None

    def create_service(self, credentials: AuthCredentials | Oauth2credentials):
        service = build("drive", "v3", credentials=credentials)
        return service
