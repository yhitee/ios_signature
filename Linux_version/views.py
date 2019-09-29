from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from . import models
from . import forms
import re, os, subprocess, time, zipfile, plistlib, string, random, hashlib, datetime, json


######################################################## PC端 #########################################################

def hash_code(s, salt='mysite'):
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())
    return h.hexdigest()


def make_confirm_string(user):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    code = hash_code(user.username, now)
    models.ConfirmString.objects.create(code=code, user=user)
    return code


def send_email(username, password, email, code):
    subject = '来自%s的注册确认邮件' % (settings.WEBSITE_DOMAIN,)
    text_content = '''感谢注册%s，这里是ios分发平台站点，如果你看到这条消息，
    说明你的邮箱服务器不提供HTML链接功能，请联系管理员！''' % (settings.WEBSITE_DOMAIN,)
    html_content = '''<p>感谢注册<a href="http://%s/emailconfirm/?code=%s" target=blank>%s</a></p>
    <p>您的用户名:%s , 密码:%s</p>
    <p>请点击站点链接完成注册确认！</p>
    <p>此链接有效期为%s天！</p>''' % (
        settings.WEBSITE_DOMAIN, code, settings.WEBSITE_DOMAIN, username, password, settings.CONFIRM_DAYS)
    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()


def get_ipapackage_information(path):
    information = []
    f = zipfile.ZipFile(path)
    file_pattern = re.compile(r'Payload/[^/]*.app/Info.plist')
    for paths in f.namelist():
        m = file_pattern.match(paths)
        if m is not None:
            content = f.read(m.group())
            plist_root = plistlib.loads(content)
            information.append(plist_root['CFBundleIdentifier'])  # BundleID
            information.append(plist_root['CFBundleShortVersionString'])  # version
            try:
                information.append(plist_root['CFBundleDisplayName'])  # Displayname
            except:
                information.append('Not Found App Name')
            return information


def index(request):
    """网站首页"""
    return render(request, 'pc/index.html')


def laws(request):
    """法律法规"""
    return render(request, 'pc/lawsregulations.html')


def register(request):
    """用户注册"""
    if request.session.get('is_login', None):
        return redirect('index')
    if request.method == 'POST':
        register_form = forms.RegisterForm(request.POST)
        message = '请检查填写的内容'
        if register_form.is_valid():
            username = register_form.cleaned_data.get('username')
            password1 = register_form.cleaned_data.get('password1')
            password2 = register_form.cleaned_data.get('password2')
            email = register_form.cleaned_data.get('email')
            if password1 != password2:
                message = '两次输入的密码不一致'
                return render(request, 'pc/register.html', locals())
            else:
                same_name_user = models.UserInfo.objects.filter(username=username)
                if same_name_user:
                    message = '用户名已存在'
                    return render(request, 'pc/register.html', locals())

                same_email_user = models.UserInfo.objects.filter(email=email)
                if same_email_user:
                    message = '该邮箱已被注册'
                    return render(request, 'pc/register.html', locals())

                new_user = models.UserInfo()
                new_user.username = username
                new_user.password = password1
                new_user.email = email
                new_user.save()

                code = make_confirm_string(new_user)
                try:
                    send_email(username, password1, email, code)
                except:
                    message = '邮件发送失败'
                    return render(request, 'pc/confirmskip.html', locals())

                message = '注册成功！请前往邮箱进行确认,正在跳转至登录...'
                return render(request, 'pc/confirmskip.html', locals())
        else:
            return render(request, 'pc/register.html', locals())
    register_form = forms.RegisterForm()
    return render(request, 'pc/register.html', locals())


def email_confirm(request):
    """注册邮件确认"""
    code = request.GET.get('code', None)
    message = ''
    try:
        confirm = models.ConfirmString.objects.get(code=code)
    except:
        message = '无效的确认请求...'
        return render(request, 'pc/confirmskip.html', locals())
    c_time = confirm.c_time
    now = datetime.datetime.now()
    if now > c_time + datetime.timedelta(settings.CONFIRM_DAYS):
        confirm.user.delete()
        message = '您的邮件已经过期，请重新注册...'
        return render(request, 'pc/confirmskip.html', locals())
    else:
        confirm.user.has_confirmed = True
        confirm.user.save()
        confirm.delete()
        message = '邮箱确认成功，正在跳转至登录...'
        return render(request, 'pc/confirmskip.html', locals())


def login(request):
    """用户登录"""
    if request.session.get('is_login', None):
        return redirect('index')
    if request.method == 'POST':
        login_form = forms.LoginForm(request.POST)
        message = '请检查填写的内容'
        if login_form.is_valid():
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')
            try:
                user = models.UserInfo.objects.get(username=username)
            except:
                message = '用户不存在'
                return render(request, 'pc/login.html', locals())

            if not user.has_confirmed:
                message = '该用户还未经过邮件确认'
                return render(request, 'pc/login.html', locals())
            if user.password == password:
                request.session['is_login'] = True
                request.session['user_id'] = user.id
                request.session['user_name'] = user.username
                return redirect('index')
            else:
                message = '密码错误'
                return render(request, 'pc/login.html', locals())
        else:
            return render(request, 'pc/login.html', locals())
    else:
        login_form = forms.LoginForm()
    return render(request, 'pc/login.html', locals())


def logout(request):
    """用户注销"""
    if not request.session.get('is_login', None):
        return redirect('login')
    del request.session['is_login']
    del request.session['user_id']
    del request.session['user_name']
    return redirect('index')


def nologinskip(request):
    """未登录跳转"""
    return render(request, 'pc/nologinskip.html')


def distribution_management(request):
    """超级签名应用"""
    if not request.session.get('is_login', None):
        return redirect('nologinskip')
    user_id = request.session.get('user_id', None)

    if request.GET.get('delete') == 'true':
        Query_Information = models.IpaPackage.objects.filter(userinfo_id=user_id,
                                                             distribution_url=request.GET.get('distribution_url'))
        Query_Information.delete()
        return redirect(reverse('distribute_management'))

    try:
        user_Package_information = models.IpaPackage.objects.filter(userinfo_id=user_id)
        UDID_Information = models.UDID.objects.filter(userinfo_id=user_id)
        for Package in user_Package_information:
            for udid_info in UDID_Information:
                if udid_info.request_distribution_url == Package.distribution_url:
                    Install_Count = UDID_Information.filter(request_distribution_url=Package.distribution_url).values(
                        'udid', 'request_distribution_url').order_by('request_distribution_url').distinct().count()
                    user_Package_information.filter(distribution_url=udid_info.request_distribution_url).update(
                        installed_amount=Install_Count)
        USER_PACKAGE_INFORMATION = models.IpaPackage.objects.filter(userinfo_id=user_id)
        User_Buy_Devices_Count = models.UserInfo.objects.filter(id=user_id)[0].buy_devices_count
        User_Used_Devices_Count = models.UDID.objects.filter(userinfo_id=user_id).values('udid').order_by(
            'udid').distinct().count()
        if User_Buy_Devices_Count == 0:
            Percent = 0
        else:
            Percent = int(round(User_Used_Devices_Count / User_Buy_Devices_Count, 2) * 100)
    except:
        message = 'Database query Error, please contact webmaster!'
        return render(request, 'pc/distribution.html', locals())

    return render(request, 'pc/distribution.html', locals())


def ipapackage_upload(request):
    """IPA包上传"""
    if not request.session.get('is_login', None):
        return redirect('nologinskip')
    username = request.session.get('user_name', None)
    if request.method == 'POST':
        upload_form = forms.UploadFileForm(request.POST, request.FILES)
        if upload_form.is_valid():
            instance = models.IpaPackage()
            instance.ipaupload_path = request.FILES['file']
            user = models.UserInfo.objects.get(username=username)
            instance.userinfo = user
            instance.save()
            try:
                file_size = round(instance.ipaupload_path.size / 1024 / 1024, 2)  # 文件大小
                absolute_path = os.path.join(settings.MEDIA_ROOT, instance.ipaupload_path.name)  # IPA文件绝对路径
                information = get_ipapackage_information(absolute_path)
                bundid_before = information[0]
                version = information[1]
                display_name = information[2]
                bundid_after = bundid_before + settings.DOMAIN_POSTFIX + ''.join(
                    random.sample(string.ascii_letters + string.digits, 6))
                appidName = bundid_after.replace('.', '')
                remove_extend = ''.join(instance.ipaupload_path.name.split('.')[:-1])
                if remove_extend:
                    distribution_url = 'http://%s/%s' % (settings.WEBSITE_DOMAIN, remove_extend)
                else:
                    distribution_url = 'http://%s/%s' % (settings.WEBSITE_DOMAIN, instance.ipaupload_path.name)
                instance.bundid_before = bundid_before
                instance.bundid_after = bundid_after
                instance.version = version
                instance.display_name = display_name
                instance.appid_name = appidName
                instance.distribution_url = distribution_url
                instance.absolute_path = absolute_path
                instance.file_size = file_size
                instance.save()
            except:
                instance.delete()
                message = {'detail_message': 'Error：IPA包信息提取错误，请检查后重新上传！如有疑问，请联系网站管理员'}
                return HttpResponse(json.dumps(message), content_type="application/json")
            message = {'detail_message': 'Success：文件上传成功！'}
        else:
            message = {'detail_message': '不允许上传空文件哟！'}
        return HttpResponse(json.dumps(message), content_type="application/json")
    if request.method == 'GET':
        return render(request, 'pc/distribution.html', locals())


######################################################## IOS端 #########################################################

def ios_request(request, username, ipafilename):
    if username == 'udid_submit' and ipafilename == 'udid_submit':
        product = request.GET.get('product')
        udid = request.GET.get('udid')
        if product and udid:
            request.session['product'] = product
            request.session['udid'] = udid
            message_storage = messages.get_messages(request)
            for User_IOS_Request in message_storage:
                if User_IOS_Request.level == 50:
                    request.session['request_distribution_url'] = str(User_IOS_Request)
                elif User_IOS_Request.level == 51:
                    request.session['Userinfo_id'] = str(User_IOS_Request)
                elif User_IOS_Request.level == 52:
                    request.session['UserName'] = str(User_IOS_Request)
                else:
                    pass
        else:
            return HttpResponse('<h2>Error： Get your UDID Failure！</h2>')
        return redirect(reverse('installapp'))
    else:
        distribute_url = models.IpaPackage.objects.filter(distribution_url=request.build_absolute_uri())
        if not distribute_url:
            return HttpResponse('<h2>Error： 没有查询到分发链接，请检查链接是否正确！</h2>')
        app_size = distribute_url[0].file_size
        version = distribute_url[0].version
        User_IOS_Request_Url = 50
        User_IOS_Request_UserID = 51
        User_IOS_Request_UserName = 52
        messages.add_message(request, User_IOS_Request_Url, message=distribute_url[0].distribution_url)
        messages.add_message(request, User_IOS_Request_UserID, message=distribute_url[0].userinfo_id)
        messages.add_message(request, User_IOS_Request_UserName, message=distribute_url[0].userinfo.username)
        return render(request, 'ios/install_mobileconfig.html', locals())


@csrf_exempt
def udid_receive(request):
    """获取设备UDID"""
    if request.method == 'POST':
        data = request.body
        data_utf = data.decode('utf8', errors='ignore')
        data_format = re.split("<dict>|</dict>", data_utf)[1]
        remove_bin = "".join(data_format.split('\n\t')).strip()
        data_list = re.split("<key>|</key>|<string>|</string>", remove_bin)
        remove_space = [i.strip() for i in data_list if i.strip() != '']
        if 'UDID' in remove_space:
            udid = remove_space[remove_space.index('UDID') + 1]
            product = remove_space[remove_space.index('PRODUCT') + 1].replace(' ', '')
        else:
            return HttpResponse('<h2>Error：Get UDID Fail！</h2>')
    else:
        return HttpResponse('<h2>Error：Your Request Method is GET！</h2>')
    return redirect(
        reverse('ios_request',
                kwargs={'username': 'udid_submit', 'ipafilename': 'udid_submit'}) + '?product=%s&udid=%s' % (
            product, udid), permanent=True)


def installapp(request):
    return render(request, 'ios/install_app.html')


def resignapp(request):
    """后台重签App"""
    ##### 获取session #####
    try:
        product = request.session.get('product')
        udid = request.session.get('udid')
        request_distribution_url = request.session.get('request_distribution_url')
        Userinfo_id = request.session.get('Userinfo_id')
        UserName = request.session.get('UserName')
        del request.session['product']
        del request.session['udid']
        del request.session['request_distribution_url']
        del request.session['Userinfo_id']
        del request.session['UserName']
    except:
        message = {'error_message': 'Error(10001)：获取信息失败，请清除浏览器记录以及缓存后重新打开分发链接安装!', 'code': 2}
        return HttpResponse(json.dumps(message), content_type="application/json")

    ##### 判断当前分发用户是否有足够的下载数 #####
    try:
        User_Buy_Device_Count = models.UserInfo.objects.filter(id=Userinfo_id)[0].buy_devices_count
    except:
        message = {'error_message': 'Error(10002)：获取信息失败，请重新打开分发链接安装!', 'code': 2}
        return HttpResponse(json.dumps(message), content_type="application/json")
    if User_Buy_Device_Count > 0:
        if models.UDID.objects.filter(userinfo_id=Userinfo_id, udid=udid):  # udid已存在当前用户下,则获取之前注册的开发者账号密码
            Account_ID = models.UDID.objects.filter(udid=udid)[0].deveploer_account
            Account_username = Account_ID.username
            Account_password = Account_ID.password
            Account_keychain = Account_ID.iphone_distribute_number
        else:  # 新注册设备
            if models.UDID.objects.filter(Userinfo_id=Userinfo_id).values('udid').order_by(
                    'udid').distinct().count() >= User_Buy_Device_Count:  # 判断下载数是否还有剩余
                message = {'error_message': 'Error(10004)：可用的下载设备数量已达峰值，请联系开发者购买超级签名数量!', 'code': 2}
                return HttpResponse(json.dumps(message), content_type="application/json")
            else:
                ##### 获取可用开发者账号 #####
                Get_Account = models.DeveloperAccount.objects.filter(used_devices_count__lt=100)
                if not Get_Account:
                    message = {'error_message': 'Error(10005)：App 安装失败! 可用IOS超级签名账号已达上限,请联系分发平台处理!', 'code': 2}
                    return HttpResponse(json.dumps(message), content_type="application/json")
                else:
                    Account_username = Get_Account[0].username
                    Account_password = Get_Account[0].password
                    Account_keychain = Get_Account[0].iphone_distribute_number
    else:
        message = {'error_message': 'Error(10003)：开发者尚未购买可下载设备的数量!无法安装此app', 'code': 2}
        return HttpResponse(json.dumps(message), content_type="application/json")

    ##### 获取IPA包中可用信息 #####
    IPAPackage_Model = models.IpaPackage.objects.filter(distribution_url=request_distribution_url)
    bundid_after = IPAPackage_Model[0].bundid_after + Account_keychain[0:6]  # 取开发者账号发布证书的前六位字符串,防止跨账号之后bundid冲突
    appid_name = IPAPackage_Model[0].appid_name + Account_keychain[0:6]
    ipa_absolute_path = IPAPackage_Model[0].absolute_path
    ipa_upload_path = IPAPackage_Model[0].ipaupload_path

    ##### 更新配置描述文件 #####
    Ruby_Script_Path = os.getcwd() + '/ios_super_signature/scripts/updateprofile.rb'
    if os.path.exists('./ios_super_signature/scripts/%s' % UserName) == False:
        os.mkdir('./ios_super_signature/scripts/%s' % UserName)
    Ruby_Command = "ruby %s %s '%s' %s %s %s '%s' '%s'" % (
        Ruby_Script_Path, Account_username, Account_password, product,
        udid, UserName, bundid_after, appid_name)
    try:
        Update_mobileprovision_State = subprocess.Popen(Ruby_Command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                                        shell=True).wait(timeout=120)
    except subprocess.TimeoutExpired as Timeout_Error:
        message = {'error_message': 'Error(10006)：Update mobileprovision File timeout, please contact the developer!',
                   'code': 2}
        return HttpResponse(json.dumps(message), content_type="application/json")
    except Exception as Other_Error:
        message = {
            'error_message': 'Error(10007)：Update mobileprovision File Unknown Error!please contact the developer!',
            'code': 2}
        return HttpResponse(json.dumps(message), content_type="application/json")
    if Update_mobileprovision_State == 0:  # update success
        print("udid:%s update mobileprovision file success!" % (udid,))
        deveploer_account_id = models.DeveloperAccount.objects.filter(username=Account_username)[0].id
        models.UDID.objects.create(product=product, udid=udid, request_distribution_url=request_distribution_url,
                                   Userinfo_id=Userinfo_id, deveploer_account_id=deveploer_account_id)  # 更新完配置文件后写库
        mobileprovision_file_exist_state = os.path.exists(
            './ios_super_signature/scripts/%s/%s.mobileprovision' % (UserName, appid_name,))
        if mobileprovision_file_exist_state == False:
            time.sleep(10)
        if mobileprovision_file_exist_state == False:
            message = {
                'error_message': 'Error(10008)：Download mobileprovision file Fail, please contact the developer!',
                'code': 2}
            return HttpResponse(json.dumps(message), content_type="application/json")
    else:
        # 可能错误：双重认证、跨账号之后bundid_after冲突
        print("Error(10009) udid:%s update mobileprovision file fail!" % (udid,))
        message = {'error_message': 'Error(10009)：Update mobileprovision File Fail, please contact the developer!',
                   'code': 2}
        return HttpResponse(json.dumps(message), content_type="application/json")

    ##### resignAPP #####
    P12_File_Path = models.DeveloperAccount.objects.filter(Developer_Account=deveploer_account_id)[0].p12_file
    if not P12_File_Path:
        print('Error(20010)：Developer Account %s  P12 file get Fail,please check Database!' % (Account_username,))
        message = {'error_message': 'Error(20010)：P12 File Get Fail!,Resign APP Fail,please contact the developer!',
                   'code': 2}
        return HttpResponse(json.dumps(message), content_type="application/json")
    Resign_Command = 'mysisn -f -k ./ios_super_signature/media/%s -m ./ios_super_signature/scripts/%s/%s.mobileprovision -o %s.signed %s' % (
        P12_File_Path, UserName, appid_name, ipa_absolute_path, ipa_absolute_path)
    try:
        Resign_State = subprocess.Popen(Resign_Command, stdout=subprocess.PIPE, shell=True).wait(timeout=60)
    except subprocess.TimeoutExpired as Timeout_Error:
        message = {'error_message': 'Error(20011)：Resign app timeout, please contact the developer!', 'code': 2}
        return HttpResponse(json.dumps(message), content_type="application/json")
    except Exception as Other_Error:
        message = {'error_message': 'Error(20012)：Resign app Unknown Error, please contact the developer!', 'code': 2}
        return HttpResponse(json.dumps(message), content_type="application/json")
    if Resign_State == 0:
        pass
    else:
        message = {'error_message': 'Error(20013)：Resign app Fail, please contact the developer!', 'code': 2}
        return HttpResponse(json.dumps(message), content_type="application/json")

    response = {'ipa_upload_path': '%s' % ipa_upload_path, 'code': 1}
    return HttpResponse(json.dumps(response), content_type="application/json")


def request_plist(request, username, ipafilename):
    return render(request, 'ios/appinstall.plist', context={'username': username, 'ipafilename': ipafilename})
