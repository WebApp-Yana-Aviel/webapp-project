
import time, datetime
import telepot
import json
from telepot.loop import MessageLoop
import os, subprocess
import RPi.GPIO as IO
import time
import sqlite3
from time import sleep

now = datetime.datetime.now()
IO.setwarnings(False)
conf_path='/home/webrgacv/webrobotapp/app/home/conf/telebot.json'

IO.setmode (IO.BCM)      
IO.setup(26,IO.OUT)
IO.setup(25,IO.OUT)
IO.setup(13,IO.OUT)
IO.setup(20,IO.OUT)       

def action(msg):
    chat_id = msg['chat']['id']
    command = msg['text']
    print ('Received: %s' % command)
    if command == '/hi':
        telegram_bot.sendMessage (chat_id, str("Hi! Admin"))
    elif command == '/time':
        telegram_bot.sendMessage(chat_id, str(now.hour)+str(":")+str(now.minute))
    elif command == '/temp':
        temp = subprocess.run('vcgencmd measure_temp', shell=True, encoding='utf-8', stdout=subprocess.PIPE).stdout.split('=')
        temp = temp[1].replace("'C\n",'')
        telegram_bot.sendMessage(chat_id, str("Temperature: ")+str(temp)+str("C"))
    elif command == '/freq':
        freq = subprocess.run('vcgencmd measure_clock arm', shell=True, encoding='utf-8', stdout=subprocess.PIPE).stdout.split('=')
        freq = int(freq[1].replace('\n', '')) / 1000000
        telegram_bot.sendMessage(chat_id, str("Freq : ")+str(freq)+str("MHz"))
    elif command == '/volt':
        volt = subprocess.run('vcgencmd measure_volts', shell=True, encoding='utf-8', stdout=subprocess.PIPE).stdout.split('=')
        volt = volt[1].replace('\n', '')
        telegram_bot.sendMessage(chat_id, str("Volt : ")+str(volt))
    elif command == '/restart':
        telegram_bot.sendMessage(chat_id, str("Rebooting"))
        os.system("sudo reboot")
        
    elif command == '/disk':
        result=subprocess.check_output("df -h .", shell=True ,encoding='utf-8')
        output=result.split()  
        telegram_bot.sendMessage(chat_id, str("Disk space:\nTotal:")+str(output[8])+str("\nUsed:")
                                 + str(output[9])+str(" ")+str( output[11])+str("\nFree:")+str(output[10]))
    elif command == '/turn on':
        #IO.output(40,1)
        for i in range (5):
           IO.output(25,1)
           IO.output(26,1)
           IO.output(13,1)  
           IO.output(20,1)
    elif command == '/turn off':
           IO.output(25,0)
           IO.output(26,0)
           IO.output(13,0)
           IO.output(20,0)
    elif command=="/help":
         message="commads : \n\
         /time: time now \n \
         /temp: temperature of raspberry pi \n\
         /freq: frequency of raspberry \n\
         /volt: voltage of raspberry \n\
         /disk: disk space of raspberry \n\
         /turn on: turn on yellow leds \n\
         /turn off: turn off yellow leds \n\
         /routes_fault: turn off yellow leds \n\
         /reboot :reboot of raspberry pi \n\
         /shutdown :shutdown of raspberry pi \n\
         /proc :shows the reasons for the decrease in processor performance:\n \
            -Bit0 & nbsp;- low voltage \n\
            -Bit 1 - manual frequency limiting \n\
            -Bit 2 - processor performance is currently degraded \n\
            -Bit 3 - processor overheating \n\
            -Bit 16 - in this session was once degraded due to power problems, low voltage\n\
            -Bit 17 -in this session was once degraded due to manual frequency limiting \n\
            -Bit 18 -in this session was once degraded.\n\
            -Bit 19 -in this session was once degraded due to processor overheating "
         telegram_bot.sendMessage (chat_id, str(message))
    elif command=="/proc":
        proc = subprocess.run('vcgencmd get_throttled', shell=True, encoding='utf-8', stdout=subprocess.PIPE).stdout.split('=')
        telegram_bot.sendMessage(chat_id, str("Processor performance:") + str (proc))
    elif command=="/routes_fault":
        count=0
        date_now=datetime.datetime.now()
        conn=sqlite3.connect('dev_app.db',check_same_thread=False)
        cursor=conn.cursor()
        SQL="SELECT * from routes where status_id='2'"
        cursor.execute(SQL)
        myResult=cursor.fetchall()
        conn.close()
        if (myResult is not None):
            for route in myResult:
               date_route=date_now-route.date_start
               min_in_day=24*60*60
               if(divmod(date_route.days*min_in_day+date_route.seconds,60)[0]>20):
                   ++count
        
        telegram_bot.sendMessage(chat_id, str("Number routes is fault : ")+ str(count))
  
    elif command=="/shutdown":
        telegram_bot.sendMessage(chat_id, str("Shutdown now...."))
        os.system("sudo shutdown -now")
        
    else:
        telegram_bot.sendMessage(chat_id, str("Wrong request"))

        
f=open(conf_path)
data=json.load(f)
if data["use_telebot"]:
    telegram_bot = telepot.Bot(data["telebot_id"])
    print (telegram_bot.getMe()) 
f.close()
print (telegram_bot.getMe())
try:
    MessageLoop(telegram_bot, action).run_as_thread()
    print ('Up and Running....')
    while 1:
       time.sleep(5)
except KeyboardInterrupt:  
    # here you put any code you want to run before the program   
    # exits when you press CTRL+C  
    print("[INFO] Exits CTRL+C")  
  
except:  
    # this catches ALL other exceptions including errors.   
    print ("Other error or exception occurred!")  
  
finally:  
    IO.cleanup() # this ensures a clean exit


    
    