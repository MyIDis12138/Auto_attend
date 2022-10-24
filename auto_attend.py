import datetime
import time
import urllib
import http.cookiejar
import json
from typing import Dict, List, Any, Optional

def get_cfg()->Dict[str,Any]:
    cfg = {
        "username" : 'sgygu14',
        "password" : 'BUAjEUk8'
    }
    return cfg

def wrap_data(cfg, data:Optional[Dict]) -> Dict[str,str]:
    today = datetime.date.today().isoformat()
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

    post_data = urllib.parse.urlencode(data_dic).encode('utf-8')

    headers = {
        'User-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}

    login_url = 'https://timetables.liverpool.ac.uk/account?returnUrl=%2F'

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
    html_file = request_timetable(cfg,data=None)
    
    while True:
        data = get_attendance_info(html_file)
        hour = str(datetime.datetime.now())[11:13]
        for d in data:
            if hour==d['registerstartdatetime'][11:13]:
                r = request_timetable(cfg,d)
                print(f"attend registered: {d['activitydesc']}")
        #print(hour)
        time.sleep(1200)
    
if __name__ == '__main__':
    main()
