import cv2
import datetime
import RPi.GPIO as GPIO

import os
import time
import os, sys
import numpy as np
import socket
from threading import Thread
from multiprocessing import Process
import json
import dropbox
import imutils
from .. import db
from .sendMessage import send_sms_user_photo,send_sms_admin_message,send_sms_user_message
from .temperature_raspberry import temperature_of_raspberry_pi
from ..models import Route, RouteStation, Video,Photo,LogUser,User
from .tempimage import TempImage,TempVideo
from .tempfolder import TempFolder
from .tempfolderV import TempFolderV
from ..auth.email import send_email_route_photo,send_email_admin_obstacle_photo,send_email_route1_photo
import subprocess
from flask import render_template
import glob
import math
from flask import Flask
import pygame
from pygame import mixer
#from .manual import sensor_back,backward,manual_stop,sensor_drive,leds_turn,execute_unix,forward,turn_right,turn_left,stop,sensor_drive
from flask import render_template,request

mixer.init()

#global parameters

global  p1,p2,distanc,status_key,capture,face1,camera,if_route_sec,rec_frame,vs,arucoR, grey, switch, face, rec, out,frame, start_time,left,right,move,tv,STATE,Stop_router
global  exits
capture=0 
distanc=25

grey=0
face=0
face1=0
switch=1 
rec=False
start_time=0
left=0
right=0
move = 0
start_time = 0
tv=0
arucoR=0
out=0
STATE=1
Stop_router=0
if_route_sec=0
status_key=0
conf_path='/home/webrgacv/webrobotapp/app/home/conf/conf.json'
# check to see if the Dropbox should be used
f=open(conf_path)
data=json.load(f)
if data["use_dropbox"]:
	# connect to dropbox and start the session authorization process
    client = dropbox.Dropbox(data["dropbox_access_token"])
    print("[SUCCESS] dropbox account linked")
f.close()

# face detection model
protoFile = '/home/webrgacv/webrobotapp/app/home/saved_model/deploy.prototxt.txt'
weightsFile = '/home/webrgacv/webrobotapp/app/home/saved_model/res10_300x300_ssd_iter_140000.caffemodel'
face_pat='/home/webrgacv/webrobotapp/app/home/saved_model/haarcascade_fron_def.xml'
face_patter=cv2.CascadeClassifier(face_pat)
#Load pretrained face detection model    
net = cv2.dnn.readNetFromCaffe(protoFile, weightsFile)

#--------------------------------
#information of camera
cameraMatrix_path='/home/webrgacv/webrobotapp/app/home/saved_model/cameraMatrix.txt'
distCoeffs_path='/home/webrgacv/webrobotapp/app/home/saved_model/cameraDistortion.txt'

#parameters for detection
arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_250)
arucoParams = cv2.aruco.DetectorParameters_create()

#convert .txt file to array
with open(cameraMatrix_path) as f:
   mylist = [line.rstrip('\n') for line in f]
cameraMatrix = np.loadtxt(mylist,delimiter=",")
f.close()

with open(distCoeffs_path) as f:
   mylist = [line.rstrip('\n') for line in f]
distCoeffs = np.loadtxt(mylist,delimiter=",")
f.close()

# aruco markers dictionary             
ARUCO_DICT = {
    "DICT_4X4_50": cv2.aruco.DICT_4X4_50,
    "DICT_4X4_100": cv2.aruco.DICT_4X4_100,
    "DICT_4X4_250": cv2.aruco.DICT_4X4_250,#
    "DICT_4X4_1000": cv2.aruco.DICT_4X4_1000,
    "DICT_5X5_50": cv2.aruco.DICT_5X5_50,
    "DICT_5X5_100": cv2.aruco.DICT_5X5_100,
    "DICT_5X5_250": cv2.aruco.DICT_5X5_250,
    "DICT_5X5_1000": cv2.aruco.DICT_5X5_1000,
    "DICT_6X6_50": cv2.aruco.DICT_6X6_50,
    "DICT_6X6_100": cv2.aruco.DICT_6X6_100,
    "DICT_6X6_250": cv2.aruco.DICT_6X6_250,
    "DICT_6X6_1000": cv2.aruco.DICT_6X6_1000,
    "DICT_7X7_50": cv2.aruco.DICT_7X7_50,
    "DICT_7X7_100": cv2.aruco.DICT_7X7_100,
    "DICT_7X7_250": cv2.aruco.DICT_7X7_250,
    "DICT_7X7_1000": cv2.aruco.DICT_7X7_1000,
    "DICT_ARUCO_ORIGINAL": cv2.aruco.DICT_ARUCO_ORIGINAL,
    "DICT_APRILTAG_16h5": cv2.aruco.DICT_APRILTAG_16h5,
    "DICT_APRILTAG_25h9": cv2.aruco.DICT_APRILTAG_25h9,
    "DICT_APRILTAG_36h10": cv2.aruco.DICT_APRILTAG_36h10,
    "DICT_APRILTAG_36h11": cv2.aruco.DICT_APRILTAG_36h11
}

print("[INFO] detecting '{}' tags...".format("DICT_4X4_250"))

# Opening a camera
print("[INFO] starting video stream...")
if os.environ.get('WERKZEUG_RUN_MAIN') or Flask.debug is False:
##****------
  camera = cv2.VideoCapture(0)
  time.sleep(2.0)

print('[DEBUG] call cv2.VideoCapture(0) from PID', os.getpid())


##******
#GPIO
"""
initialization
"""
mA1=24
mA2=23
mB1=17
mB2=27
en1=18
en2=12

#set GPIO for sensors
sensor_a=16 #middle
sensor_b=6  #left
sensor_c=5  #right

#set LEDs
led_red=26
led_blue=25
led_green=13
led_yellow=20
# import pdb; pdb.set_trace()
# GPIO.cleanup()
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(mA1, GPIO.OUT)
GPIO.setup(mA2, GPIO.OUT)
GPIO.setup(mB1, GPIO.OUT)
GPIO.setup(mB2, GPIO.OUT)
GPIO.setup(en1,GPIO.OUT)
GPIO.setup(en2,GPIO.OUT)
GPIO.setup(16,GPIO.IN)
GPIO.setup(6,GPIO.IN)
GPIO.setup(5,GPIO.IN)
p1=GPIO.PWM(en1,1000)
p1.start(33)
p2=GPIO.PWM(en2,1000)
p2.start(33)

TRIG = 22
ECHO = 2


GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.output(TRIG, GPIO.LOW)

#sensor = DistanceSensor(4,22)

GPIO.setup(led_red,GPIO.OUT)
GPIO.setup(led_yellow,GPIO.OUT)
GPIO.setup(led_blue,GPIO.OUT)
GPIO.setup(led_green,GPIO.OUT)

GPIO.output(mA1,0)
GPIO.output(mA2,0)
GPIO.output(mB1,0)
GPIO.output(mB2,0)

GPIO.output(led_red,0)
GPIO.output(led_yellow,0)
GPIO.output(led_green,0)
GPIO.output(led_blue,0)

def distance():
    global distanc
    count=0
    avg_dist=0
    for i in range(5):
        dist=distance_check()
        if(dist != "N/A"):
            avg_dist=avg_dist+dist
            count=count + 1
    if(avg_dist != 0):
        distanc=avg_dist/count
            
  
def distance_check():
    
    new_reading = False
    counter = 0
    distance = 0
    duration = 0
    GPIO.output(TRIG, 0)
    time.sleep(0.000002)
    GPIO.output(TRIG, 1) # here the trigger is put on
    time.sleep(0.000010) # 10us of trigger duration
    GPIO.output(TRIG, 0) # now trigger is put off  
    time.sleep(0.000002)
    while GPIO.input(ECHO) == 0:
        pass
        counter += 1
        if counter == 5000:
            new_reading = True
            break

    if new_reading:
         return False
    startT = time.time()
    while GPIO.input(ECHO) == 1: pass
    feedbackT = time.time()
    if feedbackT == startT:
       distance = "N/A"
    else:
       duration = feedbackT - startT
       distance = duration *17150
       distance = round(distance, 2)
    return distance

    
# record video stream
def record(out):
    global rec_frame
    while(rec):
        time.sleep(0.05)
        out.write(rec_frame)

# Face detection function 
def detect_face(frame):
    global net
    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0,
        (300, 300), (104.0, 177.0, 123.0))   
    net.setInput(blob)
    detections = net.forward()
    confidence = detections[0, 0, 0, 2]

    if confidence < 0.5:            
            return frame           

    box = detections[0, 0, 0, 3:7] * np.array([w, h, w, h])
    (startX, startY, endX, endY) = box.astype("int")
    try:
        frame=frame[startY:endY, startX:endX]
        (h, w) = frame.shape[:2]
        r = 480 / float(h)
        dim = ( int(w * r), 480)
        frame=cv2.resize(frame,dim)
    except Exception as e:
        pass
    return frame

# Face detection function and quare marking
def detect_face_1(frame):
    faces = face_patter.detectMultiScale(frame,scaleFactor=1.1,
    minNeighbors=5,minSize=(80, 80))
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
    return frame    

# aruco marker detection
def detect_aruco(frame):
    # Detect ArUco markers in the video frame
    # grab the current timestamp and draw it on the frame
    
    timestamp = datetime.datetime.now()
    cv2.putText(frame, timestamp.strftime("%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
    # if the total number of frames has reached a sufficient
	# number to construct a reasonable background model, then
	# continue to process the frame	
    # Detect ArUco markers in the video frame
    (corners, ids, rejected) = cv2.aruco.detectMarkers(
            frame, arucoDict, parameters=arucoParams)
       
    # Check that at least one ArUco marker was detected
    if len(corners) > 0:
        # Flatten the ArUco IDs list
        ids = ids.flatten()
       
        # Loop over the detected ArUco corners
        for (marker_corner, marker_id) in zip(corners, ids):
           
            # Extract the marker corners
            corners = marker_corner.reshape((4, 2))
            (top_left, top_right, bottom_right, bottom_left) = corners
         
            # Convert the (x,y) coordinate pairs to integers
            top_right = (int(top_right[0]), int(top_right[1]))
            bottom_right = (int(bottom_right[0]), int(bottom_right[1]))
            bottom_left = (int(bottom_left[0]), int(bottom_left[1]))
            top_left = (int(top_left[0]), int(top_left[1]))
         
            # Draw the bounding box of the ArUco detection
            cv2.line(frame, top_left, top_right, (0, 255, 0), 2)
            cv2.line(frame, top_right, bottom_right, (0, 255, 0), 2)
            cv2.line(frame, bottom_right, bottom_left, (0, 255, 0), 2)
            cv2.line(frame, bottom_left, top_left, (0, 255, 0), 2)
         
            # Calculate and draw the center of the ArUco marker
            center_x = int((top_left[0] + bottom_right[0]) / 2.0)
            center_y = int((top_left[1] + bottom_right[1]) / 2.0)
            cv2.circle(frame, (center_x, center_y), 4, (0, 0, 255), -1)
         
            # Draw the ArUco marker ID on the video frame
            # The ID is always located at the top_left of the ArUco marker
            cv2.putText(frame, str(marker_id), 
                     (top_left[0], top_left[1] - 15),
            cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 255, 0), 2)
   

    return frame

# generate frame by frame from camera
def gen_frames(userId):  
    global out, capture,rec_frame
    while True:     
        success, frame = camera.read()
        if success:
            if(face):                
                frame= detect_face(frame)
            if(face1):                
                frame= detect_face_1(frame)
            if(grey):
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)    
            if(capture):
                capture=0
                ts=datetime.datetime.now().strftime("%m %d %Y.%H:%M:%S%p")
                # open a file to read
                f=open(conf_path)
                data=json.load(f)
                if data["use_dropbox"]:
				# write the image to temporary file                  			
                    t = TempImage()
                    cv2.imwrite(t.path, frame)
					# upload the image to Dropbox and cleanup the tempory image
                    print("[UPLOAD] {}".format(ts))
                    path = "/{base_path}/{timestamp}.jpg".format(
                    base_path=data["dropbox_base_path"], timestamp=ts)
                    name_photo="{timestamp}.jpg".format(timestamp=ts)
                    client.files_upload(open(t.path, "rb").read(), path)
                    t.cleanup()
                    print('[INFO] capture:userid,path :',userId,path)
                    photo=Photo(name=name_photo,user_id=userId,route_id=1)
                  
                    try:
                        db.session.add(photo)  # Adds new image record to database
                        db.session.commit()  # Commits all changes
                        print('[INFO] Add into db - new image')
                    except:
                    # in case image name already exists
                        print('[ERROR] image name already exists.')
                      
                f.close()
            if(rec):
                rec_frame=frame
                frame= cv2.putText(cv2.flip(frame,1),"Recording...", (0,25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255),4)
            if(arucoR):
                frame = detect_aruco(frame)
   
            try:
                
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            except Exception as e:
                pass
                

# user selection in manual state
# input : name of task and id of user
def tasks(task,userId):
    global switch,camera
    if task == 'capture':
            global capture
            capture=1
    elif  task == 'grey':
            global grey
            grey=not grey

    elif  task == 'face':
            global face
            face=not face 
            if(face):
                time.sleep(1)  
    
    elif  task == 'face1':
            global face1
            face1=not face1 
            if(face1):
                time.sleep(1) 
    elif  task == 'aruco':
            global arucoR
            arucoR=not arucoR
            if(arucoR):
                time.sleep(1) 
    elif task== 'stopL':
            print(switch)
            if(switch==1):
                switch=0
                camera.release()
                cv2.destroyAllWindows()             
            else:
                if os.environ.get('WERKZEUG_RUN_MAIN') or Flask.debug is False:
                    camera = cv2.VideoCapture(0)

                switch=1
    elif task == 'record':
        global rec,path,out,tv
        print('[INFO] In to record - cameryPi - manual state')      
        rec= not rec
  
        if(rec):   
            tv = TempVideo()
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(tv.path, fourcc, 20.0, (640, 480))
            print('[Info] record...')
            #Start new thread for recording the vide
            thread = Thread(target = record, args=[out,])
            thread.start()
        else:
            out.release()
            f=open(conf_path)
            data=json.load(f)
            if data["use_dropbox"]:
                timestamp = datetime.datetime.now()
                ts = timestamp.strftime("%m %d %Y.%H:%M:%S%p")
                print("[UPLOAD] {}".format(ts))
                path = "/{base_path}/{timestamp}.avi".format(base_path=data["dropbox_base_path1"], timestamp=ts)                                                                      
                name_Video="{timestamp}.avi".format(timestamp=ts)
  
                videoFile=open(tv.path, "rb")
                data=videoFile.read()
                
                # video file upload to dropbox
                client.files_upload(data,path)
                print('[INFO] upload video....')
                videoFile.close()
                print('[INFO] close video....')
                tv.cleanup()
                print('[INFO] delete video....')

                # add to db      
                video=Video(name=name_Video,user_id=userId,routeV_id=1)
                print('[INFO] Add to db  new record... ')
                try:
                    db.session.add(video)  # Adds new video record to database
                    db.session.commit()  # Commits all changes
                    print('[INFO] Ok add new video record ')
                except:
                    # in case video name already exists
                    print('[ERROR] video name already exists.')
                  

                print('[INFO] delete temp video file ')
            f.close()
    return render_template('home/manual.html',title='WebRobot')

 # close camera from automatic state
def close_camera(task):   
    global camera

    if task=='open':
        if camera is None or not camera.isOpened():
            if os.environ.get('WERKZEUG_RUN_MAIN') or Flask.debug is False:
                camera = cv2.VideoCapture(0)
        
    elif task=='stop':
        if camera is not None or camera.isOpened():
            camera.release()
            cv2.destroyAllWindows()

    return render_template('home/automatic.html',title='WebRobot')


#Travel to one station 
def drive_station(station,route,if_secur,userId):
    global camera,move,start_time,exits,right,left,distanc,status_key
    exits=1
    if camera is None or not camera.isOpened():
        print('Warning: unable to open video source: ')
        #if os.environ.get('WERKZEUG_RUN_MAIN') or Flask.debug is False:
        camera = cv2.VideoCapture(0)
    while camera.isOpened() and exits==1:
        print('[INFO] drive_station'+ str(station) + '!')
        ret,frame = camera.read()
        if not ret:
            break
        #import pdb; pdb.set_trace()
        ret,frame = camera.read()
        dictionary = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
        parameters =  cv2.aruco.DetectorParameters_create()
        corners,Ids,rejected = cv2.aruco.detectMarkers(frame, dictionary, parameters=parameters)
        sensor_left=False
        sensor_middle=False
        sensor_right=False
         

        t= Thread(target=distance)
        t.start()
        if( distanc < 5):
                stop()
                ts=datetime.datetime.now().strftime("%m %d %Y.%H:%M:%S%p")
                # open a file to read
                f=open(conf_path)
                data=json.load(f)
                if data["use_dropbox"]:
				# write the image to temporary file                  			
                    t = TempImage()
                    cv2.imwrite(t.path, frame)
					# upload the image to Dropbox and cleanup the tempory image
                    print("[UPLOAD] {}".format(ts))
                    path = "/{base_path}/{timestamp}.jpg".format(
                    base_path=data["dropbox_base_path"], timestamp=ts)
                    name_photo="{timestamp}.jpg".format(timestamp=ts)
                    client.files_upload(open(t.path, "rb").read(), path)
                    user=User.query.filter(User.id==userId).first()
                    print("[INFO] send email")
                    send_email_route1_photo(route,user,t.path)
                    send_email_admin_obstacle_photo(route,t.path)
                    print('[INFO] capture:userid,path :',userId,path)
                    photo=Photo(name=name_photo,user_id=userId,route_id=route.id)    
                    try:
                        db.session.add(photo)  # Adds new image record to database
                        db.session.commit()  # Commits all changes
                        print('[INFO] Add into db - new image')
                    except:
                    # in case image name already exists
                        print('[ERROR] image name already exists.')    
                    t.cleanup() 
                f.close()
                a="Obstacle before me, please help me"
                message='espeak -ven+m7 -k5 -s150 --punct="<characters>" "%s" 2>>/dev/null' % a 
                execute_unix(message)
                time.sleep(0.1)
                message="Note, route number is:"+(route.name)+". Obstacle before me, please help me"
                user=User.query.filter(User.id==userId).first()
                #send_sms_user_message(message,user.name,user.phone)
                
                leds_turn("all")
                while(1):
                    status_key=1
                    key_identification_and_waiting()
                    if(status_key != 1):
                        break
                    print (status_key)
                if(status_key==2):
                   ###Write log
                    end_of_route_number(route,1,userId)     
        else:
                sensor_left=bool(GPIO.input(16))
                sensor_middle=bool(GPIO.input(6))
                sensor_right=bool(GPIO.input(5))
                try:
                   if (not sensor_left and not sensor_middle and not sensor_right):
                      #stop()
                      #time.sleep(0.002)
                      if(drive_to_station(corners,Ids,start_time,station,route)):
                         move = 1
                         start_time = time.time()
                      if(if_secur==True):
                         face_recog(route,frame,userId)
                      #backward()
                      #time.sleep(0.5)
                      print("case 1")

                   elif (not sensor_left and not sensor_middle and sensor_right):
                        #stop()
                        #time.sleep(0.02)
                        turn_right()
                        print("case 2")
        
                   elif (not sensor_left and sensor_middle and not sensor_right):
                        #stop()
                        #time.sleep(0.02)
                        if(drive_to_station(corners,Ids,start_time,station,route)):
                           move = 1
                           start_time = time.time()
                        if(if_secur==True):
                           face_recog(route,frame,userId)
                        forward()
                        #time.sleep(1) 
                        print("case 3")
                 
                   elif (not sensor_left and sensor_middle and sensor_right):
                       #stop()
                       #time.sleep(0.02)
                       if(drive_to_station(corners,Ids,start_time,station,route)):
                          move = 1
                          start_time = time.time()
                       if(if_secur==True):
                          face_recog(route,frame,userId)
                       turn_right()

                       print("case 4")
            
                   elif (sensor_left and not sensor_middle and not sensor_right):
                       #stop()
                       #time.sleep(0.02)
                       turn_left()
                       print("case 5")
               
                   elif (sensor_left and not sensor_middle and sensor_right):
                      #stop()
                      #time.sleep(0.02)
                      turn_right()
                      print("case 6")
            
                   elif (sensor_left and sensor_middle and not sensor_right):
                      #stop()
                      #time.sleep(0.02)
                      if(drive_to_station(corners,Ids,start_time,station,route)):
                         move = 1
                         start_time = time.time()
                      if(if_secur==True):
                         face_recog(route,frame,userId)
                      turn_left()
                      print("case 7")
                
                   elif (sensor_left and sensor_middle and sensor_right):   
                      if(drive_to_station(corners,Ids,start_time,station,route)):
                         move = 1
                         start_time = time.time()
                      if(if_secur==True):
                         face_recog(route,frame,userId)
                      print("case 8")
              
                   else:
                      print("error occured while driving!!")
            #manual_stop()
           
                except KeyboardInterrupt:
                    print ('KeyboardInterrupt exception is caught')    
             
#exits=0 


def face_recog(route,frame,userId):
    faces = face_patter.detectMultiScale(frame,scaleFactor=1.1,
    minNeighbors=5,minSize=(80, 80))
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        timestamp = datetime.datetime.now()
        ts=timestamp.strftime("%m %d %Y.%H:%M:%S%p")
        t = TempImage()
        cv2.imwrite(t.path, frame)
        user=User.query.filter(User.id==userId).first()
        send_email_route_photo(route,user,t.path)
        print("hi hi")
        if_route_sec=1
        t.cleanup()
        break
            
def find_marker(corners,Ids,station):
    global move
    if(Ids is not None):
        #stop()
        for i in Ids:
            if(i[0]==station):
                #find pose estimation vectors
                rvecs, tvecs, _objPoints = cv2.aruco.estimatePoseSingleMarkers(corners, 0.1, cameraMatrix, distCoeffs)
                #calculate size of vectors
                mean = math.sqrt(math.pow(tvecs[0][0][0],2) + math.pow(tvecs[0][0][1],2)+ math.pow(tvecs[0][0][2],2))
                print('[INFO]', mean)
                if (mean<0.9):
                    move = 1
                    return move
                return move
        return move
    return move
            
def find_marker_card(Ids,card):
    if(Ids is not None):
        #stop()
        for i in Ids:
            if(i[0]==card):
                return True
        return False
    return False
    
#travel to one station    
def drive_to_stat(corners,Ids,start_time,station,route):
    global exits,move
    if not move:
        if (find_marker(corners,Ids,station)):
            return True
    else:
        print(time.time() - start_time)
        if((time.time() - start_time)>3):
            stop()
            print('arrived to ', station, 'successfuly')
            route.status_id=1
            db.session.commit()  # Commits all changes
            print('[INFO] Update of route status - OK')
            a="Route is done."
            message='espeak -ven+m7 -k5 -s150 --punct="<characters>" "%s" 2>>/dev/null' % a 
            execute_unix(message)
            time.sleep(0.1) 
            exits=0
        return False

def end_of_route_number(route,check_route,userId):
    global if_route_sec,status_key
    if(check_route==1 and checkRoute(route,userId)):
        if(status_key==2):
            log_user=LogUser(fault_id=3,route_id=route.id)
            db.session.add(log_user)
            
        print('[INFO] The route:' + str(route.id)+' failed ...')
        a="The route failed. Please check the history of routes"
        message='espeak -ven+m7 -k5 -s150 --punct="<characters>" "%s" 2>>/dev/null' % a 
        execute_unix(message)
        time.sleep(0.5)
        route.status_id=4
    else:
        print('[INFO] Route '+str(route.id )+ ' completed successfully') 
        a="Route is done."
        message='espeak -ven+m7 -k5 -s150 --punct="<characters>" "%s" 2>>/dev/null' % a 
        execute_unix(message)
        time.sleep(0.5)
        route.status_id=1
        #++++
        #
        leds_turn("all")
    db.session.commit()  # Commits all changes
    print('[INFO]: update status of route (db) - OK')
    time.sleep(0.5)
    if(if_route_sec==1):
        print("if_route_sec")
        try:
            user=User.query.filter(User.id==userId)
            send_sms_user_photo(route,user.name,user.phone)
        except:
            print('[ERROR] Name of user wrong')
        if_route_sec=0
    back_to_basic_station()
    #manual_stop()
    return

def back_to_basic_station():
    while(True):
        sensor_back()       
        a="Robot arrived at base station"
        message='espeak -ven+m7 -k5 -s150 --punct="<characters>" "%s" 2>>/dev/null' % a 
        execute_unix(message)
        break;
       
            
#trave to many stations     
def drive_stations(stations,route,if_secur,userId):
    global camera,move,start_time,exits,Stop_router
    
    #Stopping conditions - high temperature 
    Stop_router=0
    #+++++
    leds_turn("yellow")
    #drive_black=Drive(24,23,17,27,16,5,6,18,12,22,4 )
    for station in stations:
        #Drive to the station 
        exits=1
        
        if(Stop_router==1):
            end_of_route_number(route,Stop_router,userId)
        
        while (exits and not(Stop_router)):
            #import pdb; pdb.set_trace()
            if camera is None or not camera.isOpened():
                print('[Warning]: unable to open video source: ')
                if os.environ.get('WERKZEUG_RUN_MAIN') or Flask.debug is False:
                    camera = cv2.VideoCapture(0)
            drive_station(station,route,if_secur,userId)  

         
    end_of_route_number(route,Stop_router,userId)    
                
#travel to many stations
def drive_to_station(corners,Ids,start_time,station,route):
    global exits,camera,vs,move,Stop_router
    if not move:
        if (find_marker(corners,Ids,station)):
            return True
    else:
        print(time.time() - start_time)
        if((time.time() - start_time)>3):
            stop()
            print('[INFO] arrived to ', station, 'successfuly')
            #+++++
            leds_turn("blue")
            #+++++
            a="You arrived at the station number is "+str(station)
            message='espeak -ven+f5 -k5 -s150 --punct="<characters>" "%s" 2>>/dev/null' % a 
            execute_unix(message)
            time.sleep(0.1)    
            pygame.mixer.music.load('/home/webrgacv/webrobotapp/app/home/audio/success.wav')
            pygame.mixer.music.play(2)
            print('[INFO] Update status of station')
                
            station_q=RouteStation.query.filter(RouteStation.route_id==route.id,RouteStation.station_id==(station+1)).first()
            station_q.is_Done=True
            station_q.date_end = datetime.datetime.now()
                
            if camera is None or not camera.isOpened(): 
                if os.environ.get('WERKZEUG_RUN_MAIN') or Flask.debug is False:
                    camera = cv2.VideoCapture(0)
                    start_measured_time = time.time()
            else:
                start_measured_time = time.time()
                
            while camera.isOpened():
                ret, frame = camera.read()
                if not ret:
                    break
                dictionary = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_250)
                parameters=  cv2.aruco.DetectorParameters_create()
                corners,Ids,rejected = cv2.aruco.detectMarkers(frame, dictionary, parameters=parameters)
                if Ids is not None:
                    tag = np.zeros((300, 300, 1), dtype="uint8")
                    cv2.aruco.drawMarker(dictionary, int(Ids), 300, tag, 1)
                    if int(Ids)==int(station)+100 or int(Ids)==200:
                        if int(Ids)==200 :
                            message="master key was displayed"
                        else:
                            message="user showed correct code"
                        #++++++
                        leds_turn("green")
                        #+++++
                        print('[INFO] Find zero marker')
                        station_q.is_Open= True
                        a="Success" + message
                        message='espeak -ven+f5 -k5 -s150 --punct="<characters>" "%s" 2>>/dev/null' % a 
                        execute_unix(message)
                        time.sleep(1.0) 
                        pygame.mixer.music.load('/home/webrgacv/webrobotapp/app/home/audio/success.wav')
                        pygame.mixer.music.play(2)
                        while pygame.mixer.music.get_busy() == True:
                            continue
                        break
                
                #timer past play error sound and continue
                if ((time.time() - start_measured_time) >55):
                    print('[INFO] timeout!!')
                    pygame.mixer.music.load('/home/webrgacv/webrobotapp/app/home/audio/fail.wav')
                    pygame.mixer.music.play(2)
                    while pygame.mixer.music.get_busy() == True:
                        continue
                    a="Timeout"
                    message='espeak -ven+m7 -k5 -s150 --punct="<characters>" "%s" 2>>/dev/null' % a 
                    execute_unix(message)
                    #++++++
                    leds_turn("red")
                    #++++++
                    time.sleep(0.5)
                    break
                 
               
            #key_identification_and_waiting(station,Route)
            db.session.commit()
            temp=temperature_of_raspberry_pi()
            temp=float(temp)
            if(temp > 70):
                Stop_router=1
                route_fault=LogUser(fault_id=1,route_id=route.id)
                db.session.add(route_fault)
                db.session.commit()
                #++++++
                leds_turn("red")
                        
            print('[INFO] driving to next station')
            exits=0  
            move = 0
            return False        
        return False
    return False
def key_identification_and_waiting():
    global status_key,camera
    if camera is None or not camera.isOpened(): 
       if os.environ.get('WERKZEUG_RUN_MAIN') or Flask.debug is False:
          camera = cv2.VideoCapture(0)
          start_measured_time = time.time()
    else:
        start_measured_time = time.time()           
    while camera.isOpened():
       ret, frame = camera.read()
       if not ret:
          break
       dictionary = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_250)
       parameters=  cv2.aruco.DetectorParameters_create()
       corners,Ids,rejected = cv2.aruco.detectMarkers(frame, dictionary, parameters=parameters)
       if Ids is not None:
          tag = np.zeros((300, 300, 1), dtype="uint8")
          cv2.aruco.drawMarker(dictionary, int(Ids), 300, tag, 1)
          if int(Ids)==200:
              a="You saved me, please direct me to the black line "
              message='espeak -ven+f5 -k5 -s150 --punct="<characters>" "%s" 2>>/dev/null' % a
              execute_unix(message)
              time.sleep(1.0)  
               #++++++
              leds_turn("green")
                #+++++
              print('[INFO] Find zero marker')
              a="Success" + message
              message='espeak -ven+f5 -k5 -s150 --punct="<characters>" "%s" 2>>/dev/null' % a 
              execute_unix(message)
              time.sleep(1.0) 
          pygame.mixer.music.load('/home/webrgacv/webrobotapp/app/home/audio/success.wav')
          pygame.mixer.music.play(2)
          status_key=0
          while pygame.mixer.music.get_busy() == True:
             continue
          break
                
       #timer past play error sound and continue
       if ((time.time() - start_measured_time) >55):
           print('[INFO] timeout!!')
           pygame.mixer.music.load('/home/webrgacv/webrobotapp/app/home/audio/fail.wav')
           pygame.mixer.music.play(2)
           while pygame.mixer.music.get_busy() == True:
              continue
           a="Timeout"
           message='espeak -ven+m7 -k5 -s150 --punct="<characters>" "%s" 2>>/dev/null' % a 
           execute_unix(message)
           status_key=2
           #++++++
           leds_turn("red")
           #++++++
           time.sleep(0.5)
           break
                        
def checkRoute(route,userId):
    route_check=RouteStation.query.filter(RouteStation.route_id==route.id
                                         ,RouteStation.is_Done==0 or RouteStation.is_Open==0).all()
    user=User.query.filter(User.id==userId).first()
    if (route_check is not None):                                         
        message="Note, route number is:"+(route.name)+" is fails"
        send_sms_user_message(message,user.name,user.phone)
        send_sms_admin_message(route.name)
        return True
    return False

########
# DROPBOX
########

def dropbox_folder_from_photos(photos):
  global tempFolder
  delete_files_from_images()
  f=open(conf_path)
  data=json.load(f)
  if data["use_dropbox"]:
     print('[INFO] using dropbox')
     tempFolder = TempFolder()
     myDir =   client.files_list_folder("/rpi_uploaderP/Photos/")
     for item in myDir.entries:

        if isinstance(item, dropbox.files.FileMetadata):
            for photo in photos:
                if item.name == photo.name:
                    client.files_download_to_file(tempFolder.path+item.name, item.path_lower)
  f.close()       
  path='/home/webrgacv/webrobotapp/app/static/images/Temp'
  
  filenames = os.listdir(path)
 
  for filename in filenames:
    try:
       os.rename(filename, filename.replace(' ', '-').lower())    
    except:
       continue
  
def dropbox_folder_from_videos(videos):
  global tempFolderV
  delete_files_from_videos()
  f=open(conf_path)
  data=json.load(f)
  if data["use_dropbox"]:
     tempFolderV = TempFolderV()   
     myDir =   client.files_list_folder("/rpi_uploaderP/Videos/")
     for item in myDir.entries:

        if isinstance(item, dropbox.files.FileMetadata):
            for video in videos:
                if item.name == video.name:  
                    client.files_download_to_file(tempFolderV.path+item.name, item.path_lower)
  f.close() 

  path='/home/webrgacv/webrobotapp/app/static/videos/Temp'
  
  filenames = os.listdir(path)

  for filename in filenames:
    try:
      os.rename(filename, filename.replace(' ','-').lower())    
    except:
       continue
  
  for filename in filenames:
    try:
       _format= ''
       if ".avi" in filename.lower():
           _format=".avi"
       if ".mp4" in filename.lower():
           _format =".mp4"
          
       if  filename.endswith("avi"):
          inputfile=os.path.join(path,filename)
          outputfile=os.path.join(path,filename.lower().replace(_format,".mp4"))
          subprocess.call(['ffmpeg', '-i', inputfile, outputfile])
    except:
        print('[ERROR] not change format of video file from avi to mp4')
        continue
  
  required_files = glob.glob(path+"/*.avi") # This gives all the files that matches the pattern

  results = [os.remove(x) for x in required_files]


#delete all photos from folder /static/images/Temp        
def delete_files_from_images():
    tempFolder = TempFolder() 
    tempFolder.cleanup()

#delete all videos from folder /static/videos/Temp 
def delete_files_from_videos():
    tempFolderV = TempFolderV() 
    tempFolderV.cleanup()

#delete current file (photo) from folder
def  delete_file_from_images(file_name):
    tempFolder = TempFolder() 
    tempFolder.cleanupFile(file_name)
    
#delete current file (video) from folder
def  delete_file_from_videos(file_name):
    tempFolderV = TempFolderV() 
    tempFolderV.cleanupFile(file_name)

#delete current file (photo) from dropbox
def delete_photo_from_dropbox(file_name):
    delete_file_from_images(file_name)
    f=open(conf_path)
    data=json.load(f)
    if data["use_dropbox"]:
         path="/rpi_uploaderP/Photos/"+file_name
         client.files_delete(path)
         print('[INFO] image file delete from dropbox')
    f.close()
         
#delete current file (video) from dropbox
def delete_video_from_dropbox(file_name):
    delete_file_from_videos(file_name)
    file_name=file_name.replace("mp4","avi")
    f=open(conf_path)
    data=json.load(f)
    if data["use_dropbox"]:
         path="/rpi_uploaderP/Videos/"+file_name
         client.files_delete(path)
         print('[INFO] video file delete from dropbox')
    f.close()

#define robot driving functions
def forward():
    print("forward")
  
    GPIO.output(mA1,GPIO.LOW)
    GPIO.output(mA2,GPIO.HIGH)
    GPIO.output(mB1,GPIO.LOW)
    GPIO.output(mB2,GPIO.HIGH)
    return 'true'

def turn_left():
    print("left")
    GPIO.output(mA1,GPIO.HIGH)
    GPIO.output(mA2,GPIO.LOW)
    GPIO.output(mB1,GPIO.LOW)
    GPIO.output(mB2,GPIO.HIGH)
    return 'true'

def turn_right():
    print("right")
    GPIO.output(mA1,GPIO.LOW)
    GPIO.output(mA2,GPIO.HIGH)
    GPIO.output(mB1,GPIO.HIGH)
    GPIO.output(mB2,GPIO.LOW)
    return 'true'

def stop():
    print("stop")
    GPIO.output(mA1,GPIO.LOW)
    GPIO.output(mA2,GPIO.LOW)
    GPIO.output(mB1,GPIO.LOW)
    GPIO.output(mB2,GPIO.LOW)
    return 'true'

def backward():
    print("backward")

    GPIO.output(mA1,GPIO.HIGH)
    GPIO.output(mA2,GPIO.LOW)
    GPIO.output(mB1,GPIO.HIGH)
    GPIO.output(mB2,GPIO.LOW)
    return 'true'

def backwardLeft():
    GPIO.output(mA1, GPIO.HIGH)
    GPIO.output(mA2, GPIO.LOW)
    GPIO.output(mB1, GPIO.LOW)
    GPIO.output(mB2, GPIO.LOW)
 

def backwardRight():
    GPIO.output(mA1, GPIO.HIGH)
    GPIO.output(mA2, GPIO.LOW)
    GPIO.output(mB1, GPIO.LOW)
    GPIO.output(mB2, GPIO.LOW)
    
def rotate():
    global p1,p2
    p1.start(50)
    p2.start(50)
    GPIO.output(mA1,GPIO.LOW)
    GPIO.output(mA2,GPIO.HIGH)
    GPIO.output(mB1,GPIO.HIGH)
    GPIO.output(mB2,GPIO.LOW)
    time.sleep(0.3)
    GPIO.output(mA1,GPIO.LOW)
    GPIO.output(mA2,GPIO.LOW)
    GPIO.output(mB1,GPIO.LOW)
    GPIO.output(mB2,GPIO.LOW)
    time.sleep(0.4)
    p1.start(32)
    p2.start(32)
    return 

def execute_unix(inputcommand):
   p = subprocess.Popen(inputcommand, stdout=subprocess.PIPE, shell=True)
   (output, err) = p.communicate()
   return output


      
                
def sensor_back():
    while(True):
       try:
           sensor_right=False
           sensor_middle=False
           sensor_left=False
           p1.start(40)
           p2.start(40)
           
           sensor_right=bool(GPIO.input(5))
           sensor_middle=bool(GPIO.input(6))
           sensor_left=bool(GPIO.input(16))
           
           if((not sensor_left and not sensor_middle and sensor_right) or (not sensor_left and sensor_middle and sensor_right)):
              print("state 001-1")
              while(True):
                 sensor_right=bool(GPIO.input(5))
                 sensor_middle=bool(GPIO.input(6))
                 sensor_left=bool(GPIO.input(16))
                 if(not sensor_left and not sensor_middle and sensor_right):
                    #stop()
                    #time.sleep(0.2)
                    print("state 001")
                    turn_right()

                 elif (not sensor_left and sensor_middle and not sensor_right):
                    forward()
                    print("state 010")

                 elif (not sensor_left and sensor_middle and sensor_right):
                    turn_right()
                    print("state 011")

                 elif (sensor_left and not sensor_middle and not sensor_right):
                    print("state 100")
                    turn_left()

                 elif (sensor_left and not sensor_middle and sensor_right):
                    print("state 101")
                    turn_right()

                 elif (sensor_left and sensor_middle and not sensor_right):
                    turn_left()
                    print("state 110")

                 elif (sensor_left and sensor_middle and sensor_right):
                    stop()
                    print("robot arrived at base station")
                    a="Robot arrived at base station"
                    message='espeak -ven+m7 -k5 -s150 --punct="<characters>" "%s" 2>>/dev/null' % a 
                    execute_unix(message)
                
                    return 
                 else:
                     print("dont care")
           else:
              rotate()
          
       except KeyboardInterrupt:
           print ('KeyboardInterrupt exception is caught')
  
        
def manual_stop():
    stop()


def leds_turn(led_color):
    if(led_color=="red"):
        for i in range (3):
           GPIO.output(led_red,1)
           time.sleep(1)
           GPIO.output(led_red,0)
    elif (led_color=="blue"):
        for i in range (3):
           GPIO.output(led_blue,1)
           time.sleep(1)
           GPIO.output(led_blue,0)
    elif (led_color=="green"):
        for i in range (3):
           GPIO.output(led_green,1)
           time.sleep(1)
           GPIO.output(led_green,0)
    elif (led_color=="yellow"):
        for i in range (3):
           GPIO.output(led_yellow,1)
           time.sleep(1)
           GPIO.output(led_yellow,0)
    elif (led_color=="all"):
        for i in range (3):
           GPIO.output(led_yellow,1)
           GPIO.output(led_green,1)
           GPIO.output(led_blue,1)
           GPIO.output(led_red,1)
           time.sleep(1)
           GPIO.output(led_yellow,0)
           GPIO.output(led_green,0)
           GPIO.output(led_blue,0)
           GPIO.output(led_red,0)
           time.sleep(1)
           

 