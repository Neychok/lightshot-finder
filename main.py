import pytesseract
import cv2
import requests
from bs4 import BeautifulSoup
import shutil
import numpy as np

# get grayscale image
def get_grayscale(image):
	return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# noise removal
def remove_noise(image):
	return cv2.medianBlur(image,5)
 
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

#skew correction
def deskew(image):
	coords = np.column_stack(np.where(image > 0))
	angle = cv2.minAreaRect(coords)[-1]
	if angle < -45:
		angle = -(90 + angle)
	else:
		angle = -angle
	(h, w) = image.shape[:2]
	center = (w // 2, h // 2)
	M = cv2.getRotationMatrix2D(center, angle, 1.0)
	rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
	return rotated

#template matching
def match_template(image, template):
	return cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED) 

# Starting number
number = 1000

# Prnt.sc URL Base
page = f'https://prnt.sc/gg{number}'

# Request Page
result = requests.get('https://prnt.sc/fs2342', headers={'User-Agent': 'Chrome'})

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
	r = requests.get(img_url, stream = True, headers={'User-Agent': 'Chrome'})

	# Check if the image was retrieved successfully
	if r.status_code == 200:

		# Set decode_content value to True, otherwise the downloaded image file's size will be zero.
		r.raw.decode_content = True

		# Open a local file with wb ( write binary ) permission.
		filename = 'temp.png'
		with open(filename,'wb') as f:
			shutil.copyfileobj(r.raw, f)
		
		# Read the image
		img = cv2.imread(filename)


		###* IMAGE PRE-PROCESSING ###

		img_gray = get_grayscale(img)
		img_threshed = thresholding( img_gray )
		cv2.imwrite( 'temp2.png', img_threshed )

		###* END ###

		# Read text from image
		text = pytesseract.image_to_string( img_threshed ).lower()
		print(text)
		# Find keyword "password" in text
		if 'career' in text:
			print('found')
			shutil.move( 'temp.png', 'images/' + number + '.png' )
		else:
			print( 'Found Nothing...' )

	else:
		print('Image Couldn\'t be retreived')
# while(True):

# 	number = number + 1