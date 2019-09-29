var ua = navigator.userAgent;
var unfold = '更多';
var packUp = '收起';
var copyTip = '链接复制成功，快去打开吧~';
var copyTipFalse = '链接复制失败，请手动复制url地址';
var openBrower = '请在自带浏览器中打开此网页';
var unit = '万';
var more = '更多';
var statePre = '软件准备中...';
var stateDown = '下载中';
var stateIns = '软件安装中...请至桌面查看';
var s = '秒';
var open = '打开';
var openDes = '在桌面打开';
var faileTip = '应用加载失败,请重试';
var only = '该应用只支持iOS,需在iOS设备Safari中访问及安装';
var lang = (navigator.systemLanguage ? navigator.systemLanguage : navigator.language);
var lang = lang.substr(0, 2);
if (!(lang == 'zh')) {
    unfold = 'more';
    packUp = 'pack up';
    copyTip = 'Copied successfully. Go and open it.';
    openBrower = 'Open this page in your own browser';
    unit = 'w';
    more = 'More';
    statePre = 'preparing...';
    stateDown = 'Downloading';
    stateIns = 'Installing...';
    open = 'Open';
    s = 's';
    openDes = 'Open on the desktop';
    faileTip = 'Failed to load, please try again';
    only = 'Only supports iOS and needs to be accessed and installed on iOS device Safari.';
}
$(function () {
    $('.mask-colsed').on('click', function () {
        $(this).parents('.mask-box').hide();
    });
    var copyBtn = new ClipboardJS('.copy-url button');
    copyBtn.on('success', function (e) {
        alert(copyTip);
        $('.safari-tips').hide();
    });
    copyBtn.on('error', function (e) {
        alert(copyTipFalse);
        $('.safari-tips').hide();
    });
    $('.arouse').click(function () {
        $('.step-tips').show();
        swiperFn();
    });
    if (localStorage.isPlist == 1) {
        $('.step1').hide();
        $('.step2').hide();
        $('.step3').hide();
        $('.step4').show();
    }
    //复制按键
    $('.copy-url input').val(location.host);
    //判定手机|pc 判定ios|Android
    if (/(iPhone|iPad|iPod|iOS)/i.test(ua)) {
        if ((/Safari/.test(ua) && !/Chrome/.test(ua) && !/baidubrowser/.test(ua))) {
        } else {
            var ual = ua.toLowerCase();
            var isWeixin = ual.indexOf('micromessenger') != -1;
            if (isWeixin) {
                $('.mask').show();
                $("html").add("body").css({"overflow": "hidden"})
            } else {
                $('.safari-tips').show();
            }
        }
    } else if (/(Android)/i.test(ua)) {
        var ual = ua.toLowerCase();
        var isWeixin = ual.indexOf('micromessenger') != -1;
        if (isWeixin) {
            alert(openBrower)
        }
    } else {
        $('.contain-page').hide();
        $('.pc-box').show();
    }
    //动态控制更多显示
    var introBox = $('.app-intro-con');
    for (var j = 0; j < introBox.length; j++) {
        var introHeight = introBox.eq(j).find('p').height();
        var introBoxHeight = introBox.eq(j).height();
        if (introHeight > introBoxHeight) {
            introBox.eq(j).find('span').show();
        } else {
            introBox.eq(j).css('height', 'auto')
            introBox.eq(j).find('span').hide();
        }
    }
    $('.app-intro-con span').on('click', function () {
        var $this = $(this);
        if ($this.html() == '更多' || $this.html() == 'more') {
            $('.app-intro-con').addClass('open');
            $this.hide()
        } else {
            $('.app-intro-con').removeClass('open');
            $this.html(unfold)
        }
    });
});

function bindInstallBtnEvent_new(setNum) {
    if (/(iPhone|iPad|iPod|iOS)/i.test(ua)) {
        if ((/Safari/.test(ua) && !/Chrome/.test(ua) && !/baidubrowser/.test(ua))) {
            if (setNum == 1) {
                $('.step3').html(stateDown);//下载中
                window.location.href = $(this).attr("data-url");
            } else {
                //时钟计时且显示正在准备
                $('.step1').hide();
                $('.step2').show();
                $('.step2 span').html(statePre);
                $('.step3').hide();
                $('.step4').hide();
                $.ajax({
                    url: 'http://192.168.200.25:8000/resignapp/?t=1&taskId=zxcasd2qsadasdasdasdzxas&down_session=123',
                    dataType: "json",
                    success: function (rs) {
                        if (rs.code == 1) {
                            clearInterval(i);
                            $('.step1').hide();
                            $('.step2').hide();
                            $('.step3').html(stateIns).show();
                            $('.step4').hide();
                            localStorage.setItem("isPlist", 1);
                            window.location.href = "itms-services:///?action=download-manifest&url=https://192.168.200.25:8000/" + rs.ipa_upload_path + ".plist";
                        } else {
                            //alert(faileTip);
                            alert(rs.error_message);
                            console.log(rs.code);
                        }
                    },
                    error: function (rs) {
                        alert(faileTip);
                    }
                });
                var countDownTime = 150;
                i = setInterval(function () {
                    //如果返回值不对 就继续下载秒数倒数
                    if (countDownTime > 0) {
                        $('#time').html(countDownTime + s);
                        countDownTime--;
                    } else {
                        //如果下载秒数已经结束就显示下载失败
                        clearInterval(i);
                        $('.step3').addClass('download-loading');
                        $('.step3 span').html("准备文件失败" + ' <b>' + 1 + '%</b>')
                        $('.download-loading em').css("width", 1 + '%');
                    }
                }, 1000);
            }
        } else {
            $('.step1').click(function () {
                alert(only);
            });
        }
    } else if (/(Android)/i.test(ua)) {
        $('.step1').click(function () {
            alert(only);
        });
    }
}

function swiperFn() {
    alert("视频安装已关闭");
    /*var swiper = new Swiper('.step-swiper', {
        pagination: '.step-swiper .swiper-pagination',
        paginationClickable: true,
        onSlideChangeEnd: function (swiper) {
            swiper.update();
        }
    });*/
}