import logging
import io
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from utils import configure_logging

configure_logging()
logger = logging.getLogger(__name__)


class AudioDownloader:
    def __init__(self, service):
        self.service = service

    def download_file_in_memory(self, file_id: str) -> bytes | None:
        if not self.service:
            logger.error("Google Drive service is not initialized.")
            return None
        try:
            request = self.service.files().get_media(fileId=file_id)
            file_io_base = io.BytesIO()
            downloader = MediaIoBaseDownload(file_io_base, request)

            done = False
            while not done:
                status, done = downloader.next_chunk()
                logger.debug(
                    f"  Downloading file {file_id}: {int(status.progress() * 100)}%."
                )

            logger.info(f"File {file_id} successfully downloaded in memory.")
            return file_io_base.getvalue()

        except HttpError as error:
            logger.error(
                f"Unexpected API error occurred while downloading file {file_id}: {error}"
            )
            return None
