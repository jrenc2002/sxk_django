
from django.urls import path, include

from ConQZ import views

app_name = 'qz'

urlpatterns = [
    # 用户登录信息
    path('login-info/', views.Logininfo, name='login-info'),
    # 课程信息
    path('class-info/', views.PostClassInfo, name='class-info'),
    # 共享状态信息
    path('share-state/', views.GetShareState, name='share-state'),
    # 共享信息发布
    path('share-state/post/', views.PostShareState, name='share-info'),
    # 共享信息回复
    path('share-state/reply/', views.ReplyShareState, name='share-info-reply'),
    # 获取共享信息
    path('share-info/get/', views.GetShareInfo, name='share-info-detail'),
    path('share-dept/create/', views.CreateDept, name='create_dept'),
    path('share-dept/join/', views.JoinDept, name='join_dept'),
    path('share-dept/quit/', views.QuitDept, name='quit_dept'),
    path('share-dept/dis/', views.DismissDept, name='dismiss_dept'),
    path('share-dept/kick/', views.KickDept, name='kick_dept'),
    path('share-dept/get/', views.GetDeptInfo, name='kick_dept'),
    path('share-dept/get-member/', views.GetDepartmentMemberInfo, name='get_dept_member'),
    path('share-week/state/', views.GetWeekPostState, name='get_week_post_state'),
    # 电话簿信息
    path('phonebook-info/', views.GetPhonebookInfo, name='phonebook-info'),
    # 课程库信息
    path('course-lib/', views.GetCourselib, name='course-lib'),
    path('course-lib/detail/', views.GetLibdetail, name='course-lib-detail'),
    # # 空教室信息
    # path('empty-classroom-info/', views.EmptyClassroomInfo, name='empty-classroom-info'),
    # # 成绩信息
    # path('grade-info/', views.GradeInfo, name='grade-info'),
    # # 考试信息
    # path('exam-info/', views.ExamInfo, name='exam-info')
]
