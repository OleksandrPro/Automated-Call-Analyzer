from googleapiclient.errors import HttpError
from typing import List, Dict, Any, Optional


class FileSearcher:
    """A universal class to find files and folders in Google Drive."""

    def __init__(self, service):
        """
        Initializes the searcher with an authenticated Google Drive service client.

        Args:
            service: An authorized Google Drive API service object.
        """
        if not service:
            raise ValueError("Service object cannot be None.")
        self.service = service

    def _query_executor(self, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Executes a generic '.list()' request against the Drive API using provided keyword arguments.
        This is the single, universal point of contact for all file listing requests.

        Args:
            **kwargs: Keyword arguments to be passed directly to the service.files().list() method.
                      Example: q="...", fields="...", pageSize=10

        Returns:
            The API response dictionary on success, None on failure.
        """
        try:
            # **kwargs unpacks the dictionary into named arguments for the list() method
            response = self.service.files().list(**kwargs).execute()
            return response
        except HttpError as error:
            print(f"An API error occurred with params {kwargs}: {error}")
            return None

    def get_folder_id(self, folder_name: str) -> Optional[str]:
        """
        Finds the ID of a folder by its name.
        """
        # Define the specific parameters for this query
        params = {
            "q": f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and trashed=false",
            "fields": "files(id, name)",
            "spaces": "drive",
        }

        response = self._query_executor(**params)

        if response:
            # TODO replace with pydantic
            files = response.get("files", [])
            if not files:
                print(f"Folder named '{folder_name}' not found.")
                return None

            folder_id = files[0]["id"]
            print(f"Found ID for folder '{folder_name}': {folder_id}")
            return folder_id

        return None

    def list_files_in_folder(self, folder_id: str) -> List[Dict[str, str]]:
        """
        Returns a simple list of files (id and name) from a folder.
        """
        params = {
            "q": f"'{folder_id}' in parents and trashed=false",
            "fields": "files(id, name)",
            "spaces": "drive",
        }

        response = self._query_executor(**params)

        if response:
            return response.get("files", [])

        return []

    def get_files_with_details(self, folder_id: str) -> List[Dict[str, Any]]:
        """
        NEW: Returns a detailed list of files from a folder, requesting more fields.
        This demonstrates the new flexibility of the query executor.
        """
        params = {
            "q": f"'{folder_id}' in parents and trashed=false",
            # We are now requesting more details about each file
            "fields": "files(id, name, createdTime, modifiedTime, mimeType, size)",
            "pageSize": 20,  # We can also control other parameters like pageSize
        }

        response = self._query_executor(**params)

        if response:
            return response.get("files", [])

        return []
