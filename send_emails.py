import glob
import numpy as np
import gmail_api_tools as gat

__author__ = 'Rahul I. Patel, PhD'

# =====================================================================================================
#      EDIT THIS SECTION
# =====================================================================================================
event_day = 'THURS.'
event_month = 'June'
event_date = '27th'
event_edition = 'Summer Solstice Edition'

speaker1_name = 'Dr. Chayan Chatterjee'
speaker1_title = 'Listening to the Cosmic Orchestra Using A.I.'
speaker2_name = 'Dr. Aaron Stemo'
speaker2_title = 'Black Holes Don\'t Suck'
eventbrite_link = 'https://www.eventbrite.com/e/astronomy-on-tap-summer-solstice-edition-tickets-924614435667?aff=ebdsoporgprofile'
location = 'Jackalope Brewing – Tap Room'
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

# =====================================================================================================
gmAPI = gat.GmailAPI()

# ================================================================
# GET CONTACTS
# ================================================================
# contacts from Gmail
contacts_gmail = gmAPI.get_contacts_gmail()
# contacts from GOOGLE sheets
find_regex = '.*Email*.*Responses*.'
contacts_sheet = gmAPI.get_contacts_sheets(find_regex).to_list()

new_email_list = np.concatenate([contacts_sheet, contacts_gmail])
new_email_list = np.unique(new_email_list)

# join and get unique values
contacts_to_bcc_string = ','.join(new_email_list)
print(f'contacts bcc:{contacts_to_bcc_string}')

contacts_to_bcc = 'ripatel272@gmail.com,anakha.1@gmail.com'

# ================================================================
# EMAIL DETAILS
# ================================================================
sender = 'aotnashville@gmail.com'
sender_name = 'Astro on Tap Nashville'

subject = f'[Astro on Tap] {event_month} {event_date} - {event_edition}'
message_text = html_content

# FLYERS TO ATTACH - LOOK FOR CURRENT MONTH FLYERS
file_path = ('/Users/darthpatel/Library/CloudStorage/GoogleDrive-'
             'aotnashville@gmail.com/My Drive/Event_flyers/')
files_2_attach = glob.glob(f'{file_path}*{event_month}*')

# ================================================================
# PUT IT ALL TOGETHER AND SEND
# ================================================================

message_dict = gat.create_message(sender, contacts_to_bcc, subject,
                                  message_text, attach_file_names=files_2_attach,
                                  sender_name=sender_name)

gmAPI.send_message('me', message_dict)
