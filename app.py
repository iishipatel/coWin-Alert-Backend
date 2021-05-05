from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import requests
import json
from google.oauth2 import service_account

from timeloop import Timeloop
from datetime import timedelta
import time

from flask import Flask
from flask_mail import Mail, Message
import os

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'keys.json'

creds = None
creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)


# The ID spreadsheet.
SAMPLE_SPREADSHEET_ID = '1IPTEcHSSzUKR20Eb0VEl4k25xe_o77yidjorYs5ynFI'

service = build('sheets', 'v4', credentials=creds)

# flask app set up
app = Flask(__name__)
mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": 'abc@mail.com',
    "MAIL_PASSWORD": 'password'
}

app.config.update(mail_settings)
mail = Mail(app)

tl = Timeloop()

def send_mail(name,email,zipcode,date):
    api='https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode='+zipcode+'&date='+date
    r=requests.get(api)
    api_result=r.json()

    msg = Message(subject="[ALERT] Vaccination Slots Near You",
                sender=app.config.get("MAIL_USERNAME"),
                recipients=[email])
    msg.body = 'Hi '+ name +'\n'+'This to inform you that the following center have slots available for you:\n \n Log On to https://www.cowin.gov.in/home ASAP \n \n'
    flag=0
    for x in range (len(api_result["centers"])):
        if api_result["centers"][x]["sessions"][0]["available_capacity"]>0 and api_result["centers"][x]["sessions"][0]["min_age_limit"]==45:
            msg.body+='Name: '+ api_result["centers"][x]["name"]+'\n PinCode: '+str(api_result["centers"][x]["pincode"])+'\n Age Limit: '+str(api_result["centers"][x]["sessions"][0]["min_age_limit"])+'\n Date: '+date+'\n Vaccine: '+api_result["centers"][x]["sessions"][0]["vaccine"]+'\n Fee Type: '+api_result["centers"][x]["fee_type"]+'\n Available Capacity: '+str(api_result["centers"][x]["sessions"][0]["available_capacity"])+'\n \n'
            flag=1
    if flag!=0:
        mail.send(msg)

        
def update_list():
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range="A1:E10").execute()
    values = result.get('values', [])
    for x in range (1,len(values)):
        name=values[x][1]
        email=values[x][2]
        zipcode=values[x][3]
        date=values[x][4].split('/')
        if (len(date[0])==2) and (len(date[1])==2):
            date=date[1]+'-'+date[0]+'-'+date[2]
        elif (len(date[0])==1) and (len(date[1])==2):
            date=date[1]+'-0'+date[0]+'-'+date[2]
        elif (len(date[0])==2) and (len(date[1])==1):
            date='0'+date[1]+'-'+date[0]+'-'+date[2]
        else:
            date='0'+date[1]+'-0'+date[0]+'-'+date[2]
        send_mail(name,email,zipcode,date)
        print (name,email,zipcode,date)
        

if __name__ == '__main__':
    with app.app_context():
        while True:
            update_list()
            time.sleep(100)
                
            





