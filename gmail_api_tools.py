import re
import base64
import os.path
import pandas as pd

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

__author__ = 'Rahul I. Patel, PhD'

# If modifying these scopes, delete the file token.json.
# Check out more scopes here:
# https://developers.google.com/identity/protocols/oauth2/scopes

SCOPES = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/spreadsheets.readonly',
          'https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/gmail.send',
          'https://www.googleapis.com/auth/drive.file',
          'https://www.googleapis.com/auth/gmail.labels',
          'https://www.googleapis.com/auth/gmail.compose',
          'https://www.googleapis.com/auth/gmail.modify',
          'https://www.googleapis.com/auth/drive.activity',
          'https://mail.google.com/',
          'https://www.googleapis.com/auth/contacts.readonly',
          'https://www.googleapis.com/auth/drive.metadata.readonly',
          'https://www.googleapis.com/auth/gmail.addons.current.action.compose',
          'https://www.googleapis.com/auth/gmail.addons.current.message.action',
          ]


def create_token():
    """
    Obtains user credentials for Google API access and saves them for future use.

    This function performs the following steps:
    1. Checks if a file named 'token.json' exists in the current directory.
       This file stores the user's access and refresh tokens.
    2. If 'token.json' exists, the function loads the credentials from the file.
    3. If the credentials are not available, invalid, or expired, the function refreshes
       the credentials using the refresh token if available.
    4. If the credentials cannot be refreshed, the function initiates the OAuth 2.0 authorization
       flow to obtain new credentials from the user.
    5. Saves the obtained credentials to 'token.json' for future use.

    Returns:
        Credentials: The obtained or refreshed user credentials.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is created automatically when the authorization flow completes for the first time.
    google_token = 'tokens/google_token.json'
    google_credentials = 'tokens/credentials.json'

    if os.path.exists(google_token):
        creds = Credentials.from_authorized_user_file(google_token, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(google_credentials, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds


def create_message(sender, bcc, subject, html_content,
                   attach_file_names=None,
                   to='',sender_name=''):
    """
    Create an encoded message dictionary that can be sent through Gmail
    with the Gmail API

    Args:
        sender: (str) email address of sender
        bcc: (str) email address(es) to include in bcc block.
         Separate multiple emails by comma in same string
        subject: (str) subject line
        html_content: (doc string) body of email message in html format
        attach_file_names: (list/optional) list of file names to attach to email
        to: (str, optional) email address to include in to block
        sender_name (str, optional): Display name of the sender. Defaults to empty string.

    Returns:
        encoded message in dictionary
    """
    message = MIMEMultipart('resumable')
    message['To'] = to
    message['From'] = f'{sender_name} <{sender}>'
    message['Subject'] = subject
    message['bcc'] = bcc
    msg = MIMEText(html_content, 'html')
    message.attach(msg)

    if attach_file_names:
        for file_attach in attach_file_names:
            with open(file_attach, 'rb') as f:
                mime_base = MIMEBase('application', 'octet-stream')
                mime_base.set_payload(f.read())
                encoders.encode_base64(mime_base)
                mime_base.add_header('Content-Disposition',
                                     'attachment', filename=file_attach)
                message.attach(mime_base)

    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    return {'raw': encoded_message}


class GmailAPI:

    def __init__(self):

        self.creds = create_token()
        # INITIALIZE APIS
        # Initialize the Gmail API
        self.service_gmail = build('gmail', 'v1',
                                   credentials=self.creds)
        # Initialize the People API
        self.service_people = build('people', 'v1',
                                    credentials=self.creds)
        # Initialize google Drive Service
        self.service_drive = build('drive', 'v3',
                                   credentials=self.creds)
        # Initialize google sheets service
        self.service_sheets = build('sheets', 'v4',
                                    credentials=self.creds)

        # THIS HELPS TO SUPPRESS OATH SCOPE CHANGE WARNINGS
        # https://stackoverflow.com/questions/51499034/google-oauthlib-scope-has-changed
        # os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

    def get_emails_by_label(self, label_id):
        """
        Get email addresses from account using
        labels already established for contacts in gmail account.
        Not working the way I want it to.
        Args:
            label_id:

        Returns:

        """
        # Get a list of messages with the specified label
        results = self.service_gmail.users().messages().list(userId='me', labelIds=[label_id]).execute()
        messages = results.get('messages', [])

        emails = []
        for message in messages:
            msg = self.service_gmail.users().messages().get(userId='me', id=message['id']).execute()
            email_data = {
                'id': msg['id'],
                'snippet': msg['snippet'],
                'payload': msg['payload']
            }
            emails.append(email_data)

        return emails

    def list_labels(self):
        """
        Return list of labels in google contacts.

        Returns:
            list of labels

        """
        results = self.service_gmail.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        for label in labels:
            print(f'Label: {label["name"]}, ID: {label["id"]}')
        return labels

    def get_contacts_gmail(self):
        """
        Get all emails from contacts in gmail account.

        Returns:
            list of contacts
        """
        results = self.service_people.people().connections().list(
            resourceName='people/me',
            pageSize=100,
            personFields='names,emailAddresses').execute()
        connections = results.get('connections', [])

        contacts = []
        for person in connections:
            # names = person.get('names', [])
            email_addresses = person.get('emailAddresses', [])
            # if names and email_addresses:
            if email_addresses:
                # name = names[0].get('displayName')
                email = email_addresses[0].get('value')
                contacts.append(email)
                # contacts.append((name, email))
        if not contacts:
            print('No gmail contacts. List is empty')

        return contacts

    def get_all_sheets(self):
        """
        Get the names, IDs, and urls of all the Google sheets in your
        Google Drive.

        Returns:
            dictionary with sheet names, url, and sheet id {'[name]':{'url':..., 'id':...}...}
        """
        query = "mimeType='application/vnd.google-apps.spreadsheet'"

        # Call the Drive API to list files
        results = self.service_drive.files().list(q=query, fields="files(id, name)").execute()
        items = results.get('files', [])
        sheets_part_addy = 'https://docs.google.com/spreadsheets/d/'
        sheets_info = {}
        if not items:
            print('No sheet files found. Dictionary is Empty')
        else:
            for item in items:
                sheets_info[item['name']] = {'url': f"{sheets_part_addy}{item['id']}/edit",
                                             'id': item['id']}

        return sheets_info

    def get_contacts_sheets(self, find_regex):
        """
        Get the email addresses of all the contacts in
        a given sheet.
        todo: remove service drive when it turns into a class
        Args:
            find_regex: (str) Regex expression to use to search for the
             right Google sheet

        Returns:
            Single column pandas dataframe of email addresses in the Google sheet
        """
        regex = re.compile(find_regex, re.IGNORECASE)
        sheets_info_dict = self.get_all_sheets()
        try:
            name_of_email_sheet = list(filter(regex.match,
                                              sheets_info_dict.keys()))[0]
        except:
            name_of_email_sheet = None
            print(f'Could not find sheet with regex: {find_regex}')
            print('Reason unknown')

        sheet = self.service_sheets.spreadsheets()
        spreadsheet_id = sheets_info_dict[name_of_email_sheet]['id']
        sheet_range = '!A:Z'
        result = sheet.values().get(spreadsheetId=spreadsheet_id,
                                    range=sheet_range).execute()
        values = result.get('values', [])
        if not values:
            print('no data found')

        df = pd.DataFrame(values[1:], columns=values[0][0:-1])
        sheet_emails = df['Email Address']

        return sheet_emails

    def send_message(self, user_id, message):
        """
        Send a message through gmail.
        Args:
            user_id: (str) user id for email address of mailbox that you're accessing. use "me" for
             current authenticated user.
            message: (dict) dictionary with encoded message under key "raw"

        Returns:

        """
        try:

            message = self.service_gmail.users().messages().send(userId=user_id,
                                                                 body=message).execute()
            print(f'Message Id: {message['id']}')
            return message
        except Exception as error:
            print(f'An error occurred: {error}')
