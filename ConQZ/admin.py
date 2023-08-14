from django.contrib import admin

# Register your models here.
# 注册模型类
from .models import User,Share,DepartmentClass,Course,LikesInfo,CourseTime,CourseSchedule
admin.site.register(User)
admin.site.register(Share)
admin.site.register(DepartmentClass)
admin.site.register(LikesInfo)
admin.site.register(Course)
admin.site.register(CourseTime)
admin.site.register(CourseSchedule)

