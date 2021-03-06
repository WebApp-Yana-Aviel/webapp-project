
# import the necessary packages
import uuid
import os
class TempImage:
    def __init__(self, basePath="/home/webrgacv/webrobotapp/app/home/Temp", ext=".jpg"):
	  	# construct the file path
       self.path = "{base_path}/{rand}{ext}".format(base_path=basePath,
          rand=str(uuid.uuid4()), ext=ext)
    def cleanup(self):
		# remove the file
       os.remove(self.path)
       
class TempVideo:
    def __init__(self, basePath="/home/webrgacv/webrobotapp/app/home/Temp", ext=".avi"):

    		# construct the file path
        self.path = "{base_path}/{rand}{ext}".format(base_path=basePath,
            rand=str(uuid.uuid4()), ext=ext)
    def cleanup(self):
	    	# remove the file
        os.remove(self.path)
