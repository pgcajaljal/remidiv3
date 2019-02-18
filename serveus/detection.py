from cStringIO import StringIO
import cv2, numpy
try: 
	from PIL import Image as PIL
except ImportError:
	import PIL
def main(images, Image):

	print('yep')
	print(images)

	for img,picture_id in images:
		picture_id = picture_id.split('/')[1]
		print(img, picture_id)
		x = Image.query.get(picture_id)
		# print(x.imread)
		x = PIL.open(StringIO(x.im))
		pil_image = x.convert('RGB') 
		open_cv_image = numpy.array(pil_image) 
		# Convert RGB to BGR 
		open_cv_image = open_cv_image[:, :, ::-1].copy() 
		print(open_cv_image)
		# print(cv2.imread(x))
		# pil_image = x.convert('RGB') 
		# open_cv_image = numpy.array(pil_image) 
		# # Convert RGB to BGR 
		# open_cv_image = open_cv_image[:, :, ::-1].copy()
		# print(open_cv_image) 
	# img = PIL.open(StringIO(x.im))
	# img = img.resize((320,240), PIL.ANTIALIAS)
	# a = StringIO()
	# img.save(a, 'JPEG', quality=85)
	# a.seek(0)
	# return send_file(a, mimetype='image/jpeg')

if __name__ == '__main__':
	main()