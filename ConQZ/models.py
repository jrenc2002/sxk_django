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


