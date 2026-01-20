# Gmail-API
Use this to send emails through gmail using python. Right now, it's optimized for [Astronomy on Tap - Nashville monthly email announcements]([url](https://astronomyontap.org/locations/nashville-tn/)).
<hr>

## Quick Use 
Modify and run `send_emails.py`. It uses functions from `gmail_api_tools.py`. If you haven't already set-up the API tokens, see below for details.
<hr>

## Current features include:
0. Modify monthly Astro on Tap - Nashville monthly announcement emails
1. Download and interact with email addresses in gmail
2. Interact with google drive
3. Send HTML-based messages
4. Send attachments with email
5. Send email via bcc.

To set-it up, you need to set-up the GMAIL API. This will produce the correct credentails.json and token.json file to connect to your gmail account. If you're an AoT Nashville team member and want to interact with the AoT Nashville account, send me a message, and I'll send you pre-generated *.json files

## Step-by-Step Guide to Set Up Gmail API
1. Enable the Gmail API
  * Go to the Google Cloud Console:
      Open the [Google Cloud Console]([url](https://console.cloud.google.com/welcome/new)).
  * Select "New Project" after clickign on "Select a Project" at the top,   

2.Create a New Project:
  * Click on the project drop-down and select "New Project".
  * Enter a project name and click "Create".
  * Select the newly formed project. This should take you to the project dashboard

3. Enable the Gmail API:
  * Navigate to the "API's Overview" page
  * Click on "Enable APIS and Services"
  * Search for the "GMAIL" and "People" APIs and enable both.
  * If you wish to access Drive, search for Drive, Sheets, etc, APIs and enable these too

4. Create OAuth 2.0 Credentials:

  * Go to the Credentials page.
  * Click "Create Credentials" and select "OAuth client ID".
  * Configure the consent screen by providing the necessary information.
  * Add your scopes. Find all the scopes you want for your purposes (e.g., send mail). 
  * Select "Application type" as "Desktop app".
  * Click "Create" and then "Download" the JSON file. This file contains your client ID and client secret. Save it as `credentials.json`.


5. Set Up Your Python Environment

 * Install Required Libraries:
 * Open your terminal or command prompt.
 * Install the necessary Python libraries using pip
`pip install --upgrade google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
`

You should be set to use the associated script.

6. Run the script

  * The file ``gmail_send.py`` is the main script you'll need to run
  * It accesses all your google sheets in the google drive you've assigned through the process above
  * Right now, it pulls event information through one sheet as seen below, and then also pulls every email address in another sheet and adds it to the list of emails in your google contacts to send out the email
  * It also locates flyers (whatever format) through the flyer ``file_path`` variable and attaches all files to the email.
  * See below for images of the google sheet screenshots
  * Body of the email is in the ``gmail_send.py`` script
  * Prompts will ask if you wish to send a test email to yourself or eamil everyone via bcc.

<img width="828" height="540" alt="image" src="https://github.com/user-attachments/assets/ccbb8170-8db3-49be-9596-6657c366d320" />
<img width="592" height="293" alt="image" src="https://github.com/user-attachments/assets/2820b3b6-a0f6-4a81-9964-f991c54e7255" />


