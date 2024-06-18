import glob
import base64
import os.path

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
# from email.message import EmailMessage
# from googleapiclient.errors import HttpError

event_day = 'THURS.'
event_month = 'June'
event_date = '27th'
event_edition = 'Summer Solstice Edition'
location = 'Jackalope Brewing – Tap Room'
speaker1_name = 'Dr. Chayan Chatterjee'
speaker1_title = 'Listening to the Cosmic Orchestra Using A.I.'
speaker2_name = 'Dr. Aaron Stemo'
speaker2_title = 'Black Holes Don\'t Suck'
eventbrite_link = 'https://www.eventbrite.com'
other_news = ''  # additional messages

html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Astronomy on Tap - {event_edition}</title>
</head>
<body>
    <p>Dear AoT-ers!</p>
    <p>We are pleased to announce that our <strong>{event_edition}</strong> event for
    Astronomy on Tap will be held on <strong>{event_day} {event_month} {event_date}</strong> at the <strong>{location}</strong>!</p>
    <p>This event will feature 2 amazing speakers:</p>
    <ul>
        <li><strong>{speaker1_name}</strong><br><em>{speaker1_title}</em></li>
        <li><strong>{speaker2_name}</strong><br><em>{speaker2_title}</em></li>
    </ul>
    <p>There will be trivia and more prizes after! So come on out after a long day of hard work in the middle of the week and relax while we bombard you with fun astro facts, beer, and prizes!</p>
    <p>Make sure to <a href="{eventbrite_link}" target="_blank">RSVP for the free event at EventBrite</a>.</p>
    <p>Please share to all and any who might be interested!</p>
    <p><strong>Doors 7pm | Show 7:30 pm</strong></p>
    <p><a href="https://www.google.com/maps/place/Jackalope+Brewing" target="_blank">Parking Instructions</a></p>
    <p>{other_news}</p>
    <p>If you wish to unsubscribe, reply to this email</p>
    <p>Sincerely,
    <br>AoT Nashville Team</p>
<br>
<div>
    <div style="text-align:center; color:rgb(34,34,34)">
        <img data-aii="CiExR3hhR1hFMERrVm9idFl0QWRzUWZ3SGhSemtIU0dGZ0I" width="96" height="96" 
             src="https://ci3.googleusercontent.com/mail-sig/AIorK4wR7MgccJn6Wi3LFcw0z4QsBsos9nAKfBYh9BxpNHb006gIZIZwnz_hNMZQFongZ6f5_uEHKaQ" 
             data-os="https://lh3.googleusercontent.com/d/1GxaGXE0DkVobtYtAdsQfwHhRzkHSGFgB">
        <br>
    </div>
    <div style="text-align:center; color:rgb(34,34,34)">
        Astronomy on Tap - Nashville
    </div>
    <div style="text-align:center; color:rgb(34,34,34)">
        <b>
            <a href="https://www.instagram.com/aotnashville/" style="color:rgb(17,85,204)" target="_blank">Instagram</a>&nbsp;|&nbsp;
            <a href="https://www.facebook.com/aotnashville" target="_blank">Facebook</a>
        </b>
    </div>
</div>

</body>
</html>
"""

# todo: get list_labels to work - results line throws 403 error

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets',
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

# THIS HELPS TO SUPPRESS OATH SCOPE CHANGE WARNINGS
# https://stackoverflow.com/questions/51499034/google-oauthlib-scope-has-changed
# os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'


def get_emails_by_label(service, label_id):
    """
    Get email addresses from account using
    labels already established for contacts in gmail account.
    Not working the way I want it to.
    Args:
        service:
        label_id:

    Returns:

    """
    # Get a list of messages with the specified label
    results = service.users().messages().list(userId='me', labelIds=[label_id]).execute()
    messages = results.get('messages', [])

    emails = []
    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        email_data = {
            'id': msg['id'],
            'snippet': msg['snippet'],
            'payload': msg['payload']
        }
        emails.append(email_data)

    return emails

def list_labels(service):
    """
    Return list of labels in google contacts.
    Args:
        service: (api client) google apie client object [googleapiclient.discovery.Resource]

    Returns:
        list of labels

    """
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])
    for label in labels:
        print(f'Label: {label["name"]}, ID: {label["id"]}')
    return labels
def get_contacts(service):
    """
    Get all contacts from gmail account
    Args:
        service: (api client) google apie client object [googleapiclient.discovery.Resource]

    Returns:
        list of contacts
    """
    results = service.people().connections().list(
        resourceName='people/me',
        pageSize=100,
        personFields='names,emailAddresses').execute()
    connections = results.get('connections', [])

    contacts = []
    for person in connections:
        # names = person.get('names', [])
        email_addresses = person.get('emailAddresses', [])
        #if names and email_addresses:
        if email_addresses:
            #name = names[0].get('displayName')
            email = email_addresses[0].get('value')
            contacts.append(email)
            # contacts.append((name, email))

    return contacts


def create_message(sender, bcc, subject, html_content,
                   attach_file_names=None,
                   to=''):
    """

    Args:
        sender: (str) email address of sender
        bcc: (str) email address(es) to include in bcc block.
         Separate multiple emails by comma in same string
        subject: (str) subject line
        html_content: (doc string) body of email message in html format
        attach_file_name: (list/optional) list of file names to attach to email
        to: (str/optional) email address to include in to block

    Returns:
        encoded message in dictionary
    """
    message = MIMEMultipart('resumable')
    message['To'] = to
    message['From'] = sender
    message['Subject'] = subject
    message['bcc'] = bcc
    msg = MIMEText(html_content, 'html')
    message.attach(msg)

    if attach_file_names:
        for file_attach in attach_file_names:
            with open(file_attach,'rb') as f:
                mime_base = MIMEBase('application','octet-stream')
                mime_base.set_payload(f.read())
                encoders.encode_base64(mime_base)
                mime_base.add_header('Content-Disposition',
                                     'attachment',filename=file_attach)
                message.attach(mime_base)


    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    return {'raw': encoded_message}

def send_message(service, user_id, message):
    """

    Args:
        service: (api client) google apie client object [googleapiclient.discovery.Resource]
        user_id: (str) user id for email address of mailbox that you're accessing. use "me" for
         current authenticated user.
        message: (dict) dictionary with encoded message under key "raw"

    Returns:

    """
    try:

        message = service.users().messages().send(userId=user_id, body=message).execute()
        print(f'Message Id: {message['id']}')
        return message
    except Exception as error:
        print(f'An error occurred: {error}')

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
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def main():
    creds = create_token()
    # Initialize the Gmail API
    service_gmail = build('gmail', 'v1', credentials=creds)
    # Initialize the People API
    people_service = build('people', 'v1', credentials=creds)

    # Get contacts
    # contacts = get_contacts(people_service)
    # contacts from google sheets
    # join and get unique values
    # contacts_to_bcc = ','.join(contacts)

    file_path = '/Users/darthpatel/Library/CloudStorage/GoogleDrive-aotnashville@gmail.com/My Drive/Event_flyers/'
    files_2_attach = glob.glob(f'{file_path}*{event_month}*')

    contacts_to_bcc = 'ripatel272@gmail.com,anakha.1@gmail.com'
    # Email details
    sender = 'aotnashville@gmail.com'
    subject = f'[Astro on Tap] {event_month} {event_date} - {event_edition}'
    message_text = html_content
    message_dict = create_message(sender,contacts_to_bcc,subject,
                                  message_text,files_2_attach)

    send_message(service_gmail,'me',message_dict)


if __name__ == '__main__':
    main()
