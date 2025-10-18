import io
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload


class AudioDownloader:
    def __init__(self, service):
        self.service = service

    def download_file_in_memory(self, file_id: str) -> bytes | None:
        if not self.service:
            return None
        try:
            request = self.service.files().get_media(fileId=file_id)
            file_io_base = io.BytesIO()
            downloader = MediaIoBaseDownload(file_io_base, request)

            done = False
            while not done:
                status, done = downloader.next_chunk()
                print(f"  Downloading file {file_id}: {int(status.progress() * 100)}%.")

            print(f"File {file_id} successfully downloaded in memory.")
            return file_io_base.getvalue()

        except HttpError as error:
            print(f"Unexpected API error occurred while downloading file: {error}")
            return None
