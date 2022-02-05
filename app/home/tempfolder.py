
# import the necessary packages

import os
import shutil
class TempFolder:
    global folder
    
    def __init__(self):
       global folder
		# construct the file path
       folder='/home/webrgacv/webrobotapp/app/static/images/Temp/'

       self.path=folder
       if not os.path.isdir(folder):
           os.mkdir(folder,mode=0o777)
    
    def cleanup(self):
        global folder
        shutil.rmtree(folder)
		# remove the file
    
    def cleanupFile(self,fileName):
        
        if os.path.exists(fileName):
            os.remove(fileName)
        else:
            print("The file does not exits")
  

        
       