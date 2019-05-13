import time
from grove.gpio import GPIO
import os
import boto3
class GroveMiniPIRMotionSensor(GPIO):
	def __init__(self, pin):
		super(GroveMiniPIRMotionSensor, self).__init__(pin, GPIO.IN)
		self._on_detect = None

	@property
	def on_detect(self):
		return self._on_detect

	@on_detect.setter
	def on_detect(self, callback):
		if not callable(callback):
			return

		if self.on_event is None:
			self.on_event = self._handle_event

		self._on_detect = callback

	def _handle_event(self, pin, value):
		if value:
			if callable(self._on_detect):
				self._on_detect()

Grove = GroveMiniPIRMotionSensor


def main():
	import sys
	import time

	if len(sys.argv) < 2:
		print('Usage: {} pin'.format(sys.argv[0]))
		sys.exit(1)

	pir = GroveMiniPIRMotionSensor(int(sys.argv[1]))

	def callback():
		ts = int(time.time())
		cmd = "fswebcam test" + str(ts) + ".jpg"
		os.system(cmd)
		time.sleep(15)
		s3 = boto3.client('s3')
		filename = 'test'+str(ts)+'.jpg'
		bucket_name = 'e6765'
		s3.upload_file(filename, bucket_name, filename)
		time.sleep(15)

	pir.on_detect = callback

	while True:
		time.sleep(1)


if __name__ == '__main__':
	main()
