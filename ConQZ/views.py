import ast
import datetime
import json
from django.contrib.sites import requests
from django.core import serializers
from django.http import HttpResponse
import requests as requests
from ConQZ.models import User,Share,LikesInfo

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
        "code": 4000,
        "message": "Invalid Login"
    }
    error = json.dumps(error)
    global HEADERS, url
    session = requests.Session()
    req = session.get(url, params=params, timeout=5, headers=HEADERS)
    s = json.loads(req.text)
    print(s["flag"])
    if s["flag"] != "1":
        return HttpResponse(content=error,content_type='application/json')
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
    print(postbody)
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
    try:
        req = session.get(url, params=params, timeout=5, headers=HEADERS)
    except:
        print(req.text)
        print("session对话错误")
        error = {
            "code": 4001,
            "message": "Session Error"
        }
        error = json.dumps(error)
        return HttpResponse(content=error, content_type='application/json')
    s = json.loads(req.text)
    print(User.objects.filter(Snumber=_account))
    Userresult=User.objects.filter(Snumber=_account)
    print("Userresult.exists()=",Userresult.exists())
    #做一个密码匹配
    if Userresult.exists():
        password = User.objects.filter(Snumber=_account).values('PasswordQZ')
        password = password[0]['PasswordQZ']
        if password != _password:
            user_obj = User.objects.get(Snumber=_account)
            user_obj.PasswordQZ = _password
            user_obj.save()
            print("对新用户进行了更新密码的操作")
    if not Userresult.exists():
        user_obj =User.objects.create(Snumber=int(s['xh']),Name=s['xm'],PasswordQZ=_password,
                             Classname=s['bj'],Majorname=s['zymc'],Collegename=s['yxmc'],Enteryear=int(s['rxnf']),Gradenumber=int(s['usertype']))
        user_obj.save()
        print("对新用户进行了创建用户表操作")
    Shareresult = Share.objects.filter(Usernumber_id=_account)
    print("Shareresult.exists()=",Shareresult.exists())
    if not Shareresult.exists():
        share_obj = Share.objects.create(Usernumber_id=_account)
        share_obj.save()
        print("对新用户进行了创建共享表操作")
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
    zc = json_param.get("cont",-1)

    cookies = requests.utils.cookiejar_from_dict(cookiesstr)
    session = requests.Session()
    session.cookies = cookies


    params = {
        "method": "getCurrentTime",
        "currDate": datetime.datetime.now().strftime("%Y-%m-%d")
    }
    req = session.get(url, params=params, timeout=5, headers=HEADERS)
    s = json.loads(req.text)
    if s["zc"]==None:
        s["zc"]=1
    params = {
        "method": "getKbcxAzc",
        "xnxqid": s["xnxqh"],
        "zc": s["zc"] if zc == -1 else zc,
        "xh": _account
    }
    req = session.get(url, params=params, timeout=5, headers=HEADERS)
    table_ord = json.loads(req.text)
    if table_ord[0]==None:

        return HttpResponse(content="[]", content_type='application/json')

    # 将爬取到的数据转成前端需要的数据，格式转换
    # color随机选择颜色
    tablecolor = ["#ebb5cc", "#b2c196", "#edd492", "#fee5a3"
        , "#e9daa3", "#ea7375", "#a286ea", "#776fdf", "#7bc6e6"
        , "#efb293"]
    # # color随机选择莫兰迪色
    # tablecolor = ["#849B91", "#B4746B", "#99857E", "#91A0A5"
    #     , "#A79A89", "#8A95A9", "#9AA690", "#B4746B", "#AB545A"
    #     , "#B77F70", "#9FABB9", "#B57C82", "#686789"]
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
#共享课表/成绩路由
def reply_share_info(request):
    postbody=request.body
    print(postbody)
    json_param = json.loads(postbody.decode())
    _account = json_param.get('account')
    _password = json_param.get('password')
    _reply = json_param.get('reply')
    _postnum = json_param.get('postnum')
    _cont = json_param.get("cont")
    Userresult = User.objects.filter(Snumber=_account)
    Shareresult = Share.objects.filter(Usernumber_id=_account)

    #查找登录用户是否注册
    if not Userresult.exists():
        error = {
            "code": 4001,
            "message": "Not User"
        }
        error = json.dumps(error)
        print(error)
        return HttpResponse(content=error, content_type='application/json')
    #查找登录用户共享表是否注册
    if not Shareresult.exists():
        share_obj = Share.objects.create(Usernumber_id=_account)
        share_obj.save()
        print("对新用户进行了创建共享表操作")
    password=User.objects.filter(Snumber=_account).values('PasswordQZ')
    password=password[0]['PasswordQZ']
    # 查找登录用户共享表是否注册
    if password==_password:
        if _cont==0:
            sharebind = Share.objects.filter(Usernumber_id=_account).values('CBindState')
            sharebind = sharebind[0]['CBindState']
            if sharebind!=2:
                error = {
                    "code": 4005,
                    "message": "Not Bind"
                }
                error = json.dumps(error)
                print(error)
                return HttpResponse(content=error, content_type='application/json')
            # 我同意别人请求
            if _reply==True:
                try:
                    #同意的代码还没写
                    user_obj = Share.objects.get(Usernumber_id=_account)
                    user_obj.CBindState = 3
                    user_obj.CBindNumber=_postnum
                    user_obj.save()
                    user_obj = Share.objects.get(Usernumber_id=_postnum)
                    user_obj.CBindState = 3
                    user_obj.CBindNumber=_account
                    user_obj.save()
                except:
                    error = {
                        "code": 4004,
                        "message": "DB Error"
                    }
                    error = json.dumps(error)
                    return HttpResponse(content=error, content_type='application/json')
                info = {
                    "code": 2000,
                    "message": "Prefect"
                }
                info = json.dumps(info)
                return HttpResponse(content=info, content_type='application/json')
            # 我拒绝别人请求
            elif _reply == False:
                try:
                    #同意的代码还没写
                    user_obj = Share.objects.get(Usernumber_id=_account)
                    user_obj.CBindState = 0
                    user_obj.CBindNumber=-1
                    user_obj.save()
                    user_obj = Share.objects.get(Usernumber_id=_postnum)
                    user_obj.CBindState = 0
                    user_obj.CBindNumber=-1
                    user_obj.save()

                except:
                    error = {
                        "code": 4004,
                        "message": "DB Error"
                    }
                    error = json.dumps(error)
                    return HttpResponse(content=error, content_type='application/json')
                info = {
                    "code": 2000,
                    "message": "Prefect"
                }
                info = json.dumps(info)
                return HttpResponse(content=info, content_type='application/json')

        elif _cont==1:
            sharebind = Share.objects.filter(Usernumber_id=_account).values('GBindState')
            sharebind = sharebind[0]['GBindState']
            if sharebind!=2:
                error = {
                    "code": 4005,
                    "message": "Not Bind"
                }
                error = json.dumps(error)
                print(error)
                return HttpResponse(content=error, content_type='application/json')
            # 我同意别人请求
            if _reply == True:
                try:
                    # 同意的代码还没写
                    user_obj = Share.objects.get(Usernumber_id=_account)
                    user_obj.GBindState = 3
                    user_obj.GBindNumber = _postnum
                    user_obj.save()
                    user_obj = Share.objects.get(Usernumber_id=_postnum)
                    user_obj.GBindState = 3
                    user_obj.GBindNumber = _account
                    user_obj.save()
                except:
                    error = {
                        "code": 4004,
                        "message": "DB Error"
                    }
                    error = json.dumps(error)
                    return HttpResponse(content=error, content_type='application/json')
                info = {
                    "code": 2000,
                    "message": "Prefect"
                }
                info = json.dumps(info)
                return HttpResponse(content=info, content_type='application/json')
            # 我拒绝别人请求
            elif _reply == False:
                try:
                    # 同意的代码还没写
                    user_obj = Share.objects.get(Usernumber_id=_account)
                    user_obj.GBindState = 0
                    user_obj.GBindNumber = -1
                    user_obj.save()
                    user_obj = Share.objects.get(Usernumber_id=_postnum)
                    user_obj.GBindState = 0
                    user_obj.GBindNumber = -1
                    user_obj.save()
                except:
                    error = {
                        "code": 4004,
                        "message": "DB Error"
                    }
                    error = json.dumps(error)
                    return HttpResponse(content=error, content_type='application/json')
                info = {
                    "code": 2000,
                    "message": "Prefect"
                }
                info = json.dumps(info)
                return HttpResponse(content=info, content_type='application/json')

    else:
        error = {
            "code": 4000,
            "message": "Invalid Login"
        }
        error = json.dumps(error)
        print(error)
        return HttpResponse(content=error, content_type='application/json')
def post_share_info(request):
    postbody=request.body
    print(postbody)
    json_param = json.loads(postbody.decode())
    _cancel = json_param.get("cancel")
    _account = json_param.get('account')
    _password = json_param.get('password')
    _postnum = json_param.get('postnum')
    _cont = json_param.get("cont")
    Userresult = User.objects.filter(Snumber=_account)
    Shareresult = Share.objects.filter(Usernumber_id=_account)
    if not Userresult.exists():
        error = {
            "code": 4001,
            "message": "Not User"
        }
        error = json.dumps(error)
        print(error)
        return HttpResponse(content=error, content_type='application/json')
    if not Shareresult.exists():
        share_obj = Share.objects.create(Usernumber_id=_account)
        share_obj.save()
        print("对新用户进行了创建共享表操作")
    password=User.objects.filter(Snumber=_account).values('PasswordQZ')
    password=password[0]['PasswordQZ']
    if password==_password:
        # 看对方有没有注册,鉴权
        # 加上了取消关键词，看这个post是取消还是不取消
        if not _cancel:
            Userresult = User.objects.filter(Snumber=_postnum)
            if not Userresult.exists():
                error = {
                    "code": 4002,
                    "message": "Not User Other"
                }
                error = json.dumps(error)
                print(error)
                return HttpResponse(content=error, content_type='application/json')
            if _cont==0:
                # 我向别人发送请求，此时我的绑定状态为1，学号变成具体值
                user_obj = Share.objects.get(Usernumber_id=_account)
                user_obj.CBindState = 1
                user_obj.CBindNumber=_postnum
                user_obj.save()
                # 我向别人发送请求，此时别人的绑定状态为2，学号变成具体值
                user_obj = Share.objects.get(Usernumber_id=_postnum)
                user_obj.CBindState = 2
                user_obj.CBindNumber=_account
                user_obj.save()
                info = {
                    "code": 2000,
                    "message": "Prefect"
                }
                info = json.dumps(info)
                return HttpResponse(content=info, content_type='application/json')
            elif _cont==1:
                # 我向别人发送请求，此时我的绑定状态为1，学号变成具体值
                user_obj = Share.objects.get(Usernumber_id=_account)
                user_obj.GBindState = 1
                user_obj.GBindNumber = _postnum
                user_obj.save()
                info = {
                    "code": 2000,
                    "message": "Prefect"
                }
                info = json.dumps(info)
                # 我向别人发送请求，此时别人的绑定状态为2，学号变成具体值
                user_obj = Share.objects.get(Usernumber_id=_postnum)
                user_obj.GBindState = 2
                user_obj.GBindNumber = _account
                user_obj.save()
                info = {
                    "code": 2000,
                    "message": "Prefect"
                }
                info = json.dumps(info)
                return HttpResponse(content=info, content_type='application/json')
        else:
            Userresult = User.objects.filter(Snumber=_postnum)
            if not Userresult.exists():
                error = {
                    "code": 4002,
                    "message": "Not User Other"
                }
                error = json.dumps(error)
                print(error)
                return HttpResponse(content=error, content_type='application/json')
            if _cont == 0:
                # 我向别人发送请求，此时我的绑定状态为1，学号变成具体值
                user_obj = Share.objects.get(Usernumber_id=_account)
                user_obj.CBindState = 0
                user_obj.CBindNumber = -1
                user_obj.save()
                # 我向别人发送请求，此时别人的绑定状态为2，学号变成具体值
                user_obj = Share.objects.get(Usernumber_id=_postnum)
                user_obj.CBindState = 0
                user_obj.CBindNumber = -1
                user_obj.save()
                info = {
                    "code": 2000,
                    "message": "Prefect"
                }
                info = json.dumps(info)
                return HttpResponse(content=info, content_type='application/json')
            elif _cont == 1:
                # 我向别人发送请求，此时我的绑定状态为1，学号变成具体值
                user_obj = Share.objects.get(Usernumber_id=_account)
                user_obj.GBindState = 0
                user_obj.GBindNumber = -1
                user_obj.save()
                info = {
                    "code": 2000,
                    "message": "Prefect"
                }
                info = json.dumps(info)
                return HttpResponse(content=info, content_type='application/json')
                # 我向别人发送请求，此时别人的绑定状态为2，学号变成具体值
                user_obj = Share.objects.get(Usernumber_id=_postnum)
                user_obj.GBindState = 0
                user_obj.GBindNumber = -1
                user_obj.save()
                info = {
                    "code": 2000,
                    "message": "Prefect"
                }
                info = json.dumps(info)
                return HttpResponse(content=info, content_type='application/json')

    else:
        error = {
            "code": 4000,
            "message": "Invalid Login"
        }
        error = json.dumps(error)
        print(error)
        return HttpResponse(content=error, content_type='application/json')
def get_share_state(request):
    postbody=request.body
    print(postbody)
    json_param = json.loads(postbody.decode())
    _account = json_param.get('account')
    _password = json_param.get('password')
    Userresult = User.objects.filter(Snumber=_account)
    Shareresult = Share.objects.filter(Usernumber_id=_account)
    if not Userresult.exists():
        error = {
            "code": 4001,
            "message": "Not User"
        }
        return HttpResponse(content=error, content_type='application/json')
    if not Shareresult.exists():
        share_obj = Share.objects.create(Usernumber_id=_account)
        share_obj.save()
        print("对新用户进行了创建共享表操作")
    password=User.objects.filter(Snumber=_account).values('PasswordQZ')
    password=password[0]['PasswordQZ']
    if password==_password:
        data = serializers.serialize("json", Share.objects.filter(Usernumber_id=_account))
        print(data)
        print(type(data))
        data_json= json.loads(data)
        data_json=json.dumps(data_json[0]['fields'])
        print(data_json)
        print(type(data_json))
        return HttpResponse(content=data_json, content_type='application/json')
    else:
        error = {
            "code": 4000,
            "message": "Invalid Login"
        }
        return HttpResponse(content=error, content_type='application/json')
def get_share_info(request):

    global url,HEADERS
    postbody = request.body
    print(postbody)
    json_param = json.loads(postbody.decode())
    _account = json_param.get('account')
    _password = json_param.get('password')
    get_cont = json_param.get("content")
    _cont = json_param.get("cont")

    Shareresult = Share.objects.filter(Usernumber_id=_account)
    if not Shareresult.exists():
        error = {
            "code": 4001,
            "message": "Not User"
        }
        error = json.dumps(error)
        print(error)
        return HttpResponse(content=error, content_type='application/json')


    if _cont==0:
        sharestate = Share.objects.filter(Usernumber_id=_account).values('CBindState')
        sharestate = sharestate[0]['CBindState']
        if sharestate!=3:
            error = {
                "code": 4005,
                "message": "Not Bind"
            }
            error = json.dumps(error)
            print(error)
            return HttpResponse(content=error, content_type='application/json')

        shareaccount = Share.objects.filter(Usernumber_id=_account).values('CBindNumber')
        shareaccount=shareaccount[0]['CBindNumber']
        if shareaccount==-1:
            error = {
                "code": 4005,
                "message": "Not Bind"
            }
            error = json.dumps(error)
            print(error)
            return HttpResponse(content=error, content_type='application/json')
        else:
            sharepassword = User.objects.filter(Snumber=shareaccount).values('PasswordQZ')
            sharepassword = sharepassword[0]['PasswordQZ']

        params = {
            "method": "authUser",
            "xh": shareaccount,
            "pwd": sharepassword
        }
        session = requests.Session()
        req = session.get(url, params=params, timeout=5, headers=HEADERS)
        s = json.loads(req.text)
        if s["flag"] != "1":
            error = {
                "code": 4000,
                "message": "Invalid Login"
            }
            error = json.dumps(error)
            return HttpResponse(content=error, content_type='application/json')
        HEADERS["token"] = s["token"]
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
            "xh": shareaccount
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
    elif _cont == 1:
        sharestate = Share.objects.filter(Usernumber_id=_account).values('GBindState')
        sharestate = sharestate[0]['GBindState']
        if sharestate!=3:
            error = {
                "code": 4005,
                "message": "Not Bind"
            }
            error = json.dumps(error)
            print(error)
            return HttpResponse(content=error, content_type='application/json')

        shareaccount = Share.objects.filter(Usernumber_id=_account).values('GBindNumber')
        shareaccount=shareaccount[0]['GBindNumber']

        if shareaccount==-1:
            error = {
                "code": 4005,
                "message": "Not Bind"
            }
            error = json.dumps(error)
            print(error)
            return HttpResponse(content=error, content_type='application/json')
        else:
            sharepassword = User.objects.filter(Snumber=shareaccount).values('PasswordQZ')
            sharepassword = sharepassword[0]['PasswordQZ']
        params = {
            "method": "authUser",
            "xh": shareaccount,
            "pwd": sharepassword
        }
        session = requests.Session()
        req = session.get(url, params=params, timeout=5, headers=HEADERS)
        s = json.loads(req.text)
        if s["flag"] != "1":
            error = {
                "code": 4000,
                "message": "Invalid Login"
            }
            error = json.dumps(error)
            return HttpResponse(content=error, content_type='application/json')
        HEADERS["token"] = s["token"]
        sy = ""
        if (get_cont != None):
            sy = get_cont
        params = {
            "method": "getCjcx",
            "xh": shareaccount,
            "xnxqid": sy
        }
        req = session.get(url, params=params, timeout=5, headers=HEADERS)
        return HttpResponse(content=req, content_type='application/json')
#小科通讯录
def get_phonebook_info(request):
    content = serializers.serialize("json", LikesInfo.objects.all())
    print(content)
    print(type(content))

    return HttpResponse(content=content, content_type='application/json')
#小科食物库
#小科备忘录
#小科经验包
#教室课表
