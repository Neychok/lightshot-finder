import pytesseract
import cv2
import requests
from bs4 import BeautifulSoup
import shutil
import numpy as np
from random import choice
from string import ascii_lowercase, digits
import time

# get grayscale image
def get_grayscale(image):
	return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

#thresholding
def thresholding(image):
	return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

#dilation
def dilate(image):
	kernel = np.ones((5,5),np.uint8)
	return cv2.dilate(image, kernel, iterations = 1)
	
#erosion
def erode(image):
	kernel = np.ones((5,5),np.uint8)
	return cv2.erode(image, kernel, iterations = 1)

#opening - erosion followed by dilation
def opening(image):
	kernel = np.ones((5,5),np.uint8)
	return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)

#canny edge detection
def canny(image):
	return cv2.Canny(image, 100, 200)

def checkImage( image, keywords, blacklist ):

	try:
		text = pytesseract.image_to_string( image ).lower()
	except:
		return False

	for word in blacklist:
		if word in text:
			print( 'found: ' + word )
			return False

	for word in keywords:
		if word in text:
			print( 'found: ' + word )
			return word

	return False

# Starting number
number = 1228


# Keywords we want to search for
keywords = [
	'password',
	'email',
	'username',
	'phrase',
	'secret',
	'e-mail'
	'e mail'
	'pasword'
	'wallet'
]

blacklist = [
	'georgian33',
	'sergein777',
	'bit king',
	'jira',
	'jiratrade'
]

while(True):

	# Increment Page number
	slug_letters = ''.join(choice(ascii_lowercase) for i in range(3))
	slug_numbers = ''.join(choice(digits) for i in range(3))

	# Prnt.sc URL
	page = f'https://prnt.sc/{slug_letters}{slug_numbers}'

	# Request Page
	try:
		result = requests.get(page, headers={'User-Agent': 'Chrome'})
	except:
		print('Error getting page')
		time.sleep(5)
		continue

	# If page accessed
	if result.status_code == 200:

		# Process page to HTML
		soup = BeautifulSoup(result.content, "lxml")

		# Find Image
		img = soup.find('img',{'class':'screenshot-image'})
		img_url = img['src']

		# If image is missing HTTP add it
		if 'http' not in img_url:
			img_url = 'http:' + img_url

		print( f'Searching {page}' )

		# Open the url image, set stream to True, this will return the stream content.
		try:
			r = requests.get(img_url, stream = True, headers={'User-Agent': 'Chrome'})
		except:
			print('Error getting image')
			time.sleep(1)
			continue

		# Check if the image was retrieved successfully
		if r.status_code == 200:

			# Set decode_content value to True, otherwise the downloaded image file's size will be zero.
			r.raw.decode_content = True

			# Open a local file with wb ( write binary ) permission.
			filename = 'temp.png'
			with open(filename,'wb') as f:
				shutil.copyfileobj(r.raw, f)
			
			# Read the image
			img_base = cv2.imread(filename)

			# First check the base image
			try:
				found_word = checkImage( img_base, keywords, blacklist )
			except:
				print('Error while checking base image')
				continue
			if found_word :
				shutil.move( 'temp.png', f'images/{slug_letters}{slug_numbers}-{found_word}.png' )
				continue

			# Get Grayscale image
			try:
				img_gray = get_grayscale( img_base )
			except:
				print('Error while grayscaling')
				continue

			# Check grayscale image
			found_word = checkImage( img_gray, keywords, blacklist )
			if found_word :
				shutil.move( 'temp.png', f'images/{slug_letters}{slug_numbers}-{found_word}.png' )
				continue

			# Threshold Image
			try:
				img_threshed = thresholding( img_gray )
			except:
				print('Error with performing thresholding')
				continue

			# Check threshed image
			found_word = checkImage( img_threshed, keywords, blacklist )
			if found_word:
				shutil.move( 'temp.png', f'images/{slug_letters}{slug_numbers}-{found_word}.png' )
				continue

			# Get opening image
			# img_opening = opening( img_gray )
			# if checkImage( img_opening, keywords ) :
			# 	shutil.move( 'temp.png', f'images/{number}.png' )
			# 	continue

			# Get canny image
			# img_canny = canny( img_gray )
			# if checkImage( img_canny, keywords ) :
			# 	shutil.move( 'temp.png', f'images/{number}.png' )
			# 	continue

			print( 'Found Nothing...' )

		else:
			print('Image Couldn\'t be retreived')