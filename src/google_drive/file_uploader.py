import os
import mimetypes
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from typing import List, Optional, Any


class FileUploader:
    def __init__(self, service: Any):
        if not service:
            raise ValueError("Service object cannot be None.")
        self.service = service

    def upload_file(
        self, local_file_path: str, folder_id: str, drive_filename: Optional[str] = None
    ) -> Optional[str]:

        if not os.path.exists(local_file_path):
            print(f"Local file not found: {local_file_path}")
            return None

        try:
            # If the Drive file name is not specified, take it from the local path
            if not drive_filename:
                drive_filename = os.path.basename(local_file_path)

            # 1. Define file metadata (name and parent folder)
            file_metadata = {"name": drive_filename, "parents": [folder_id]}

            # 2. Determine content type and create an upload object
            mimetype, _ = mimetypes.guess_type(local_file_path)
            media = MediaFileUpload(local_file_path, mimetype=mimetype, resumable=True)

            # 3. Execute the request to create (upload) the file
            uploaded_file = (
                self.service.files()
                .create(
                    body=file_metadata,
                    media_body=media,
                    fields="id",  # Request only the ID in the response for efficiency
                )
                .execute()
            )

            file_id = uploaded_file.get("id")
            print(f"File '{drive_filename}' successfully uploaded. ID: {file_id}")
            return file_id

        except HttpError as error:
            print(
                f"An API error occurred while uploading file '{local_file_path}': {error}"
            )
            return None

    def upload_multiple_files(
        self, local_file_paths: List[str], folder_id: str
    ) -> List[str]:
        """
        Uploads a list of local files to the specified folder ID on Google Drive.

        Args:
            local_file_paths: List of paths to local files.
            folder_id: ID of the folder on Drive.

        Returns:
            List of IDs of all successfully uploaded files.
        """

        uploaded_ids = []
        for path in local_file_paths:
            file_id = self.upload_file(local_file_path=path, folder_id=folder_id)
            if file_id:
                uploaded_ids.append(file_id)

        print(
            f"\nUpload complete. Successfully uploaded {len(uploaded_ids)} out of {len(local_file_paths)} files."
        )
        return uploaded_ids
