
from django.urls import path, include

from ConQZ import views

urlpatterns = [

    path('get_login_info/',views.get_login_info)

]