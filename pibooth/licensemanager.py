# https://developers.google.com/calendar/api/quickstart/python
# pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
# add token.json
# -*- coding: utf-8 -*-

"""Pibooth licensemanager.
"""

from __future__ import print_function
import configparser

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from dateutil.parser import parse as dtparse
from datetime import datetime, timezone

from uuid import getnode as get_mac
import logging


LOGGER = logging.getLogger("pibooth")


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def parseDate(stringdate):
    tmfmt = '%d %B, %H:%M %p'            
    return dtparse(stringdate)

def isDatetimeInRange(start):
    realStart = parseDate(start)
    now = datetime.now(timezone.utc)
    difference = (realStart - now).total_seconds() / 60 / 60
    print('Event coming up in (hours): ', difference)
    return (difference < 24)

def getUUID():
    mac = get_mac()
    #print(mac)
    #print(hex(mac))
    macString = ':'.join(("%012X" % mac)[i:i+2] for i in range(0, 12, 2))
    uuid = '[' + macString + ']'
    return uuid

def getEvents(): 
    print("Trying to get the license from Google Calendar")
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        print('Getting the upcoming event')
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime', q=getUUID()).execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return
        
        return events
    
    except HttpError as error:
        print('An error occurred: %s' % error)  
    
def checkEvents():
    config = ""
    events = getEvents()   
    if(events):
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])
            if (isDatetimeInRange(start)):
                config = event['description']
                break
    
    #### TODO Check the config file for the UUID
    
    #configparser.ConfigParser()
    #config.read(config)
    #print(config.get('UUID'))
    
    if(config):
        print(config)
        return config
    else:
        print("No event found within 24 hours")
        return False
            
    #print(getUUID())
    ####
        
if __name__ == '__main__':
    checkEvents()
