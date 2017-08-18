#!/usr/bin/python

from __future__ import print_function
import httplib2
import os

import picamera
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


def start_photobooth(camera): 
	
	camera.annotate_text_size = 160
	#camera.resolution = (1920, 1080)
	#camera.exposure_mode = 'night'

	# START PICTURE SEQUENCE
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
	# ADDING TIME ON BLACK BACKGROUND ON THE PICTURE
	ts = time.time()
	st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
	camera.annotate_background = picamera.Color('black')
	camera.annotate_text_size = 20
	camera.annotate_text = st

	camera.capture('temp/photo.jpg')
	camera.stop_preview()
	# STAYING FEW SECONDS ON THE PICTURE WITH THE OVERLAY AND THEN REMOVE THE OVERLAY
	# Load the arbitrarily sized image
	img = Image.open('temp/photo.jpg')
	# Create an image padded to the required size with
	# mode 'RGB'
	pad = Image.new('RGB', (
	        ((img.size[0] + 31) // 32) * 32,
	        ((img.size[1] + 15) // 16) * 16,
		))
	# Paste the original image into the padded one
	pad.paste(img, (0, 0))
	
	# Add the overlay with the padded image as the source,
	# but the original image's dimensions
	o = camera.add_overlay(pad.tobytes(), size=img.size)

	sleep(5)
	camera.remove_overlay(o)

	# UPLOAD TO GOOGLE DRIVE
	credentials = get_credentials()
	http = credentials.authorize(httplib2.Http())
	service = discovery.build('drive', 'v3', http=http)
	
	file_metadata = { 'name' : st + '.jpg' }
	media = MediaFileUpload('temp/photo.jpg', mimetype='image/jpeg')
	file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

	os.remove('temp/photo.jpg')

def main():
			
	# INSTANCIATE CAMERA
	camera = picamera.PiCamera()

	# START DISPLAY WHILE BUTTON NOT PRESSED
	# ADDING OVERLAY IMAGE
	# Load the arbitrarily sized image
	img = Image.open('resources/intro.png')
	# Create an image padded to the required size with
	# mode 'RGB'
	pad = Image.new('RGB', (
	        ((img.size[0] + 31) // 32) * 32,
	        ((img.size[1] + 15) // 16) * 16,
		))
	# Paste the original image into the padded one
	pad.paste(img, (0, 0))
	
	# Add the overlay with the padded image as the source,
	# but the original image's dimensions
	camera.add_overlay(pad.tobytes(), size=img.size)

	try:
	    while True:
		led.on()
		if button.is_pressed:
			start_photobooth(camera)

	except KeyboardInterrupt:
		led.off()
		camera.close()
    		pass

if __name__ == '__main__':
    main()
