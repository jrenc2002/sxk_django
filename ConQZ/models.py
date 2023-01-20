from django.db import models

# Create your models here.
class User(models.Model):
    Snumber =models.BigIntegerField('学号',primary_key=True)
    Name=models.CharField('名称',max_length=20,default='')
    PasswordQZ=models.CharField('强智密码',max_length=50,default='')
    Classname=models.CharField('班级名称',max_length=50,default='')
    Majorname=models.CharField('专业名称',max_length=50,default='')
    Collegename=models.CharField('学院名称',max_length=50,default='')
    Enteryear=models.IntegerField('入学年份',default='')
    Gradenumber=models.IntegerField('当前年级',default='')

class Share(models.Model):
    Usernumber = models.OneToOneField(User,verbose_name='学号',on_delete=models.PROTECT, primary_key=True)
    CBindState=models.IntegerField('课程绑定状态',default=0,blank=True,null=True)
    CBindNumber=models.BigIntegerField('课程绑定学号',default=-1,blank=True,null=True)
    GBindState=models.IntegerField('成绩绑定状态',default=0,blank=True,null=True)
    GBindNumber=models.BigIntegerField('成绩绑定学号',default=-1,blank=True,null=True)

class LikesInfo(models.Model):
   Groupname=models.CharField('同好名称',max_length=30,default='')
   QQGroupNumber=models.CharField('同好群号',max_length=50,default='')
   InfoContent=models.TextField('介绍内容')
   LikesStatic=models.ImageField('同好群文件路径',blank=True,null=True)

class Course(models.Model):
   CourseName=models.CharField('课程名称',max_length=100,default='')
   CoursePlace=models.CharField('上课地点',max_length=100,default='')
   CourseTeacher=models.CharField('教师名称',max_length=20,default='')
class CourseTime(models.Model):
   CourseId = models.ForeignKey(Course, verbose_name='课程编号', on_delete=models.CASCADE)
   CourseTime=models.CharField('上课时间',max_length=20,default='')
   CourseWeek=models.CharField('上课周数',max_length=20,default='')

