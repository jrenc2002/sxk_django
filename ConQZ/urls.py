
from django.urls import path, include

from ConQZ import views

urlpatterns = [
    # http://192.168.21.128:8000/qz/get_login_info/
    path('get_login_info/',views.get_login_info),
    # http://192.168.21.128:8000/qz/get_student_info/
    path('get_student_info/',views.get_student_info),
    # http://192.168.21.128:8000/qz/get_current_time/
    path('get_current_time/',views.get_current_time),
    # http://192.168.21.128:8000/qz/get_class_info/
    path('get_class_info/',views.get_class_info),
    # # http://192.168.21.128:8000/qz/get_classroom_info/
    path('get_classroom_info/',views.get_classroom_info),
    # # http://192.168.21.128:8000/qz/get_grade_info/
    path('get_grade_info/',views.get_grade_info),
    # # http://192.168.21.128:8000/qz/get_exam_info/
    path('get_exam_info/',views.get_exam_info),
    # # http://192.168.21.128:8000/qz/get_share_state/
    path('get_share_state/',views.get_share_state),
    # # http://192.168.21.128:8000/qz/post_share_info/
    path('post_share_info/',views.post_share_info),
    # # http://192.168.21.128:8000/qz/reply_share_info/
    path('reply_share_info/', views.reply_share_info),
    # # http://192.168.21.128:8000/qz/get_share_info/
    path('get_share_info/', views.get_share_info),
    # # http://192.168.21.128:8000/qz/get_phonebook_info/
    path('get_phonebook_info/', views.get_phonebook_info),
    # # http://192.168.21.128:8000/qz/get_courselib/
    path('get_courselib/', views.get_courselib),
]