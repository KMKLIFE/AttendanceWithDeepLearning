from time import sleep
from edgetpu.classification.engine import ClassificationEngine
from edgetpu.utils import dataset_utils
from PIL import Image
import json
import picamera
import RPi.GPIO as GPIO
import datetime
import requests
import os

comebtn=27
leavebtn=22
host="https://2a8043f9.ngrok.io"
headers={'content-type':'application/json'}
filepath='/home/pi/edgetpu/retrain-imprinting2/'

labels = dataset_utils.ReadLabelFile(os.path.join(filepath,'Attendance_model2.txt'))
engine = ClassificationEngine(os.path.join(filepath,'Attendance_model2.tflite'))

camera=picamera.PiCamera()
print('camera made')




GPIO.setmode(GPIO.BCM)
GPIO.setup(comebtn,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(leavebtn,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

print('Start camera')
print('Press red btn or blue btn')

def comein(channel):
    saveFileName=datetime.datetime.now().strftime('%Y%m%d %H%M%c')+'.jpg'
    camera.capture(os.path.join('/home/pi/edgetpu/retrain-imprinting2/', saveFileName))
    print('camera capture')

    img = Image.open(os.path.join('/home/pi/edgetpu/retrain-imprinting2/', saveFileName))
    result = engine.ClassifyWithImage(img, top_k=3)
    print(result)
    result_first = result[0]
    print(result_first)
    name=result_first[0]
    print(name)
    acc=result_first[1]
    if(acc<0.6):
        print('error')
    else:
        name=int(name)
        label = labels[name]
        print(label)
        output = json.dumps({
            "name": label,
            "tag_type": "Come"
        })
        print(output)
        try:
            url=host+'/tag'
            response = requests.post(url, data=output, headers=headers)
            print(response)
        except Exception as ex:
            print(ex)
        else:
            print("Send Success")


def leaveout(channel):
    saveFileName = datetime.datetime.now().strftime('%Y%m%d %H%M%s') + '.jpg'
    camera.capture(os.path.join('/home/pi/edgetpu/retrain-imprinting2/', saveFileName))
    print('camera capture')

    img = Image.open(os.path.join('/home/pi/edgetpu/retrain-imprinting2/', saveFileName))
    result = engine.ClassifyWithImage(img, top_k=1)
    print(result)
    result_first = result[0]
    name = result_first[0]
    acc = result_first[1]
    if (acc < 0.6):
        print('error')
    else:
        name = int(name)
        label = labels[name]
        print(label)
        output = json.dumps({
            "name": label,
            "tag_type": "Leave"
        })
        print(output)
        try:
            url=host+'/tag'
            response = requests.post(url, data=output, headers=headers)
            print(response)
        except Exception as ex:
            print(ex)
        else:
            print("Send Success")





camera.resolution=(1920,1080)
camera.framerate=30
camera.start_preview(fullscreen=False,window=(0,0,1920,1080))
GPIO.add_event_detect(27, GPIO.RISING, callback=comein, bouncetime=1000)
GPIO.add_event_detect(22, GPIO.RISING, callback=leaveout, bouncetime=1000)


try:
    while(True):
        sleep(0.1)
except KeyboardInterrupt:
    print('interruput')
finally:
    camera.stop_preview()
    camera.close()
    GPIO.cleanup()
    print('final')