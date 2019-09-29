from django.contrib import admin
from . import models

class UserInfo(admin.ModelAdmin):
    list_display = ['username','email','has_confirmed','buy_devices_count','registration_datetime']

class Email_Confirm(admin.ModelAdmin):
    list_display = ['user','code','c_time']

class IpaPackage(admin.ModelAdmin):
    list_display = ['userinfo','display_name','version','distribution_url','upload_datetime','installed_amount']

class UDID(admin.ModelAdmin):
    list_display = ['userinfo','product','udid','request_distribution_url','deveploer_account','request_datetime']

class DeveloperAccount(admin.ModelAdmin):
    list_display = ['username','used_device_count']


admin.site.register(models.UserInfo,UserInfo)
admin.site.register(models.ConfirmString,Email_Confirm)
admin.site.register(models.UDID,UDID)
admin.site.register(models.DeveloperAccount,DeveloperAccount)
admin.site.register(models.IpaPackage,IpaPackage)

admin.site.site_title = '后台管理'
admin.site.site_header = 'Giao超级签名管理平台'
admin.site.index_title = 'IOS超级签名'