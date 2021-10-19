import pickle
import os.path
from googleapiclient import discovery
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload
import logging

from models.article import Article
from tools.variables import SPREADSHEET_ID, UPLOAD_FOLDER_ID, RANGE_NAME

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

def get_creds():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds

def open_sheet():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = get_creds()
    service = discovery.build('sheets', 'v4', credentials=creds, cache_discovery=False)

    # Call the Sheets API
    sheet = service.spreadsheets()
    return sheet

def get_value_rows(id=SPREADSHEET_ID, range=RANGE_NAME):
    sheet = open_sheet()

    try:
        result = sheet.values().get(
            spreadsheetId=id,
            range=range
        ).execute()
    except:
        logging.exception('Error getting rows. Is ID or range valid?')

    values = result.get('values', [])

    return values

"""
Returns articles from spreedsheet.
"""
def get_articles_from_sheet():
    values = get_value_rows()

    if not values:
        print('No data found.')
        result = []
    else:
        result = [
            Article(
                title=row[0],
                abstract=row[1],
                keywords=row[2],
                citations=row[3],
                pub_location=row[4],
                pub_year=row[5],
                pub_type=row[6],
                pub_url=row[7],
                drive_url=row[8],
                created_at=row[9],
                bibtex=row[10],
                gsrank=row[11],
                exclude=row[12] if len(row) > 12 else '',
                exclude_motive=row[13] if len(row) > 13 else ''
            ) for row in values
        ]

    return result

def insert_article_in_sheet(article):
    sheet = open_sheet()

    result = sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME,
        body=article.body(),
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS'
    ).execute()


def update_in_sheet(range, values, id=SPREADSHEET_ID):
    sheet = open_sheet()

    sheet.values().update(
        spreadsheetId=id,
        range=range,
        body={ 'values': values },
        valueInputOption='RAW'
    ).execute()


def upload_file(filename, filepath):
    creds = get_creds()

    service = discovery.build('drive', 'v3', credentials=creds, cache_discovery=False)

    file_metadata = {'name': filename, 'parents': [UPLOAD_FOLDER_ID]}
    media = MediaFileUpload(filepath, mimetype='application/pdf')
    uploaded_file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    return uploaded_file

def update_articles_in_sheet(articles, range=RANGE_NAME, id=SPREADSHEET_ID):
    rows = [article.to_row(include_pad=False) for article in articles]

    update_in_sheet(range, rows, id)
