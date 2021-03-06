import cv2
import sys
import time
import os
import logging as log
import datetime as dt
from time import sleep
import paho.mqtt.client as mqtt
import threading



def pub():
    flag=60
    while(True):
        if len(faces):
            client.publish("locksmith/detected","True")
            cv2.imwrite('cam.jpg',frame)
            if flag==60:
                os.system("echo \"Face Detected\" | mailx -A \"cam.jpg\" -s \"A person has entered your space\" "+addr)
                flag=0
            flag+=1
        else:
            client.publish("locksmith/detected","False")
        sleep(2)


cascPath = "haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascPath)
log.basicConfig(filename='webcam.log',level=log.INFO)

video_capture = cv2.VideoCapture(0)
anterior = 0

client = mqtt.Client()
client.connect(host="eclipse.usc.edu", port=11000, keepalive=60)
client.loop_start()

state=1

global addr
addr=input("Enter email address: ")

while True:
    if not video_capture.isOpened():
        print('Unable to load camera.')
        sleep(5)
        pass
    # Capture frame-by-frame
    global frame
    ret, frame = video_capture.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    global faces
    faces= faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=5,
        minSize=(30, 30)
    )
    if state==1:
        state=0
    elif state==0:
        x=threading.Thread(target=pub)
        x.start()
        state=2
    
    # Draw a rectangle around the faces
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
    if anterior != len(faces):
        anterior = len(faces)
        log.info("faces: "+str(len(faces))+" at "+str(dt.datetime.now()))
    # Display the resulting frame
    cv2.imshow('Video', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    # Display the resulting frame
    cv2.imshow('Video', frame)
# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()
