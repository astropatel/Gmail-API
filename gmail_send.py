import sys
import glob
import numpy as np
import gmail_api_tools as gat

__author__ = 'Rahul I. Patel, PhD'

# =====================================================================================================
#      EDIT THIS SECTION
# =====================================================================================================
event_day = 'TUES.'
event_month = 'Dec'
event_date = '9th'
event_edition = "Valar & Vitality Edition"

speaker1_name = 'Harrison Blake-Goszyk'
speaker1_title = "Why the Hell is Earth so Perfect for Life?"

speaker2_name = 'Dr. Rithya Kunnawalkam Elayavalli'
speaker2_title = "Cosmology of Middle Earth"

eventbrite_link = 'https://www.eventbrite.com/e/astronomy-on-tap-valar-and-vitality-edition-tickets-1968919667728?aff=oddtdtcreator'
location = 'Fait La Force Brewing'
pre_news = ''  # NEW LOCATION! NEW TIME!'
other_news = ''  # additional messages

html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Astronomy on Tap - {event_edition}</title>
</head>
<body>
    <p>Dear AoT-ers!</p>
    <p><strong>{pre_news}</strong></p>
    <p>We are pleased to announce that our <strong>{event_edition}</strong> event for
    Astronomy on Tap will be held on <strong>{event_day} {event_month} {event_date}</strong> at <strong><a href="https://www.faitlaforcebrewing.com/" target="_blank">{location}</a></strong>!</p>
    <p>This event will feature 2 amazing speakers:</p>
    <ul>
        <li><strong>{speaker1_name}</strong><br><em>{speaker1_title}</em></li>
        <li><strong>{speaker2_name}</strong><br><em>{speaker2_title}</em></li>
    </ul>
	<p>{other_news}</p>
    <p>There will be trivia and more prizes after! So come on out after a long day of hard work in the middle of the week and relax while we bombard you with fun astro facts, beer, and prizes!</p>
    <p>Make sure to <a href="{eventbrite_link}" target="_blank">RSVP for the free event at EventBrite</a>.</p>
    <p>Please share to all and any who might be interested!</p>
    <p><strong>Doors 6:00pm | Event 7:00 pm</strong></p>
    
    <p>Check out our <a href="https://astronomyontap.org/locations/nashville-tn/" target="_blank">Chapter Site and upcoming event dates</a>.</p>
    
    <p>Have any feedback for us? Please fill out this <a href="https://forms.gle/QbbadNWP6apfRkTT8" target="_blank">quick survey</a>.</p> 
    
    <p>If you wish to unsubscribe, please reply to this email.</p>
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
sender = 'aotnashville@gmail.com'
sender_name = 'Astro on Tap Nashville'
google_sheet_name = 'Responses_Email_Feedback_SpeakerStuff'
email_tab_name = 'Email List'
# ================================================================
# GET CONTACTS
# ================================================================
# contacts from Gmail
contacts_gmail = gmAPI.get_contacts_gmail()
contact_bool = input("Test email to yourself (t) or Send to everyone (e): ")
if contact_bool == 't':
    new_email_list = [sender]
elif contact_bool == 'e':
    # contacts from GOOGLE sheets
    contacts_sheet = gmAPI.get_contacts_sheets(google_sheet_name,
                                               email_tab_name).to_list()  # ,

    new_email_list = np.concatenate([contacts_sheet, contacts_gmail])
    new_email_list = np.unique(new_email_list)
else:
    sys.exit('incorrect entry. Type "t" or "s"')
# join and get unique values
contacts_to_bcc_string = ','.join(new_email_list)
print(f'contacts bcc:{contacts_to_bcc_string}')
total_emails = len(new_email_list)
print('\n Total emails: {}\n'.format(total_emails))
stop_or_cont = input("y to continue, n to stop: ")
if stop_or_cont == 'n':
    sys.exit("Execution halted")

contacts_to_bcc = contacts_to_bcc_string

# ================================================================
# EMAIL DETAILS
# ================================================================

subject = f'[Astro on Tap] {event_month} {event_date} - {event_edition}'
message_text = html_content

# FLYERS TO ATTACH - LOOK FOR CURRENT MONTH FLYERS
file_path = ('/Users/darthpatel/Library/CloudStorage/GoogleDrive-'
             'aotnashville@gmail.com/My Drive/Event_flyers/')

files_2_attach = glob.glob(f'{file_path}*{event_month}*.png')

print(f'Attached files: {files_2_attach}')

stop_or_cont = input("y to continue, n to stop: ")
if stop_or_cont == 'n':
    sys.exit("Execution halted")

# ================================================================
# PUT IT ALL TOGETHER AND SEND
# ================================================================

message_dict = gat.create_message(sender, contacts_to_bcc, subject,
                                  message_text,
                                  attach_file_names=files_2_attach,
                                  sender_name=sender_name)

gmAPI.send_message('me', message_dict)
