import requests
import json
import argparse
import re
import time

# 初始化变量
parser = argparse.ArgumentParser()
parser.add_argument('--username', type=str, default=None)
parser.add_argument('--password', type=str, default=None)
parser.add_argument('--province', type=str, default=None)
parser.add_argument('--city', type=str, default=None)
parser.add_argument('--county', type=str, default=None)
parser.add_argument('--address', type=str, default=None)
parser.add_argument('--inprovince', type=str, default=None)
parser.add_argument('--incity', type=str, default=None)
parser.add_argument('--incounty', type=str, default=None)
parser.add_argument('--inaddress', type=str, default=None)
parser.add_argument('--isin', type=bool, default=False)
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
    # print(token, captcha)
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
    clockin_data = {"Temperature":36.5,
                    "RealProvince":args.inprovince if args.isin else args.province,
                    "RealCity":args.incity if args.isin else args.city,
                    "RealCounty":args.incounty if args.isin else args.county,
                    "RealAddress":args.inaddress if args.isin else args.address,
                    "IsUnusual": 0,
                    "UnusualInfo": "",
                    "IsTouch": 0,
                    "IsInsulated": 0,
                    "IsSuspected": 0,
                    "IsDiagnosis": 0,
                    "Content": None,
                    "IsViaHuBei": 0,
                    "IsViaWuHan": 0,
                    "IsInCampus": 1 if args.isin else 0,
                    "InsulatedAddress": "",
                    "TouchInfo": "",
                    "IsNormalTemperature": 1,
                    "BackState": 1 if args.isin else 0,
                    "MorningTemp": "36.5",
                    "NightTemp": "36.5",
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
    else:
        isSucccess = 1
    print(clockin.status_code, json.loads(clockin.text)['msg'])
    return isSucccess

while True:
    try:    
        a = main()
        if a == 0:
            break
        else:
            time.sleep(60)
    except:
        time.sleep(60)
