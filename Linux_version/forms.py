from django import forms
from captcha.fields import CaptchaField

class LoginForm(forms.Form):
    """登录表单"""
    username = forms.CharField(max_length=128, min_length=6, label='用户名',
                               widget=forms.TextInput(attrs={'placeholder': "Username", 'autofocus': ''}))
    password = forms.CharField(max_length=128, min_length=8, label='密码',
                               widget=forms.PasswordInput(attrs={'placeholder': "Password"}))
    captcha = CaptchaField(label='验证码',error_messages={'invalid':'验证码错误'})

class RegisterForm(forms.Form):
    """注册表单"""
    username = forms.CharField(label='用户名', max_length=128, min_length=6, widget=forms.TextInput)
    password1 = forms.CharField(label='密码', max_length=128, min_length=8, widget=forms.PasswordInput)
    password2 = forms.CharField(label='确认密码', max_length=128, min_length=8, widget=forms.PasswordInput)
    email = forms.EmailField(label='邮箱地址', widget=forms.EmailInput)
    captcha = CaptchaField(label='验证码',error_messages={'invalid':'验证码错误'})

class UploadFileForm(forms.Form):
    """文件上传表单"""
    file = forms.FileField(label='选择文件')