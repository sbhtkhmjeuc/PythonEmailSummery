from __future__ import print_function

import base64
import os.path
import pickle

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from requests import HTTPError

# from WebScrapying import linkExtractionFromHTML
from MailsSummeryUpdated import extract_links as ExractLinks

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
]

sender_list = [
    "rahul@pythonweekly.com",
    "info@cloudseclist.com",
    "jsw@peterc.org",
    "clint@tldrsec.com",
    "frontend@cooperpress.com",
    "executiveoffense@mail.beehiiv.com",
    "newsletter@css-weekly.com",
    "bluepurple@substack.com",
    "react@cooperpress.com",
    "cyficrime@substack.com",
    "hello@awssecuritydigest.com",
    "bee@securib.ee",
    # "riskybiznews@substack.com",
    "bee@mail.hivefive.community",
    # "rahul@founderweekly.com",
    "hello@sourcesmethods.com",
    "blockthreat@substack.com",
    "weekinethereum@substack.com",
    "hello@sourcesmethods.com",
    "node@cooperpress.com",
    "defihacklabs@substack.com",
    "kenny@uxdesignweekly.com",
    "newsletter@smashingmagazine.com",
    "tamas@heydesigner.com",
    "riskybiznews@substack.com",
    "risky-biz@ghost.io",
    "securitypills@mail.beehiiv.com",
    # "comment-reply@wordpress.com",
]

# daniel@danielmiessler.com


def extract_email(text):
    start = text.find("<") + 1
    end = text.find(">")
    if start != 0 and end != -1:
        return text[start:end]
    else:
        return text


def get_message(service, msg_id, user_id="me"):
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id).execute()
        return message
    except (HTTPError, RefreshError) as error:
        print(f"An error occurred: {error}")


def get_sender_email(service, msg_id, user_id="me"):
    message = get_message(service, msg_id, user_id)

    if not message:
        return None

    payload = message.get("payload", {})
    headers = payload.get("headers", [])

    for header in headers:
        name = header.get("name")
        if name == "From":
            return header.get("value")

    return None


def authentication():
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials/credentials.json",
                SCOPES,
            )
            creds = flow.run_local_server(port=0)
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    print("Authentication successful")
    return creds


def main():
    creds = authentication()
    service = build("gmail", "v1", credentials=creds)
    query = "is:unread"
    if sender_list:
        query += " from:({})".format(" OR ".join(sender_list))
    response = service.users().messages().list(userId="me", q=query).execute()
    if response["resultSizeEstimate"] == 0:
        print("No New Messages")
    else:
        print("You Have New Messages")
        messages = response["messages"]
        for message in messages:
            message_details = (
                service.users().messages().get(userId="me", id=message["id"]).execute()
            )
            MessageID = message_details["id"]
            payload = message_details["payload"]
            if "parts" in payload:
                for part in payload["parts"]:
                    if part["mimeType"] == "text/html":
                        data = part["body"]["data"]
                        break
            else:
                data = payload["body"]["data"]
            html = base64.urlsafe_b64decode(data).decode()
            sender = extract_email(get_sender_email(service, MessageID))
            if ExractLinks(html, sender, MessageID) == 0:
                break
            service.users().messages().modify(
                userId="me", id=MessageID, body={"removeLabelIds": ["UNREAD"]}
            ).execute()
            print(MessageID + " Marked as Read")


if __name__ == "__main__":
    main()

# TODO : Fix the "clint@tldrsec.com" Mails
