import os
import datetime
import time
import pytz
import urllib
import http.cookiejar
import json
from typing import Dict, List, Any, Optional


time_zone = pytz.timezone('Europe/London')
username = os.environ['username']
password = os.environ['password']

def get_cfg()->Dict[str,Any]:
    cfg = {
        "username" : username,
        "password" : password
    }
    return cfg

def wrap_data(cfg, data:Optional[Dict]) -> Dict[str,str]:
    today = datetime.datetime.now(tz=time_zone).strftime('%Y/%m/%d')
    if data is None:
        dic = {
            'Username': cfg["username"],
            'Password': cfg["password"],
            'url' : f'https://timetables.liverpool.ac.uk/services/get-events?start={today}&end={today}'
            }
    else:
        dic = {
            'Username': cfg['username'],
            'Password': cfg['password'],
            'attCode': data['code'],
            'attCodeInput': data['code'],
            'uniqueId': data['uniqueid'],
            'actId': data['activityid'],
            'attStart': data['registerstartdatetime'],
            'attEnd': data['registerenddatetime'],
            'location': '',
            'url' : 'https://timetables.liverpool.ac.uk/services/register-attendance-student'
            }
    return dic

# Unused in this program
def get_attendance_code(html) -> List[str]:
    html_json_load = (json.loads(html))
    result = []
    for one_class in html_json_load:
        result.append(f"{one_class['activitydesc'][0:7]}: {one_class['attendancecode']}, {one_class['registerstartdatetime'][11:13]} to {one_class['registerenddatetime'][11:-3]}")
    return result

def get_attendance_info(html) -> Dict[str,Any]:
    html_json_load = (json.loads(html))
    result = []
    for item in html_json_load:
        dic = {
            'activitydesc': item['activitydesc'][0:7],
            'code' : item['attendancecode'],
            'registerstartdatetime' : item['registerstartdatetime'],
            'registerenddatetime' : item['registerenddatetime'],
            'uniqueid' : item['uniqueid'],
            'activityid' : item['activityid']
        }
        result.append(dic)
    return result

def request_timetable(cfg, data:Optional[Dict]):
    data_dic = wrap_data(cfg,data)
    url = data_dic.pop('url')

    login_url = 'https://timetables.liverpool.ac.uk/account?returnUrl=%2F'
    headers = {
        'User-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}
    post_data = urllib.parse.urlencode(data_dic).encode('utf-8')
    req = urllib.request.Request(login_url, headers=headers, data=post_data)

    cookie = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie))

    try:
        resp = opener.open(req)
    except Exception:
        print('There might be some problem with your network.')
        print('Check you network setting and rerun the program.')
        quit()

    req = urllib.request.Request(url, headers=headers, data=post_data)
    resp = opener.open(req)

    result = resp.read().decode('utf-8')
    if 'Username:' in result:
        result = 'password error'

    return result

def main():
    cfg = get_cfg()
    record_time=-1
    
    print('Auto attend start.')
    while True:
        html_file = request_timetable(cfg,data=None)
        data = get_attendance_info(html_file)
        hour = datetime.datetime.now(tz=time_zone).strftime('%H')
        for d in data:
            if hour==d['registerstartdatetime'][11:13] and int(hour)>=record_time and d['code']!='':
                r = request_timetable(cfg,d)
                record_time=int(d['registerenddatetime'][11:13])
                print(f"attend registered: {d['activitydesc']}")
        print(hour)
        time.sleep(1200)
    
if __name__ == '__main__':
    main()
