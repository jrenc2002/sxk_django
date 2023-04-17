
from django.urls import path, include

from ConQZ import views

app_name = 'qz'

urlpatterns = [
    # 用户登录信息
    path('login-info/', views.Logininfo, name='login-info'),
    # 学生信息

    # path('student-info/', views.StudentInfo, name='student-info'),
    # # 当前时间
    # path('current-time/', views.CurrentTime, name='current-time'),
    # # 班级信息

    path('class-info/', views.ClassInfo, name='class-info'),
    # 空教室信息

    path('empty-classroom-info/', views.EmptyClassroomInfo, name='empty-classroom-info'),
    # 成绩信息

    path('grade-info/', views.GradeInfo, name='grade-info'),
    # 考试信息

    path('exam-info/', views.ExamInfo, name='exam-info'),
    # 分享状态信息

    path('share-state/', views.GetShareState, name='share-state'),
    # 分享信息发布
    path('share-state/post/', views.PostShareInfo, name='share-info'),
    # 分享信息回复

    path('share-state/reply/', views.ReplyShareInfo, name='share-info-reply'),
    # 获取分享信息

    path('share-info/get/', views.GetShareInfo, name='share-info-detail'),
    # 电话簿信息

    path('phonebook-info/', views.GetPhonebookInfo, name='phonebook-info'),
    # 课程库信息
    path('course-lib/', views.GetCourselib, name='course-lib'),
]
