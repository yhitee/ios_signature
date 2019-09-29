from django.urls import path
from . import views
from django.urls import include
from django.conf import settings
from django.conf.urls import url
from django.views.static import serve

urlpatterns = [
    path('', views.index, name='index'),
    path('lawsregulations/', views.laws, name='laws'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('nologinskip/', views.nologinskip, name='nologinskip'),
    path('register/', views.register, name='register'),
    path('emailconfirm/', views.email_confirm, name='emailconfirm'),
    path('captcha/', include('captcha.urls')),
    path('DistributionManagement/', views.distribution_management, name='distribute_management'),
    path('IpaPackageUpload/', views.ipapackage_upload, name='ipapackageupload'),

    path('udid/receive/', views.udid_receive, name='udid_receive'),
    path('installapp/', views.installapp, name='installapp'),
    path('resignapp/', views.resignapp, name='resignapp'),
    path('ipa_files/<username>/<ipafilename>.plist', views.request_plist, name='request_plist'),
    path('ipa_files/<username>/<ipafilename>', views.ios_request, name='ios_request'),
    url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
