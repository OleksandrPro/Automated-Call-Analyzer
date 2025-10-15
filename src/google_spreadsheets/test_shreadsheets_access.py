import gspread
from constants import ConfigFiles
from utils import create_full_path


def test_cell_access(sheet_name: str, cell: str):

    worksheet = get_worksheet(sheet_name, ConfigFiles.CREDENTIALS)

    return worksheet.get(cell)


def get_worksheet(sheet_name: str, credentials_path: str):
    gc = gspread.service_account(filename=credentials_path)

    spreadsheet = gc.open(sheet_name)
    worksheet = spreadsheet.sheet1

    return worksheet
