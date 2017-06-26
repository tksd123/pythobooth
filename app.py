#!/usr/bin/python

from __future__ import print_function
import httplib2
import os

from picamera import PiCamera, Color
from time import sleep

import datetime
import time

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from apiclient.http import MediaFileUpload

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/drive.file'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Drive API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'drive-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():
    # CAMERA

    camera = PiCamera()

    camera.annotate_text_size = 160
    #camera.annotate_background = Color('blue')
    camera.annotate_foreground = Color('blue')

    #camera.exposure_mode = 'night'

    camera.start_preview()
    camera.annotate_text = "PRETS ???"
    sleep(3)
    camera.annotate_text = "5"
    sleep(1)
    camera.annotate_text = "4"
    sleep(1)
    camera.annotate_text = "3"
    sleep(1)
    camera.annotate_text = "2"
    sleep(1)
    camera.annotate_text = "1"
    sleep(1)
    camera.annotate_text = ""

    ts = time.time()
    st1 = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    camera.capture('/home/pi/Desktop/photo1.jpg')

    camera.image_effect = 'gpen'

    ts = time.time()
    st2 = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    camera.capture('/home/pi/Desktop/photo2.jpg')

    camera.image_effect = 'cartoon'

    ts = time.time()
    st3 = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    camera.capture('/home/pi/Desktop/photo3.jpg')

    camera.image_effect = 'pastel'

    ts = time.time()
    st4 = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    camera.capture('/home/pi/Desktop/photo4.jpg')

    camera.stop_preview()
    sleep(3)


# UPLOAD TO  GOOGLE DRIVE
    
    """Shows basic usage of the Google Drive API.

    Creates a Google Drive API service object and outputs the names and IDs
    for up to 10 files.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)

    for letter in '1234':
        file_metadata = { 'name' : eval('st' + letter) + '.jpg' }
        media = MediaFileUpload('/home/pi/Desktop/photo' + letter + '.jpg',
                                mimetype='image/jpeg')
        file = service.files().create(body=file_metadata,
                                            media_body=media,
                                            fields='id').execute()

if __name__ == '__main__':
    main()
