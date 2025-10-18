from googleapiclient.discovery import build
import gspread
from google_auth import authenticate_user  # Your existing authentication module


def setup_google_clients(scopes: list[str]):
    """
    Authenticates the user and creates clients for Google Drive and Google Sheets.
    """
    print("Starting user authentication process...")

    # Get user credentials ONCE
    user_credentials = authenticate_user(scopes)

    # Create service for Google Drive
    print("Creating Google Drive service...")
    drive_service = build("drive", "v3", credentials=user_credentials)
    print("Google Drive service ready.")

    # Create client for Google Sheets
    print("Creating gspread client...")
    gspread_client = gspread.authorize(user_credentials)
    print("gspread client ready.")

    return drive_service, gspread_client
