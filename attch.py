import base64
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
import html2text


credentials_file_path = 'credentials.json'

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail_api():
    creds = None
   
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json')
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_file_path, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def download_attachments(service, msg_id, download_dir):
    medical_keywords = ["health", "medical", "doctor", "prescription", "treatment", "appointment", "diagnosis", "clinic"]

    try:
        message = service.users().messages().get(userId='me', id=msg_id).execute()
        from_address = message['payload']['headers'][0]['value']
        subject = next(header['value'] for header in message['payload']['headers'] if header['name'] == 'Subject')
        date = next(header['value'] for header in message['payload']['headers'] if header['name'] == 'Date')

        # print(f"Downloading attachments for message with ID: {msg_id}")

        if any(keyword in subject.lower() for keyword in medical_keywords):
            email_dir = os.path.join(download_dir, subject)

            if not os.path.exists(email_dir):
                os.makedirs(email_dir)

            # with open(os.path.join(email_dir, "email_info.txt"), "w") as file:
            #     file.write(f"Message ID: {msg_id}\n")
            #     file.write(f"From: {from_address}\n")
            #     file.write(f"Date: {date}\n")
            #     file.write(f"Subject: {subject}\n")
            #     file.write("Contents:\n")

            for part in message['payload']['parts']:
                if 'body' in part:
                    if 'attachmentId' in part['body']:
                        attachment = service.users().messages().attachments().get(
                            userId='me', messageId=msg_id, id=part['body']['attachmentId']).execute()

                        file_data = base64.urlsafe_b64decode(attachment['data'].encode('UTF-8'))

                        # Create a unique filename or use a default name if the filename is empty
                        filename = part['filename'] or 'attachment.bin'
                        file_path = os.path.join(email_dir, filename)

                        with open(file_path, "wb") as attachment_file:
                            attachment_file.write(file_data)

                        # print(f"Attachment downloaded: {filename}")
                        # file.write(f"Attachment: {filename}\n")

                    elif 'data' in part['body']:
                        file_data = base64.urlsafe_b64decode(part['body']['data'].encode('Latin'))

                        # Create a unique filename or use a default name if the filename is empty
                        filename = 'body.txt'
                        file_path = os.path.join(email_dir, filename)

                        with open(file_path, "wb") as attachment_file:
                            attachment_file.write(file_data)

                        # print(f"Attachment downloaded: {filename}")
                        # file.write(f"Attachment: {filename}\n")


    except HttpError as error:
        print(f"An error occurred: {error}")



def main():
    creds = authenticate_gmail_api()
    
    service = build('gmail', 'v1', credentials=creds)

    try:
        results = service.users().messages().list(userId='me', labelIds=['INBOX']).execute()
        messages = results.get('messages', [])

        download_dir = 'Med_email'

        if not os.path.exists(download_dir):
            os.makedirs(download_dir)

        for message in messages:
            download_attachments(service, message['id'], download_dir)

    except HttpError as error:
        print(f"An error occurred: {error}")

if __name__ == '__main__':
    main()
