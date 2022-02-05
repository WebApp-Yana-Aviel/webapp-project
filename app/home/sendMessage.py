import json
from twilio.rest import Client

conf_path='/home/webrgacv/webrobotapp/app/home/conf/twilio.json'

def send_sms_admin_message(route):
    message_route="The route failed. Please check route number :"
    # check to see if the Twilio should be used
    f=open(conf_path)
    data=json.load(f)
    if data["use_twilio"]:    
        client = Client(data["account_sid"],data["auth_token"]) 
        message = client.messages.create( 
                              from_='+972526987310',  
                              body='Hi, admin! '+ message_route+str(route),     
                              to='972549111254'
                            
                          )
    f.close()
def send_sms_user_message(message,user_name,user_phone):
    f=open(conf_path)
    data=json.load(f)
    if data["use_twilio"]:    
        client = Client(data["account_sid"],data["auth_token"]) 
        message = client.messages.create( 
                              from_='+972526987310',  
                              body='Hi, '+user_name+'!' +message ,     
                              to=str(user_phone) )
    
    f.close()

def send_sms_user_photo(route,user_name,user_phone):
    f=open(conf_path)
    data=json.load(f)
    if data["use_twilio"]:    
        client = Client(data["account_sid"],data["auth_token"]) 
        message = client.messages.create( 
                              from_='+972526987310',  
                              body='Hi, '+user_name+'!' +'Route :'+str(route)+'. Please check your email.' ,     
                              to=str(user_phone) )
    
    f.close()
