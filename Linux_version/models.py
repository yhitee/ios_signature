from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver


class UserInfo(models.Model):
    """用户信息"""
    username = models.CharField(max_length=128, unique=True, verbose_name='用户名')
    password = models.CharField(max_length=128, verbose_name='密码')
    email = models.EmailField(unique=True, verbose_name='邮箱')
    has_confirmed = models.BooleanField(default=False, verbose_name='是否确认')
    buy_devices_count = models.IntegerField(default=0, verbose_name='购买下载量')
    registration_datetime = models.DateTimeField(auto_now_add=True, verbose_name='注册时间')

    def __str__(self):
        return self.username

    class Meta:
        ordering = ['-registration_datetime']
        verbose_name = '用户信息'
        verbose_name_plural = '用户信息'


class ConfirmString(models.Model):
    """用户邮件注册确认"""
    code = models.CharField(max_length=256, verbose_name='确认码')
    user = models.OneToOneField(to='UserInfo', on_delete=models.CASCADE, verbose_name='用户')
    c_time = models.DateTimeField(auto_now_add=True, verbose_name='生成时间')

    def __str__(self):
        return self.user.username

    class Meta:
        ordering = ['-c_time']
        verbose_name = '邮件确认码'
        verbose_name_plural = '邮件确认码'


class UDID(models.Model):
    """IOS设备信息"""
    userinfo = models.ForeignKey(to='UserInfo', on_delete=models.CASCADE, verbose_name='所属用户')
    product = models.CharField(max_length=64, blank=True, null=True, verbose_name='设备型号')
    udid = models.CharField(max_length=128, verbose_name='设备UDID')
    request_distribution_url = models.CharField(max_length=240, blank=True, null=True, verbose_name='请求的分发链接')
    deveploer_account = models.ForeignKey(to='DeveloperAccount', on_delete=models.CASCADE, blank=True, null=True,
                                          verbose_name='重签的开发者账号')
    request_datetime = models.DateTimeField(auto_now_add=True, verbose_name='请求时间')

    def __str__(self):
        return self.udid

    class Meta:
        ordering = ['-request_datetime']
        verbose_name = 'IOS设备信息'
        verbose_name_plural = 'IOS设备信息'


def p12_path(instance, filename):
    """苹果开发者账号models回调函数"""
    return '/'.join(['p12_files', instance.username, filename])


class DeveloperAccount(models.Model):
    """苹果开发者账号"""
    username = models.CharField(max_length=64, unique=True, verbose_name='开发者账号')
    password = models.CharField(max_length=128, verbose_name='密码')
    p12_file = models.FileField(upload_to=p12_path, verbose_name='P12文件路径')
    used_device_count = models.IntegerField(default=0, verbose_name='已使用设备数量')

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = '开发者账号'
        verbose_name_plural = '开发者账号'


@receiver(pre_delete, sender=DeveloperAccount)
def p12_file_delete(sender, instance, **kwargs):
    """删除P12对象时,一并删除上传的文件"""
    instance.p12_file.delete(False)


def user_directory_path(instance, filename):
    """IPA包信息models回调函数"""
    return '/'.join(['ipa_files', instance.userinfo.username, filename])


class IpaPackage(models.Model):
    """IPA包信息"""
    userinfo = models.ForeignKey(to='UserInfo', on_delete=models.CASCADE, verbose_name='所属用户')
    ipaupload_path = models.FileField(upload_to=user_directory_path, verbose_name='文件相对路径')
    absolute_path = models.CharField(max_length=256, verbose_name='文件绝对路径', blank=True, null=True)
    display_name = models.CharField(max_length=64, default='Not Found App Name', verbose_name='App名称')
    bundid_before = models.CharField(max_length=128, blank=True, null=True, verbose_name='原Bundle ID')
    bundid_after = models.CharField(max_length=128, blank=True, null=True, verbose_name='重签后Bundle ID')
    version = models.CharField(max_length=32, blank=True, null=True, verbose_name='版本')
    appid_name = models.CharField(max_length=128, blank=True, null=True, verbose_name='AppID名称')
    distribution_url = models.URLField(blank=True, null=True, verbose_name='分发链接')
    file_size = models.FloatField(default=0.0, blank=True, null=True, verbose_name='文件大小(M)')
    installed_amount = models.IntegerField(default=0, blank=True, null=True, verbose_name='安装数量')
    upload_datetime = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')

    def __str__(self):
        return self.display_name

    class Meta:
        ordering = ['-upload_datetime']
        verbose_name = 'IPA包信息'
        verbose_name_plural = 'IPA包信息'


@receiver(pre_delete, sender=IpaPackage)
def ipa_file_delete(sender, instance, **kwargs):
    """删除IPAPackage对象时,一并删除上传的文件"""
    instance.ipaupload_path.delete(False)
