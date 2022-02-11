import json
from twilio.rest import Client
import sqlite3

conf_path="/home/webrgacv/webrobotapp/app/home/conf/twilio.json"

def send_sms_admin_message(temp):
    message_temp="Raspberry temperature is very high  > 70 C ....."
    conn=sqlite3.connect('produc_app.db',check_same_thread=False)
    cursor=conn.cursor()
    SQL="SELECT phone from users where name like 'admin'"
    cursor.execute(SQL)
    myRes=cursor.fetchone()[0]
    conn.close()
    if (myRes is None):
        phone='+972549111254'
    else:
        phone=myRes
    print(phone)
    # check to see if the Twilio should be used
    f=open(conf_path)
    data=json.load(f)
    if data["use_twilio"]:    
        client = Client(data["account_sid"],data["auth_token"]) 
        message = client.messages.create( 
                              from_='+972526987310',  
                              body='Hi, admin! '+message_temp+str(temp)+' C',     
                              to=str(phone)
                          )
    f.close()
    
    
