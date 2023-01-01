import ast
import datetime
import json
from django.contrib.sites import requests
from django.http import HttpResponse
import requests as requests
from django.shortcuts import render

# Create your views here.
HEADERS = {
   "User-Agent": "Mozilla/5.0 (Linux; U; Mobile; Android 6.0.1;C107-9 Build/FRF91 )",
   "Referer": "http://www.baidu.com",
   "Accept-encoding": "gzip, deflate, br",
   "Accept-language": "zh-CN,zh-TW;q=0.8,zh;q=0.6,en;q=0.4,ja;q=0.2",
   "Cache-control": "max-age=0"
}
url = "http://jwgl.sdust.edu.cn/app.do"
def get_login_info(request):
    # 读取数据
    postbody=request.body
    json_param = json.loads(postbody.decode())
    _account = json_param.get('account')
    _password = json_param.get('password')

    params = {
        "method": "authUser",
        "xh": _account,
        "pwd": _password
    }
    error = {
        "code": 2002,
        "message": "Invalid Login"
    }
    global HEADERS, url
    session = requests.Session()
    req = session.get(url, params=params, timeout=5, headers=HEADERS)
    s = json.loads(req.text)
    if s["flag"] != "1":
        return error
    HEADERS["token"] = s["token"]
    global cookies
    cookies = session.cookies
    print(session.cookies)
    cookies_dict = requests.utils.dict_from_cookiejar(cookies)
    cookies_str = json.dumps(cookies_dict)

    # '{"JSESSIONID": "3474AAED60477A63776B77CC2B82E5FB"}'
    return  HttpResponse(content=cookies_str,content_type='application/json')


def get_student_info(request):
    postbody=request.body
    json_param = json.loads(postbody.decode())
    _account = json_param.get('account')
    _password = json_param.get('password')
    cookiesstr = json_param.get("cookiesstr")
    print(cookiesstr)
    cookies = requests.utils.cookiejar_from_dict(cookiesstr)
    session = requests.Session()
    session.cookies = cookies
    global HEADERS,url
    params = {
            "method": "getUserInfo",
            "xh": _account
        }
    req = session.get(url, params=params, timeout=5, headers=HEADERS)

    return HttpResponse(content=req,content_type='application/json')

def get_current_time(request):
    postbody=request.body
    json_param = json.loads(postbody.decode())
    _account = json_param.get('account')
    _password = json_param.get('password')
    cookiesstr = json_param.get("cookiesstr")

    cookies = requests.utils.cookiejar_from_dict(cookiesstr)
    session = requests.Session()
    session.cookies = cookies
    global HEADERS,url
    params = {
        "method": "getCurrentTime",
        "currDate": datetime.datetime.now().strftime("%Y-%m-%d")
    }
    req = session.get(url, params=params, timeout=5, headers=HEADERS)
    return HttpResponse(content=req,content_type='application/json')

def get_class_info(request):
    global url,HEADERS
    postbody = request.body
    json_param = json.loads(postbody.decode())
    _account = json_param.get('account')
    _password = json_param.get('password')
    cookiesstr = json_param.get("cookiesstr")
    get_cont = json_param.get("cont")

    cookies = requests.utils.cookiejar_from_dict(cookiesstr)
    session = requests.Session()
    session.cookies = cookies
    zc = -1
    if (get_cont != None):
        zc = get_cont

    params = {
        "method": "getCurrentTime",
        "currDate": datetime.datetime.now().strftime("%Y-%m-%d")
    }
    req = session.get(url, params=params, timeout=5, headers=HEADERS)
    s = json.loads(req.text)
    params = {
        "method": "getKbcxAzc",
        "xnxqid": s["xnxqh"],
        "zc": s["zc"] if zc == -1 else zc,
        "xh": _account
    }
    req = session.get(url, params=params, timeout=5, headers=HEADERS)
    print(req)
    # 将爬取到的数据转成前端需要的数据，格式转换
    table_ord = ast.literal_eval(req.text)
    print(table_ord)
    # color随机选择莫兰迪色
    tablecolor = ["#849B91", "#B4746B", "#99857E", "#91A0A5"
        , "#A79A89", "#8A95A9", "#9AA690", "#B4746B", "#AB545A"
        , "#B77F70", "#9FABB9", "#B57C82", "#686789"]
    # color随机选择apple超级亮色
    # tablecolor = ["#FF6961", "#FFB340", "#FFD426", "#30DB5B", "#70D7FF"
    #     , "#409CFF", "#707AFF", "#DA8FFF", "#FF6482"]
    # tablecolor = ["#D70015", "#C93400", "#B25000", "#248A3D", "#0071A4"
    #     , "#0040DD", "#3634A3", "#8944AB", "#D30F45"]
    # 分割将class转换成数组返回
    table = [[[[] for j in range(5)] for i in range(5)] for k in range(7)]
    tablesame = [[-1 for j in range(2)] for k in range(35)]
    flag_i_color = 0  # 进行表的比对，如果same表存在就直接用颜色，不存在就给个新颜色，新颜色用到的
    for newtable in table_ord:
        get_kcsj = newtable.get("kcsj")
        cout = int(get_kcsj[3] + get_kcsj[4])
        cout = int(cout / 2) - 1
        get_kcmc = newtable.get("kcmc")
        get_jsmc = newtable.get("jsmc")
        get_jsxm = newtable.get("jsxm")
        # random.randrange(0,12,1)
        kcsj_day = int(get_kcsj[0]) - 1
        table[kcsj_day][cout][0] = get_kcmc
        table[kcsj_day][cout][1] = get_jsmc
        table[kcsj_day][cout][2] = get_jsxm

        for tablesame_i in tablesame:
            # 进行表的比对，如果same表存在就直接用颜色，不存在就给个新颜色
            if (tablesame_i[0] == get_kcmc):
                table[kcsj_day][cout][3] = tablesame_i[1]
                break
            if (tablesame_i[0] == -1):
                tablesame_i[0] = get_kcmc
                tablesame_i[1] = tablecolor[flag_i_color]
                flag_i_color += 1
                table[kcsj_day][cout][3] = tablesame_i[1]
                break
    # print(table)
    str_json = json.dumps(table, ensure_ascii=False, indent=2)
    # print(str_json)
    return HttpResponse(content=str_json,content_type='application/json')

def get_classroom_info(request):
    postbody = request.body
    json_param = json.loads(postbody.decode())
    _account = json_param.get('account')
    _password = json_param.get('password')
    cookiesstr = json_param.get("cookiesstr")
    get_cont = json_param.get("cont")

    idleTime = "allday"

    if (get_cont != None):
        idleTime=get_cont
    cookies = requests.utils.cookiejar_from_dict(cookiesstr)
    session = requests.Session()
    session.cookies = cookies
    global HEADERS,url
    params = {
        "method": "getKxJscx",
        "time": datetime.datetime.now().strftime("%Y-%m-%d"),
        "idleTime": idleTime
    }
    req = session.get(url, params=params, timeout=5, headers=HEADERS)
    return HttpResponse(content=req,content_type='application/json')

def get_grade_info(request):  # put application's code here

    global HEADERS,url
    postbody = request.body
    json_param = json.loads(postbody.decode())
    _account = json_param.get('account')
    _password = json_param.get('password')
    cookiesstr = json_param.get("cookiesstr")
    get_cont = json_param.get("cont")
    sy = ""

    if (get_cont != None):
        sy=get_cont
    cookies = requests.utils.cookiejar_from_dict(cookiesstr)
    session = requests.Session()
    session.cookies = cookies
    params = {
        "method": "getCjcx",
        "xh": _account,
        "xnxqid": sy
    }
    req = session.get(url, params=params, timeout=5, headers=HEADERS)
    return HttpResponse(content=req, content_type='application/json')

def get_exam_info(request):  # put application's code here
    postbody = request.body
    json_param = json.loads(postbody.decode())
    _account = json_param.get('account')
    _password = json_param.get('password')
    cookiesstr = json_param.get("cookiesstr")
    global HEADERS,url

    cookies = requests.utils.cookiejar_from_dict(cookiesstr)
    session = requests.Session()
    session.cookies = cookies
    params = {
        "method": "getKscx",
        "xh": _account,
    }
    req = session.get(url, params=params, timeout=5, headers=HEADERS)
    return HttpResponse(content=req, content_type='application/json')