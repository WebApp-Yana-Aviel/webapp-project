import os
import time
from sendMessage import send_sms_admin_message

def temperature_of_raspberry_pi():
    cpu_temp = os.popen("vcgencmd measure_temp").readline()
    cpu_temp = cpu_temp.replace("temp=", "")
    cpu_temp = cpu_temp.replace("'C\n", "")
    return cpu_temp

 
while True:
    time.sleep(5)
    temp=float(temperature_of_raspberry_pi())
    if(temp > 79):
      message="Hi admin! Temperature is:" + str(temp)+"!!!!"
      send_sms_admin_message(message)
      print(temperature_of_raspberry_pi())
    
