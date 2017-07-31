#!/usr/bin/python

from __future__ import print_function
import httplib2
import os

from picamera import PiCamera, Color
from time import sleep
from gpiozero import LED, Button
from signal import pause
from PIL import Image

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
SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'resources/client_secret.json'
APPLICATION_NAME = 'Pythobooth'

# DEFINITION OF INPUT / OUTPUT
led = LED(4)
button = Button(26)


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

# define the photo taking function for when the big button is pressed 
def start_photobooth(): 
	if button.is_pressed:
		# CAMERA
		camera = PiCamera()
		camera.annotate_text_size = 160
		#camera.resolution = (1920, 1080)
		#camera.exposure_mode = 'night'
		#camera.flash_mode = 'torch'
		camera.awb_mode = 'cloudy'

		# START PICTURE SEQUENCE
		camera.start_preview()
		camera.flash_mode = 'torch'
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
		st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
		camera.capture('/home/pi/Desktop/photo.jpg')
		camera.stop_preview()
		camera.flash_mode = 'off'

		# UPLOAD TO GOOGLE DRIVE
		credentials = get_credentials()
		http = credentials.authorize(httplib2.Http())
		service = discovery.build('drive', 'v3', http=http)
		
		file_metadata = { 'name' : st + '.jpg' }
		media = MediaFileUpload('/home/pi/Desktop/photo.jpg', mimetype='image/jpeg')
		file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

		os.remove('/home/pi/Desktop/photo.jpg')
		camera.close()


def main():
	# START DISPLAY WHILE BUTTON NOT PRESSED
	#img = Image.open('resources/intro.png')
	#img.show()

	try:
	    while True:
		led.on()
		start_photobooth()

	except KeyboardInterrupt:
		led.off()
		camera.close()
    		pass

if __name__ == '__main__':
    main()
