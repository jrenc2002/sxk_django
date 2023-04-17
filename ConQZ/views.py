import datetime
import json
from django.contrib.sites import requests
from django.core import serializers
from django.http import HttpResponse, JsonResponse
import requests as requests

from django.conf import settings
from django.contrib.auth import authenticate
from django.core.cache import cache
import jwt

from ConQZ.models import User,Share,LikesInfo,Course,CourseTime
from requests import RequestException

global HEADERS,url

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


def auth_by_snumber(snumber,token):
    """根据学号和openid鉴权"""
    if not snumber or not token:
        return None

    # 解析token获取openid
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        openid = payload['openid']
    except jwt.exceptions.ExpiredSignatureError:
        return None
    except jwt.exceptions.InvalidTokenError:
        return None

    # 根据snumber和openid查询用户
    try:
        user = User.objects.get(snumber=snumber, openid=openid)
    except User.DoesNotExist:
        return None

    return user

def Logininfo(request):
    """
    鉴权登录并创建用户表，返回用户对话token
    :return: 用户对话token
    """
    if request.method == 'POST':
        json_param = json.loads(request.body.decode())
        account = int(json_param.get('snumber'))
        name = json_param.get('name')
        classname = json_param.get('classname')
        majorname = json_param.get('majorname')
        collegename = json_param.get('collegename')
        enteryear = int(json_param.get('enteryear'))
        gradenumber = int(json_param.get('gradenumber'))
        code = json_param.get('code')

        if code:
            # 发起网络请求，获取用户的 openid 和 session_key
            response = requests.get(
                f'https://api.weixin.qq.com/sns/jscode2session?appid=wx09eeff6c032da35a&secret=cbabace88e0f70970a07eb468d6db23d&js_code={code}&grant_type=authorization_code')

            if response.status_code != 200:
                return JsonResponse({'error': '登录失败'})
            # 解析微信服务器的返回结果
            data = response.json()
            openid = data.get('openid')
            # session_key = data.get('session_key')

            # 如果 openid 返回成功，读入输入的数据存入数据库，如果有这个用户只更新 Openid，没有这个用户新建表
            try:
                user_obj = User.objects.get(Snumber=account)
                user_obj.Openid = openid
                user_obj.save()
                print("更新了用户表的 Openid")
            except User.DoesNotExist:
                user_obj = User.objects.create(Snumber=account, Name=name,
                                               Classname=classname, Majorname=majorname,
                                               Collegename=collegename,
                                               Enteryear=enteryear,
                                               Gradenumber=gradenumber,Openid=openid)
                user_obj.save()
                print("创建了新用户表")

            share_obj, created = Share.objects.get_or_create(Usernumber_id=account)
            # 创建共享表
            if created:
                print("创建了共享表")
            else:
                print("共享表已存在")

            # 根据 openid 和 session_key 进行登录验证，并返回响应数据
            # 绑定 openid 到 token
            payload = {'openid': openid}
            token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
            return JsonResponse({'status': 'success', 'token': token})

        else:
            return JsonResponse({'status': 'error', 'message': '缺少 code 参数'})
    else:
        return JsonResponse({'status': 'error', 'message': '仅支持 POST 请求'})



def ClassInfo(request):
    global url,HEADERS
    # 获取请求体中的参数
    try:
        postbody = request.body
        json_param = json.loads(postbody.decode())
        table_ord = json_param.get('table_ord')
        token = json_param.get("token")
    except Exception as e:
        # 处理请求体中参数解析错误的情况
        error = {"code": 4000, "message": "Invalid Parameters"}
        return JsonResponse(error)


    table_ord = json.loads(table_ord)


    # 将爬取到的数据转成前端需要的数据，格式转换
    tablesame = [[-1 for j in range(2)] for k in range(35)]
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
    table = [[[[] for j in range(5)] for i in range(5)] for k in range(7)]#课程
    flag_i_color = 0  # 进行表的比对，如果same表存在就直接用颜色，不存在就给个新颜色，新颜色用到的
    for newtable in table_ord:
        try:
            # 解析课程信息
            get_kcmc = newtable.get("kcmc")  # 课程名称
            get_jsmc = newtable.get("jsmc")  # 上课教室
            get_jsxm = newtable.get("jsxm")  # 老师名称
            get_kkzc = newtable.get("kkzc")  # 上课星期
            get_kcsj = newtable.get("kcsj")  # 上课时间
            # 将课程信息存入表格
            kcsj_day = int(get_kcsj[0]) - 1
            cout = int(get_kcsj[3] + get_kcsj[4])
            cout = int(cout / 2) - 1
            # 课程名称
            table[kcsj_day][cout][0] = get_kcmc
            # 上课地址
            table[kcsj_day][cout][1] = get_jsmc
            # 老师名称
            table[kcsj_day][cout][2] = get_jsxm

            Courseresult = Course.objects.filter(CourseName=get_kcmc, CourseTeacher=get_jsxm)
            # 所有东西都存储说明我存储了课，这样不会有重复的课
            # 我没有存储这个课
            if not Courseresult.exists():
                NewCourse = Course.objects.create(CourseName=get_kcmc, CourseTeacher=get_jsxm)
                NewCourse.save()
                NewCourseTime = CourseTime.objects.create(CourseTime=get_kcsj, CourseWeek=get_kkzc, CourseId=NewCourse,
                                                          CoursePlace=get_jsmc)
                NewCourseTime.save()
            # 我已经存储这个课
            else:
                # 现在看看有没有存储这个课的时间
                Course_result = Course.objects.get(CourseName=get_kcmc, CourseTeacher=get_jsxm)
                CourseTimeresult = Course_result.coursetime_set.all().values_list('CourseTime')
                flag_time = True  # 没有相等的
                for time_i in CourseTimeresult:
                    if time_i[0] == get_kcsj:
                        flag_time = False  # 存在相等的
                        break
                # 不存在相等的时间，我要不要记录星期有没有时间相同星期不同？除非后期调课，原来的课调走后面的课然后调到相同时间这时会漏读多读。
                if flag_time == True:
                    NewCourseTime = CourseTime.objects.create(CourseTime=get_kcsj, CourseWeek=get_kkzc,
                                                              CourseId=Course_result,
                                                              CoursePlace=get_jsmc)
                    NewCourseTime.save()

            # 给颜色
            for tablesame_i in tablesame:
                if tablesame_i[0] == get_kcmc:
                    table[kcsj_day][cout][3] = tablesame_i[1]
                    break
                if tablesame_i[0] == -1:
                    tablesame_i[0] = get_kcmc
                    tablesame_i[1] = tablecolor[flag_i_color]
                    flag_i_color += 1
                    if flag_i_color>5:
                        flag_i_color = flag_i_color % 7
                    table[kcsj_day][cout][3] = tablesame_i[1]
                    break
        except Exception as e:
            # 添加异常处理机制
            return HttpResponse(content=f"An error occurred: {e}", status=500)
    # 将表格转换成 JSON 格式并返回
    try:
        str_json = json.dumps(table, ensure_ascii=False, indent=2)
        return HttpResponse(content=str_json, content_type='application/json')
    except Exception as e:
        # 添加异常处理机制
        return HttpResponse(content=f"An error occurred: {e}", status=500)

def EmptyClassroomInfo(request):
    # 获取 POST 请求的参数
    postbody = request.body
    try:
        json_param = json.loads(postbody.decode())
    except json.JSONDecodeError:
        error = {
            "code": 4000,
            "message": "Invalid JSON payload"
        }
        return JsonResponse(error, status=400)

    # 获取参数中的账号、密码、cookie 和 idleTime
    _account = json_param.get('account')
    _password = json_param.get('password')
    get_cont = json_param.get("cont")
    token = json_param.get("token")

    # 设置请求头中的 token
    HEADERS["token"] = token

    # 设置 idleTime 参数
    idleTime = "allday" if get_cont is None else get_cont



    # 构造会话对象
    session = requests.Session()

    # 构造请求参数
    params = {
        "method": "getKxJscx",
        "time": datetime.datetime.now().strftime("%Y-%m-%d"),
        "idleTime": idleTime
    }

    try:
        # 发送 GET 请求
        req = session.get(url, params=params, timeout=5, headers=HEADERS)
        req.raise_for_status()
    except requests.exceptions.RequestException as e:
        error = {
            "code": 4001,
            "message": "Session Error"
        }
        return JsonResponse(error, status=400)
    # 返回 JSON 格式的响应
    result = {"data": req.json()}
    return JsonResponse(result, status=200, safe=False)

def GradeInfo(request):
    """
    说明：获取学生成绩信息视图函数

    参数：
    - request: 请求对象

    返回值：
    - HttpResponse对象

    异常：
    - 返回4001错误：Session错误
    - 返回4008错误：登录错误
    """

    # 设置全局变量
    global HEADERS, url

    # 解析POST请求中的JSON参数
    try:
        json_param = json.loads(request.body)
    except json.JSONDecodeError:
        # 返回JSON解码错误
        error = {
            "code": 4000,
            "message": "JSON Decode Error"
        }
        return HttpResponse(content=json.dumps(error), content_type='application/json', status=400)

    # 获取必需的参数
    _account = json_param.get('account')
    _password = json_param.get('password')
    get_cont = json_param.get("cont")
    token = json_param.get("token")

    # 检查必需的参数是否存在
    if not (_account and _password  and token):
        # 返回缺少参数的错误
        error = {
            "code": 4002,
            "message": "Missing Required Parameters"
        }
        return HttpResponse(content=json.dumps(error), content_type='application/json', status=400)

    # 设置请求头部的token字段
    HEADERS["token"] = token

    # 获取sy参数（如果存在）
    sy = "" if get_cont is None else get_cont

    try:
        # 解析cookies字符串，构建会话
        session = requests.Session()

        # 设置请求参数
        params = {
            "method": "getCjcx",
            "xh": _account,
            "xnxqid": sy
        }

        # 发送GET请求
        req = session.get(url, params=params, timeout=5, headers=HEADERS)
        req.raise_for_status()  # 检查HTTP错误状态码

    except (requests.exceptions.RequestException, ValueError):
        # 返回Session错误
        error = {
            "code": 4001,
            "message": "Session Error"
        }
        return HttpResponse(content=json.dumps(error), content_type='application/json', status=400)

    except requests.exceptions.HTTPError as err:
        # 返回HTTP错误
        error = {
            "code": err.response.status_code,
            "message": err.response.reason
        }
        return HttpResponse(content=json.dumps(error), content_type='application/json', status=err.response.status_code)

    # 返回学生成绩信息
    return HttpResponse(content=req, content_type='application/json')

def ExamInfo(request):
    """
    获取考试信息视图函数
    """
    # 获取请求参数
    try:
        postbody = request.body
        json_param = json.loads(postbody.decode())
        _account = json_param.get('account')
        _password = json_param.get('password')
        token = json_param.get("token")
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        error = {
            "code": 4000,
            "message": "Request Parameter Error",
            "details": str(e)
        }
        error = json.dumps(error)
        return HttpResponse(content=error, content_type='application/json', status=400)


    HEADERS["token"] = token



    session = requests.Session()

    # 发送 GET 请求获取考试信息
    params = {
        "method": "getKscx",
        "xh": _account,
    }
    try:
        req = session.get(url, params=params, timeout=5, headers=HEADERS)
        req.raise_for_status()
    except RequestException as e:
        error = {
            "code": 4001,
            "message": "Request Error",
            "details": str(e)
        }
        error = json.dumps(error)
        print(error)
        return HttpResponse(content=error, content_type='application/json', status=400)

    return HttpResponse(content=req.content, content_type='application/json', status=200)

#共享课表/成绩路由
def ReplyShareInfo(request):
    postbody = request.body
    print(postbody)
    json_param = json.loads(postbody.decode())
    _account = json_param.get('account')
    _password = json_param.get('password')
    _reply = json_param.get('reply')
    _postnum = json_param.get('postnum')
    _cont = json_param.get("cont")#0表示课程，1表示成绩


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
def PostShareInfo(request):
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
                try:
                    # 我向别人发送请求，此时我的绑定状态为1，学号变成具体值
                    user_obj = Share.objects.get(Usernumber_id=_account)
                    user_obj.GBindState = 0
                    user_obj.GBindNumber = -1
                    user_obj.save()
                    # 我向别人发送请求，此时别人的绑定状态为2，学号变成具体值
                    user_obj = Share.objects.get(Usernumber_id=_postnum)
                    user_obj.GBindState = 0
                    user_obj.GBindNumber = -1
                    user_obj.save()
                except:
                    error = {
                        "code": 4004,
                        "message": "DB error"
                    }
                    error = json.dumps(error)
                    print(error)
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
def GetShareState(request):
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
def GetShareInfo(request):

    global url,HEADERS
    postbody = request.body
    print(postbody)
    json_param = json.loads(postbody.decode())
    _account = json_param.get('account')
    _password = json_param.get('password')
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
            "account": shareaccount,
            "pwd": sharepassword,
            "code": 200
        }
        info = json.dumps(params)
        return HttpResponse(content=info,content_type='application/json')
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
            "account": shareaccount,
            "pwd": sharepassword,
            "code": 200
        }
        info = json.dumps(params)
        return HttpResponse(content=info, content_type='application/json')
#小科通讯录

def GetPhonebookInfo(request):
    # 获取POST请求的body数据
    post_body = request.body
    print(post_body)

    # 解析JSON参数
    json_param = json.loads(post_body.decode())

    # 序列化数据库中所有的LikesInfo对象，并将结果赋值给content变量
    content = serializers.serialize("json", LikesInfo.objects.all())
    print(content)
    print(type(content))

    # 检查并获取分页参数和like名称参数
    page = json_param.get("page")
    like_name = json_param.get('likename')
    if like_name is None or page is None:
        # 如果缺少参数，则返回错误响应
        error = {
            "code": 4009,
            "message": "Begin Data Error"
        }
        error = json.dumps(error)
        print(error)
        return HttpResponse(content=error, content_type='application/json')

    # 从数据库中获取包含like名称的LikesInfo对象
    course_lib = LikesInfo.objects.filter(Groupname__icontains=like_name)

    # 将course_lib序列化为JSON对象，然后再反序列化为Python对象
    course_lib_json = serializers.serialize('json', course_lib)
    course_lib_list = json.loads(course_lib_json)

    # 创建一个空列表来保存Course_lib_list的前5项
    course_lib_top_5 = []

    # 计算第一个需要返回的项的索引
    start_index = (page - 1) * 5

    # 计算最后一个需要返回的项的索引
    end_index = page * 5

    # 如果end_index超出了Course_lib_list的长度，则将其设置为Course_lib_list的长度
    if end_index > len(course_lib_list):
        end_index = len(course_lib_list)

    # 遍历Course_lib_list中的项，将前5项添加到course_lib_top_5中
    for index in range(start_index, end_index):
        # 将当前项添加到course_lib_top_5中
        current_item = course_lib_list[index]['fields']
        current_item['id'] = course_lib_list[index]['pk']
        course_lib_top_5.append(current_item)

    # 将course_lib_top_5序列化为JSON对象，并将其返回
    course_lib_top_5_json = json.dumps(course_lib_top_5)
    return HttpResponse(content=course_lib_top_5_json, content_type='application/json')
    #  _page = json_param.get("page")
    #     _likename = json_param.get('likename')
    #     if _likename==None or _page==None:
    #         error = {
    #             "code": 4009,
    #             "message": "Begin Data Error"
    #         }
    #         error = json.dumps(error)
    #         print(error)
    #         return HttpResponse(content=error, content_type='application/json')
    #     Course_lib = serializers.serialize("json", LikesInfo.objects.filter(Groupname__icontains=_likename))
    #     print(Course_lib)
    #     print("-----")
    #     Course_lib = json.loads(Course_lib)
    #     Course_lib_list = [[] for k in range(5)]
    #     for index in range((_page - 1) * 5, (_page) * 5):
    #         if len(Course_lib) > index:
    #             print(index)
    #             Course_lib_list[index - (_page - 1) * 5] = Course_lib[index]['fields']
    #             Course_lib_list[index-(_page-1)*5]["id"]=Course_lib[index]['pk']
    #             print(Course_lib_list[index - (_page - 1) * 5])
    #             print("-----------")
    #     Course_lib_json = json.dumps(Course_lib_list)
    #     print(Course_lib_json)
    #     print(type(Course_lib_json))
    #     return HttpResponse(content=Course_lib_json, content_type='application/json')
    #
    #     return HttpResponse(content=content, content_type='application/json'
#小科食物库

#小科备忘录

#小科经验包

#小科课程库
def GetCourselib(request):

    if request.method == 'POST':
        post_body = request.body
        print(post_body)
        try:
            json_param = json.loads(post_body.decode())
        except ValueError:
            error = {
                "code": 4009,
                "message": "Invalid JSON data"
            }
            error = json.dumps(error)
            print(error)
            return HttpResponse(content=error, content_type='application/json')

    # 处理 "cont" 字段
    cont = json_param.get("cont")
    if cont==0:
        # 处理 "page" 和 "coursename"、"teachername" 字段
        page = json_param.get("page")
        coursename = json_param.get('coursename')
        teachername = json_param.get('teachername')
        print(page,coursename,teachername)
        # 分页查询课程表数据
        if not page :
            error = {
                "code": 400,
                "message": "Bad Request: Missing required parameters."
            }
            return JsonResponse(error, status=400)

        courses = Course.objects.filter(CourseName__icontains=coursename, CourseTeacher__icontains=teachername)
        course_list = [[] for k in range(10)]

        for index, course in enumerate(courses[(page - 1) * 10: page * 10], start=(page - 1) * 10):
            course_fields = {
                "id": course.id,
                "CourseName": course.CourseName,
                "CourseTeacher": course.CourseTeacher,
            }
            course_list[index - (page - 1) * 10] = course_fields

        response_data = {
            "code": 200,
            "data": course_list,
        }
        return JsonResponse(response_data, status=200)
    elif cont == 1:
        toweek= json_param.get('toweek')
        course_id = json_param.get("id")
        # 查询指定课程的课程表数据
        if not toweek or not course_id or not isinstance(toweek, int):
            error = {
                "code": 400,
                "message": "Bad Request: Missing required parameters."
            }
            return JsonResponse(error, status=400)
        # 正式请求，请求课程数据，要求给课程ID；然后我给出详细的数据，包括课程名称，教室，老师名字，课程时间；

        try:
            course = Course.objects.get(id=course_id)
            course_detail = course.coursetime_set.all().values_list('CourseWeek', 'CourseTime', 'CoursePlace')
        except Course.DoesNotExist:
            error = {
                "code": 4009,
                "message": "Begin Data Error"
            }
            return HttpResponse(content=json.dumps(error), content_type='application/json')

        timetable = [[[[] for j in range(5)] for i in range(5)] for k in range(7)]  # 课程

        for detail in course_detail:
            week_nums = detail[0].split(',')
            time_range = detail[1]
            place = detail[2]

            time_slot = int(time_range[3] + time_range[4])
            time_slot = int(time_slot / 2) - 1  # 节数

            for week_num in week_nums:
                if '-' in week_num:
                    start_week, end_week = map(int, week_num.split('-'))
                    if start_week <= toweek <= end_week:
                        day = int(time_range[0]) - 1
                        timetable[day][time_slot][0] = course.CourseName
                        timetable[day][time_slot][1] = place
                        timetable[day][time_slot][2] = course.CourseTeacher
                        timetable[day][time_slot][3] = detail[0]
                else:
                    if int(week_num) == toweek:
                        day = int(time_range[0]) - 1
                        timetable[day][time_slot][0] = course.CourseName
                        timetable[day][time_slot][1] = place
                        timetable[day][time_slot][2] = course.CourseTeacher
                        timetable[day][time_slot][3] = detail[0]
        return HttpResponse(content=json.dumps(timetable, ensure_ascii=False, indent=2),
                            content_type='application/json')

    # >> > coursedetil = course.coursetime_set.all().values_list('CourseWeek', 'CourseTime')
    # >>  coursedet>il
    # < QuerySet[('2-9', '20304')] >
    # >> > coursedetil[0]
    # ('2-9', '20304')

    # 节流查询数据
    # elif _cont==1:
    #
    #     return HttpResponse(content=req, content_type='application/json')

# def process_coureselib_data():

# def get_croom_course(request):
#     postbody = request.body
#     print(postbody)
#     json_param = json.loads(postbody.decode())
#     _cont = json_param.get("cont")
#     _page = json_param.get("page")
#
#     # 返回所有的教室
#     if _cont==0:
#         Class_ord=CourseTime.objects.all().distinct().values_list("CoursePlace")
#         # 如何区分教室顺序？还有空教室渲染问题。这个教室部分之后搞。
#         Class_list = [[] for k in range(len(Class_ord))]
#         for index in range(len(Class_ord)):
#             Class_list[index]=Class_ord[index][0]
#         Course_lib_json = json.dumps(Course_lib_list)
#         print(Course_lib_json)
#         print(type(Course_lib_json))
#         return HttpResponse(content=Course_lib_json, content_type='application/json')
#     # 返回教室课表
#     elif _cont == 1:
#         _toweek= json_param.get('toweek')
#         # _coursename = json_param.get('coursename')
#         # _teachername = json_param.get('teachername')
#         # _cont = json_param.get("cont")
#         # _page = json_param.get("page")
#         # 判断是否传入周数
#         print(isinstance(_toweek,int))
#         if _toweek==None and not isinstance(_toweek,int):
#             error = {
#                 "code": 4009,
#                 "message": "Begin Data Error"
#             }
#             error = json.dumps(error)
#             print(error)
#             return HttpResponse(content=error, content_type='application/json')
#         # 正式请求，请求课程数据，要求给课程ID；然后我给出详细的数据，包括课程名称，教室，老师名字，课程时间；
#         _id = json_param.get("id")
#         try:
#             Course_id=Course.objects.get(id=_id)
#         except:
#             error = {
#                 "code": 4009,
#                 "message": "Begin Data Error"
#             }
#             error = json.dumps(error)
#             print(error)
#             return HttpResponse(content=error, content_type='application/json')
#         print(Course_id)
#         Course_detail = Course_id.coursetime_set.all().values_list('CourseWeek', 'CourseTime',"CoursePlace")
#         print(len(Course_detail))
#         print(Course_detail[0][1])
#         Course_timetable = [[[[] for j in range(5)] for i in range(5)] for k in range(7)]  # 课程
#         print("xxxxxxxxxxxxxxxxxxxxxxxxxx")
#         for index in range(len(Course_detail)):#dh_fg课程为一个数组,里面存储的两个时间
#
#             dh_fg=Course_detail[index][0].split(',')#存储的几个星期时间
#
#             end_fg = [[[],[]] for k in range(len(dh_fg))]#第一个是几个时间，第二个是开始时间和结束时间
#             get_time = Course_detail[index][1]
#             get_place=Course_detail[index][2]
#             week_time = int(get_time[3] + get_time[4])
#             week_time = int(week_time/2) - 1 #节数
#             print("_______sdsadsadsad___________")
#             for hg_i in range(len(dh_fg)):#end_fg课程为一个二维数组，
#                 process_data=dh_fg[hg_i].split('-')
#                 print(Course_id.CourseName)
#                 print(get_place)
#                 print(Course_id.CourseTeacher)
#                 if len(process_data)==2:
#                     end_fg[hg_i][0] = int(process_data[0])
#                     end_fg[hg_i][1] = int(process_data[1])
#                     # 判断本周有没有这个课程
#                     if end_fg[hg_i][0] <= _toweek and end_fg[hg_i][1] >= _toweek:
#                         kcsj_day = int(get_time[0]) - 1
#                         print(kcsj_day)
#                         print(week_time)
#                         # 课程名称
#                         Course_timetable[kcsj_day][week_time][0] = Course_id.CourseName
#                         # 上课地址
#                         Course_timetable[kcsj_day][week_time][1] = get_place
#                         # 老师名称
#                         Course_timetable[kcsj_day][week_time][2] = Course_id.CourseTeacher
#                 elif len(process_data)==1:
#                     end_fg[hg_i][0] = int(process_data[0])
#                     # 判断本周有没有这个课程
#                     if end_fg[hg_i][0] == _toweek :
#                         kcsj_day = int(get_time[0]) - 1
#                         # 课程名称
#                         Course_timetable[kcsj_day][week_time][0] = Course_id.CourseName
#                         # 上课地址
#                         Course_timetable[kcsj_day][week_time][1] = get_place
#                         # 老师名称
#                         Course_timetable[kcsj_day][week_time][2] = Course_id.CourseTeacher
#
#         str_json = json.dumps(Course_timetable, ensure_ascii=False, indent=2)
#         # print(str_json)
#         return HttpResponse(content=str_json, content_type='application/json')
# 如何区分教学楼和教室？
# 教室的表现形式是什么



#废弃区
def LogininfoQZ(request):
    # 检验POST
    if request.method != 'POST':
        error = {
            "code": 4000,
            "message": "Invalid Request Method"
        }
        return HttpResponse(content=json.dumps(error), content_type='application/json', status=400)
    # 读取POST请求的数据
    try:
        post_data = json.loads(request.body.decode())
    except json.JSONDecodeError:
        error = {
            "code": 4001,
            "message": "Invalid Request Body"
        }
        return HttpResponse(content=json.dumps(error), content_type='application/json', status=400)
    account = post_data.get('account')
    password = post_data.get('password')
    if not all([account, password]):
        error = {
            "code": 4002,
            "message": "Missing Account or Password"
        }
        return HttpResponse(content=json.dumps(error), content_type='application/json', status=400)

    #构造请求参数
    params = {
        "method": "authUser",
        "xh": account,
        "pwd": password
    }
    global HEADERS, url
    session = requests.Session()
    try:
        req = session.get(url, params=params, timeout=5, headers=HEADERS)
        s = req.json()
    except requests.exceptions.RequestException:
        # 如果请求出错，返回4001错误
        error = {"code": 4001, "message": "Session Error"}
        return JsonResponse(error, status=400)
    # 检查是否登录成功
    if s.get("flag") != "1":
        # 如果登录不成功，返回400错误
        error = {"code": 4000, "message": "Invalid Login"}
        return JsonResponse(error, status=400)
    # 保存cookie
    session_token = s.get("token")
    print(session_token)
    # 返回cookie和token
    response_data = {
        "token": session_token
    }
    return HttpResponse(content=json.dumps(response_data), content_type='application/json')
def ClassInfoQZ(request):
    global url,HEADERS
    # 获取请求体中的参数
    try:
        postbody = request.body
        json_param = json.loads(postbody.decode())
        _account = json_param.get('account')
        _password = json_param.get('password')
        zc = json_param.get("cont", -1)
        token = json_param.get("token")
        HEADERS["token"] = token
    except Exception as e:
        # 处理请求体中参数解析错误的情况
        error = {"code": 4000, "message": "Invalid Parameters"}
        return JsonResponse(error)
    # 建立一个 requests session 并设置 cookies
    session = requests.Session()

    # 请求接口，获取当前学期和周次信息
    params = {"method": "getCurrentTime", "currDate": datetime.datetime.now().strftime("%Y-%m-%d")}
    try:
        req = session.get(url, params=params, timeout=15, headers=HEADERS)
        s = json.loads(req.text)
        # 处理获取周次信息失败的情况
        if s.get("zc") is None:
            error = {"code": 4006, "message": "QZ Error"}
            return JsonResponse(error)
    except Exception as e:
        print("请求错误：", e)  # 输出异常信息
        # 处理 session 对话错误的情况
        error = {"code": 4001, "message": "Session Error"}
        return JsonResponse(error)

    # 获取到当前学期和周次信息后，请求获取课表数据接口
    params = {"method": "getKbcxAzc", "xnxqid": s["xnxqh"], "zc": s["zc"] if zc == -1 else zc, "xh": _account}
    try:
        req = session.get(url, params=params, timeout=15, headers=HEADERS)
        table_ord = json.loads(req.text)
        print(req.text)
        # 处理获取课表数据失败的情况
        if table_ord[0] is None:
            return JsonResponse([])
    except Exception as e:
        # 处理获取课表数据错误的情况
        print("请求错误：", e)  # 输出异常信息
        error = {"code": 4001, "message": "Session Error"}
        return JsonResponse(error)



    # 将爬取到的数据转成前端需要的数据，格式转换
    tablesame = [[-1 for j in range(2)] for k in range(35)]
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
    table = [[[[] for j in range(5)] for i in range(5)] for k in range(7)]#课程
    flag_i_color = 0  # 进行表的比对，如果same表存在就直接用颜色，不存在就给个新颜色，新颜色用到的
    for newtable in table_ord:
        try:
            # 解析课程信息
            get_kcmc = newtable.get("kcmc")  # 课程名称
            get_jsmc = newtable.get("jsmc")  # 上课教室
            get_jsxm = newtable.get("jsxm")  # 老师名称
            get_kkzc = newtable.get("kkzc")  # 上课星期
            get_kcsj = newtable.get("kcsj")  # 上课时间
            # 将课程信息存入表格
            kcsj_day = int(get_kcsj[0]) - 1
            cout = int(get_kcsj[3] + get_kcsj[4])
            cout = int(cout / 2) - 1
            # 课程名称
            table[kcsj_day][cout][0] = get_kcmc
            # 上课地址
            table[kcsj_day][cout][1] = get_jsmc
            # 老师名称
            table[kcsj_day][cout][2] = get_jsxm

            Courseresult = Course.objects.filter(CourseName=get_kcmc, CourseTeacher=get_jsxm)
            # 所有东西都存储说明我存储了课，这样不会有重复的课
            # 我没有存储这个课
            if not Courseresult.exists():
                NewCourse = Course.objects.create(CourseName=get_kcmc, CourseTeacher=get_jsxm)
                NewCourse.save()
                NewCourseTime = CourseTime.objects.create(CourseTime=get_kcsj, CourseWeek=get_kkzc, CourseId=NewCourse,
                                                          CoursePlace=get_jsmc)
                NewCourseTime.save()
            # 我已经存储这个课
            else:
                # 现在看看有没有存储这个课的时间
                Course_result = Course.objects.get(CourseName=get_kcmc, CourseTeacher=get_jsxm)
                CourseTimeresult = Course_result.coursetime_set.all().values_list('CourseTime')
                flag_time = True  # 没有相等的
                for time_i in CourseTimeresult:
                    if time_i[0] == get_kcsj:
                        flag_time = False  # 存在相等的
                        break
                # 不存在相等的时间，我要不要记录星期有没有时间相同星期不同？除非后期调课，原来的课调走后面的课然后调到相同时间这时会漏读多读。
                if flag_time == True:
                    NewCourseTime = CourseTime.objects.create(CourseTime=get_kcsj, CourseWeek=get_kkzc,
                                                              CourseId=Course_result,
                                                              CoursePlace=get_jsmc)
                    NewCourseTime.save()

            # 给颜色
            for tablesame_i in tablesame:
                if tablesame_i[0] == get_kcmc:
                    table[kcsj_day][cout][3] = tablesame_i[1]
                    break
                if tablesame_i[0] == -1:
                    tablesame_i[0] = get_kcmc
                    tablesame_i[1] = tablecolor[flag_i_color]
                    flag_i_color += 1
                    if flag_i_color>5:
                        flag_i_color = flag_i_color % 7
                    table[kcsj_day][cout][3] = tablesame_i[1]
                    break
        except Exception as e:
            # 添加异常处理机制
            return HttpResponse(content=f"An error occurred: {e}", status=500)
    # 将表格转换成 JSON 格式并返回
    try:
        str_json = json.dumps(table, ensure_ascii=False, indent=2)
        return HttpResponse(content=str_json, content_type='application/json')
    except Exception as e:
        # 添加异常处理机制
        return HttpResponse(content=f"An error occurred: {e}", status=500)


def StudentInfoQZ(request):
    # 解析请求体
    if request.method != 'POST':
        error = {
            "code": 4003,
            "message": "Invalid request method"
        }
        error = json.dumps(error)
        return HttpResponse(content=error, content_type='application/json')

    try:
        json_param = json.loads(request.body.decode())
        _account = json_param.get('account')
        _password = json_param.get('password')
        token=json_param.get("token")
        HEADERS["token"] = token
    except json.decoder.JSONDecodeError:
        error = {
            "code": 4000,
            "message": "Invalid request body"
        }
        error = json.dumps(error)
        return HttpResponse(content=error, content_type='application/json')



    session = requests.Session()

    params = {
        "method": "getUserInfo",
        "xh": _account
    }


    HEADERS["token"] = token
    print(HEADERS)

    try:
        req = session.get(url, params=params, timeout=5, headers=HEADERS)
    except:
        error = {
            "code": 4001,
            "message": "Session Error"
        }
        error = json.dumps(error)
        return HttpResponse(content=error, content_type='application/json')

    data = json.loads(req.text)
    if data.get('token') == '-1':
        error = {
            "code": 4009,
            "message": "Token=-1"
        }
        error = json.dumps(error)
        return HttpResponse(content=error, content_type='application/json')
    elif req.status_code != 200:
        error = {
            "code": 4004,
            "message": "Bad Request"
        }
        error = json.dumps(error)
        return HttpResponse(content=error, content_type='application/json')

    print(req.text)
    # 更新用户信息
    try:
        user_obj = User.objects.get(Snumber=_account)
    except User.DoesNotExist:
       user_obj = User.objects.create(Snumber=int(data.get('xh', '')), Name=data.get('xm', ''), PasswordQZ=_password,
                                           Classname=data.get('bj', ''), Majorname=data.get('zymc', ''), Collegename=data.get('yxmc', ''),
                                           Enteryear=int(data.get('rxnf', '')), Gradenumber=int(data.get('usertype', '')))
       user_obj.save()
       print("对新用户进行了创建用户表操作")
    else:
        if user_obj.PasswordQZ != _password:
            user_obj.PasswordQZ = _password
            user_obj.save()
            print("对新用户进行了更新密码的操作")

    share_obj, created = Share.objects.get_or_create(Usernumber_id=_account)
    # 创建共享表
    if created:
        print("对新用户进行了创建共享表操作")
    else:
        print("共享表已存在")

    if req.status_code == 200:
        data = json.loads(req.text)
        return JsonResponse(data, safe=False)
    else:
        error = {
            "code": 4004,
            "message": "Bad Request"
        }
        error = json.dumps(error)
        return HttpResponse(content=error, content_type='application/json')

def CurrentTimeQZ(request):
    """
    获取当前时间的视图函数
    """
    if request.method == "POST":
        # 从请求体中解析参数
        try:
            json_param = json.loads(request.body.decode())
        except json.JSONDecodeError:
            error = {
                "code": 4000,
                "message": "Invalid JSON format"
            }
            return HttpResponse(json.dumps(error), content_type='application/json', status=400)

        # 检查必要参数
        _account = json_param.get('account')
        _password = json_param.get('password')
        token = json_param.get("token")
        if not (_account and _password  and token):
            error = {
                "code": 4002,
                "message": "Missing parameter"
            }
            return HttpResponse(json.dumps(error), content_type='application/json', status=400)

        # 设置请求头
        HEADERS["token"] = token

        # 解析 cookie 字符串并创建会话
        try:

            session = requests.Session()
        except:
            error = {
                "code": 4008,
                "message": "Login Error"
            }
            return HttpResponse(json.dumps(error), content_type='application/json', status=400)

        # 构造 GET 请求参数
        params = {
            "method": "getCurrentTime",
            "currDate": datetime.datetime.now().strftime("%Y-%m-%d")
        }

        # 发送请求
        try:
            req = session.get(url, params=params, timeout=5, headers=HEADERS)
            req.raise_for_status()  # 检查响应状态码是否为 200
        except requests.exceptions.RequestException as e:
            error = {
                "code": 4001,
                "message": "Session Error"
            }
            return HttpResponse(json.dumps(error), content_type='application/json', status=400)

        # 返回响应结果
        return HttpResponse(req.content, content_type='application/json')

    else:
        error = {
            "code": 4003,
            "message": "Invalid request method"
        }
        return HttpResponse(json.dumps(error), content_type='application/json', status=405)
