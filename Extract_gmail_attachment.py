import imaplib
import email
from utils import email_id, password, attch_dir
import os

imap_server = "imap.gmail.com"
imap = imaplib.IMAP4_SSL(imap_server)
imap.login(email_id,password)
imap.select("Inbox")

_, msgnums = imap.search(None, "All")
download_dir = attch_dir


medical_keywords = ["health", "medical", "doctor", "prescription", "treatment", "appointment", "diagnosis", "clinic"]


if not os.path.exists(download_dir):
    os.makedirs(download_dir)

for msgnum in msgnums[0].split():
    _, data = imap.fetch(msgnum, "(RFC822)")

    msg = email.message_from_bytes(data[0][1])

    print(f"Downloading attachments for message no. {msgnum}")

    from_address = msg.get('From')
    subject = msg.get('Subject')
    date = msg.get('Date')

    if any(keyword in subject.lower() for keyword in medical_keywords):


        email_dir = os.path.join(download_dir, subject)

        if not os.path.exists(email_dir):
            os.makedirs(email_dir)

        with open(os.path.join(email_dir, "email_info.txt"), "w") as file:
            file.write(f"message no. - {msgnum}\n")
            file.write(f"from - {from_address}\n")
            file.write(f"To - {msg.get('To')}\n")
            file.write(f"Date - {date}\n")
            file.write(f"Subject - {subject}\n")
            file.write("contents:\n")

            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    file.write(part.as_string())
                    file.write("\n") 

                elif part.get_content_disposition() and part.get_filename():
                    attachment_path = os.path.join(email_dir, part.get_filename())
                    with open(attachment_path, "wb") as attachment_file:
                        attachment_file.write(part.get_payload(decode=True))

            print(f"Attachments downloaded for message no. {msgnum}")

imap.logout()
