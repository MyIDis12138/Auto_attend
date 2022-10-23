import datetime
today = datetime.date.today()

import urllib
import http.cookiejar
import json
from typing import Dict, Any

# fill your username and password here
def get_cfg()->Dict[str,Any]:
    cfg = {
        "username" : '',
        "password" : '',
        "year" : today.year,
        "month" : today.month,
        "day" : today.day
    }
    return cfg

def simulate_login(cfg):
    year_str = str(cfg["year"])
    if cfg["month"] < 10:
        month_str = '0' + str(cfg["month"])
    else:
        month_str = str(cfg["month"])
    if cfg["day"] < 10:
        day_str = '0' + str(cfg["day"])
    else:
        day_str = str(cfg["day"])

    url = 'https://timetables.liverpool.ac.uk/services/get-events?start=' + year_str + '-' + month_str + '-' + day_str + '&end=' + year_str + '-' + month_str + '-' + day_str

    data = {'Username': cfg["username"],
            'Password': cfg["password"]}
    post_data = urllib.parse.urlencode(data).encode('utf-8')

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

    req = urllib.request.Request(url, headers=headers)

    resp = opener.open(req)

    result = resp.read().decode('utf-8')
    if 'Username:' in result:
        result = 'password error'

    return result

def get_attendance_code(html):
    html_json_load = (json.loads(html))
    result = []
    for one_class in html_json_load:
        result.append(f"{one_class['activitydesc']}: \n {one_class['attendancecode']}")
    return result

def main():
    cfg = get_cfg()
    html = simulate_login(cfg)
    attendance_code = get_attendance_code(html)
    for i in attendance_code:
        print(i)

if __name__ == '__main__':
    main()