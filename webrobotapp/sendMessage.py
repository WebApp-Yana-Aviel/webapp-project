import json
from twilio.rest import Client
conf_path="/home/webrgacv/webrobotapp/app/home/conf/twilio.json"
def send_sms_admin_message(temp):
    message_temp="Raspberry temperature is very high  > 79 C ....."
    # check to see if the Twilio should be used
    f=open(conf_path)
    data=json.load(f)
    if data["use_twilio"]:    
        client = Client(data["account_sid"],data["auth_token"]) 
        message = client.messages.create( 
                              from_='+972526987310',  
                              body='Hi, admin! '+message_temp+str(temp)+' C',     
                              to='972549111254' 
                          )
    f.close()
    
    
def send_sms_user_message(message,user_name):
    f=open(conf_path)
    data=json.load(f)
    if data["use_twilio"]:    
        client = Client(data["account_sid"],data["auth_token"]) 
        message = client.messages.create( 
                              from_='+972526987310',  
                              body='Hi,! '+user_name+'!' +message ,     
                              to='972549111254' )
    f.close()
