import requests
import json
import argparse
import re
import smtplib
from email.mime.text import MIMEText

# 初始化变量
parser = argparse.ArgumentParser()
parser.add_argument('--username', type=str, default=None)
parser.add_argument('--password', type=str, default=None)
parser.add_argument('--province', type=str, default=None)
parser.add_argument('--city', type=str, default=None)
parser.add_argument('--county', type=str, default=None)
parser.add_argument('--address', type=str, default=None)
parser.add_argument('--mhost', type=str, default=None)
parser.add_argument('--muser', type=str, default=None)
parser.add_argument('--mpass', type=str, default=None)
parser.add_argument('--mrecv', type=str, default=None)
args = parser.parse_args()

def captchaOCR():
    captcha = ''
    token   = '' 
    while len(captcha) != 4:
        token = json.loads(requests.get('https://fangkong.hnu.edu.cn/api/v1/account/getimgvcode').text)['data']['Token']
        data = {
                'image_url': f'https://fangkong.hnu.edu.cn/imagevcode?token={token}',
                'type': 'https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic',
                'detect_direction': 'false'
                }
        captcha = requests.post('https://cloud.baidu.com/aidemo', data=data).json()['data']['words_result'][0]['words']
    print(token, captcha)
    return token, captcha
            
    while len(captcha) != 4:
        token = json.loads(requests.get('https://fangkong.hnu.edu.cn/api/v1/account/getimgvcode').text)['data']['Token']
        captcha = requests.post('https://cloud.baidu.com/aidemo', data=data).json()['data']['words_result'][0]['words']
    return token, captcha

def login():
    login_url = 'https://fangkong.hnu.edu.cn/api/v1/account/login'
    token, captcha = captchaOCR()
    login_info = {"Code":args.username,"Password":args.password,"VerCode":captcha,"Token":token}
    
    set_cookie = requests.post(login_url, json=login_info).headers['set-cookie']
    regex = r"\.ASPXAUTH=(.*?);"
    ASPXAUTH = re.findall(regex, set_cookie)[2]

    headers = {'Cookie': f'.ASPXAUTH={ASPXAUTH}; TOKEN={token}'}
    return headers

def main():
    clockin_url = 'https://fangkong.hnu.edu.cn/api/v1/clockinlog/add'
    headers = login()
    clockin_data = {"Temperature":36.50,
                    "RealProvince":args.province,
                    "RealCity":args.city,
                    "RealCounty":args.county,
                    "RealAddress":args.address,
                    "IsUnusual": 0,
                    "UnusualInfo": "",
                    "IsTouch": 0,
                    "IsInsulated": 0,
                    "IsSuspected": 0,
                    "IsDiagnosis": 0,
                    "Content": null,
                    "IsViaHuBei": 0,
                    "IsViaWuHan": 0,
                    "IsInCampus": 1,
                    "InsulatedAddress": "",
                    "TouchInfo": "",
                    "IsNormalTemperature": 1,
                    "BackState": 0.0,
                    "MorningTemp": null,
                    "NightTemp": null,
                    "QRCodeColor": "绿色",
                    "tripinfolist": [],
                    "toucherinfolist": [],
                    "dailyinfo":{"IsVia":"0","DateTrip":""},
                    "Longitude":None,
                    "Latitude":None
                    }

    clockin = requests.post(clockin_url, headers=headers, json=clockin_data)

    if clockin.status_code == 200:
        if '成功' in clockin.text or '已提交' in clockin.text:
            isSucccess = 0
        else:
            isSucccess = 1
            print(json.loads(clockin.text)['msg'])
    else:
        isSucccess = 1
    print('msg:', json.loads(clockin.text)['msg'])

    return isSucccess

def send_mail(info):
    mail_host = args.mhost
    mail_user = args.muser 
    mail_pass = args.mpass   
    sender = args.muser
    receivers = [args.mrecv]  

    message = MIMEText('', 'plain', 'utf-8')    
    message['Subject'] = '打卡' + info
    message['From'] = sender 
    message['To'] = receivers[0]  
    
    try:
        smtpObj = smtplib.SMTP() 
        smtpObj.connect(mail_host, 25)
        smtpObj.login(mail_user, mail_pass) 
        smtpObj.sendmail(sender, receivers, message.as_string()) 
        smtpObj.quit() 
        print('邮件发送成功')
    except smtplib.SMTPException as e:
        print('error', e)

for i in range(10):
    try:    
        a = main()
        if a == 0:
            send_mail('成功')
            break
        elif i == 9 and a == 1:
            send_mail('失败')
            raise valueerror("打卡失败")
        else:
            continue
    except:
        continue
