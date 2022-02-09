import os
import time

def temperature_of_raspberry_pi():
    cpu_temp = os.popen("vcgencmd measure_temp").readline()
    cpu_temp = cpu_temp.replace("temp=", "")
    cpu_temp = cpu_temp.replace("'C\n", "")
    return cpu_temp


