
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
    path('get_exam_info/',views.get_exam_info)
]