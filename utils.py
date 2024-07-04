from database import DatabaseHandler
import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()


def list_uploaded_songs():
    db_handler = DatabaseHandler()

    try:
        cursor = db_handler.connect()
        cursor.execute("SELECT DISTINCT song_id FROM fingerprints")
        song_names = [row[0] for row in cursor.fetchall()]
        return song_names
    finally:
        db_handler.close()


def send_email_result(result):
    sender_email = os.getenv("SENDER_EMAIL")
    receiver_email = os.getenv("RECEIVER_EMAIL").split(",")
    password = os.getenv("EMAIL_PASSWORD")

    uploaded_song = list(result.keys())[0]
    match = list(result.values())[0]

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = ", ".join(receiver_email)
    msg["Subject"] = f"Processing Result for {uploaded_song}"

    body = f"Uploaded song: {uploaded_song}\nMatch: {match}"
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, password)
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)

# def send_email_result(result):
#     sender_email = os.getenv("SENDER_EMAIL")
#     receiver_email = os.getenv("RECEIVER_EMAIL").split(",")
#     password = os.getenv("EMAIL_PASSWORD")

#     msg = MIMEMultipart()
#     msg["From"] = sender_email
#     msg["To"] = ", ".join(receiver_email)
#     msg["Subject"] = "Processing Result"
#     print(result)

#     uploaded_song = list(result.keys())[0]
#     match = result[uploaded_song][0]  # Access the first item in the list, which is the match name

#     body = f"Uploaded song: {uploaded_song}\nMatch: {match}"
#     msg.attach(MIMEText(body, "plain"))

#     with smtplib.SMTP("smtp.gmail.com", 587) as server:
#         server.starttls()
#         server.login(sender_email, password)
#         text = msg.as_string()
#         server.sendmail(sender_email, receiver_email, text)