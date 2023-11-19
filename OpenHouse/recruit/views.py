from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect, get_object_or_404
from .forms import RecruitSignupForm, JobfairInfoForm, SeminarInfoCreationForm, StudentForm, ExchangeForm, \
    SeminarInfoTemporaryCreationForm, JobfairInfoTempForm, SurveyForm, OnlineSeminarInfoCreationForm
from .models import RecruitConfigs, SponsorItem, Files, ExchangePrize
from .models import RecruitSignup, SponsorShip, CompanySurvey, RecruitOnlineSeminarInfo, RecruitOnlineJobfairInfo
from .models import SeminarSlot, SlotColor, SeminarOrder, SeminarInfo, RecruitJobfairInfo, SeminarInfoTemporary
from .models import JobfairSlot, JobfairOrder, JobfairInfo, StuAttendance, Student, JobfairInfoTemp
from .models import SeminarParking, JobfairParking
from .models import OnlineSeminarInfo, OnlineSeminarOrder, OnlineSeminarSlot, OnlineJobfairSlot
from company.models import Company
from django.forms import inlineformset_factory
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.http import HttpResponseRedirect, JsonResponse, Http404, HttpResponse
from django import forms
from django.db.models import Count, Q
import datetime
import json
import logging
from ipware.ip import get_client_ip
from company.models import Company
from datetime import timedelta
import recruit.models
from urllib.parse import urlparse, parse_qs
import re

logger = logging.getLogger('recruit')


def parse_YT_video(url):
    """ Parse video ID from the given url """
    query = urlparse(url)
    if query.hostname == 'youtu.be':
        video = query.path[1:]
    elif query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            p = parse_qs(query.query)
            video = p['v'][0]
        elif query.path[:7] == '/embed/':
            video = query.path.split('/')[2]
        elif query.path[:3] == '/v/':
            video = query.path.split('/')[2]
        else:
            video = None
    else:
        video = None
    return video


@login_required(login_url='/company/login/')
def recruit_company_index(request):
    sidebar_ui = {'index': 'active'}
    try:
        configs = RecruitConfigs.objects.all()[0]
    except IndexError:
        return render(request, 'recruit/error.html', {'error_msg' : "活動設定尚未完成，請聯絡行政人員設定"})
    
    plan_file = Files.objects.filter(category="企畫書").first()
    recruit_company_info = recruit.models.RecruitCompanyInfo.objects.all()

    # semantic ui control
    sidebar_ui = {'index': "active"}
    menu_ui = {'recruit': "active"}
    return render(request, 'recruit/company/index.html', locals())


@login_required(login_url='/company/login/')
def recruit_signup(request):
    if request.user.is_staff:
        return redirect("/admin")

    # semantic ui control
    sidebar_ui = {'signup': "active"}
    menu_ui = {'recruit': "active"}
    
    mycompany = Company.objects.filter(cid=request.user.cid).first()
    if mycompany.chinese_funded:
        return render(request, 'recruit/error.html', {'error_msg' : "本企業被政府判定為陸資企業，因此無法使用，請見諒"})

    try:
        configs = RecruitConfigs.objects.all()[0]
    except IndexError:
        return render(request, 'recruit/error.html', {'error_msg' : "活動設定尚未完成，請聯絡行政人員設定"})
    
    if timezone.now() < configs.recruit_signup_start or timezone.now() > configs.recruit_signup_end:
        if request.user.username != "77777777":
            error_msg = "非報名時間。期間為 {} 至 {}".format(
                timezone.localtime(configs.recruit_signup_start).strftime("%Y/%m/%d %H:%M:%S"),
                timezone.localtime(configs.recruit_signup_end).strftime("%Y/%m/%d %H:%M:%S"))
            return render(request, 'recruit/error.html', locals())

    plan_file = recruit.models.Files.objects.filter(category="企畫書").first()

    try:
        signup_info = RecruitSignup.objects.get(cid=request.user.cid)
    except ObjectDoesNotExist:
        signup_info = None

    if request.POST:
        data = request.POST.copy()
        # decide cid in the form
        data['cid'] = request.user.cid
        form = RecruitSignupForm(data=data, instance=signup_info)
        if form.is_valid():
            form.save()
            form.save_m2m()
        else:
            # Debug
            print(form.errors.items())
        return redirect(recruit_signup)
    else:
        form = RecruitSignupForm(instance=signup_info)
    return render(request, 'recruit/company/signup.html', locals())


@login_required(login_url='/company/login/')
def seminar_select_form_gen(request):
    # semantic ui control
    sidebar_ui = {'seminar_select': "active"}
    menu_ui = {'recruit': "active"}
    
    mycompany = Company.objects.filter(cid=request.user.cid).first()
    if mycompany.chinese_funded:
        return render(request, 'recruit/error.html', {'error_msg' : "本企業被政府判定為陸資企業，因此無法使用，請見諒"})
    

    mycid = request.user.cid
    try:
        my_signup = RecruitSignup.objects.get(cid=request.user.cid)
        # check the company have signup seminar
        if my_signup.seminar == "":
            error_msg = "貴公司已報名本次活動，但並未勾選參加實體說明會選項。"
            return render(request, 'recruit/error.html', locals())
    except Exception as e:
        error_msg = "貴公司尚未報名本次活動，請於左方點選「填寫報名資料」"
        return render(request, 'recruit/error.html', locals())

    # check the company have been assigned a slot select order and time
    try:
        seminar_select_time = SeminarOrder.objects.filter(company=mycid).first().time
    except Exception as e:
        seminar_select_time = "選位時間及順序尚未排定，您可以先參考下方實體說明會時間表"

    seminar_session = my_signup.get_seminar_display()

    try:
        configs = RecruitConfigs.objects.all()[0]
    except IndexError:
        return render(request, 'recruit/error.html', {'error_msg' : "活動設定尚未完成，請聯絡行政人員設定"})
    seminar_start_date = configs.seminar_start_date
    seminar_end_date = configs.seminar_end_date
    table_start_date = seminar_start_date
    # find the nearest Monday
    while (table_start_date.weekday() != 0):
        table_start_date -= datetime.timedelta(days=1)
    # make the length to 5 multiples
    dates_in_week = list()
    weeks = seminar_end_date.isocalendar()[1] - seminar_start_date.isocalendar()[1] + 1
    for week in range(0, weeks):
        # separate into 5 in each list (there are 5 days in a week)
        dates_in_week.append([(table_start_date + datetime.timedelta(days=day + week * 7)) \
                              for day in range(0, 4)])

    slot_colors = SlotColor.objects.all()
    session_list = [
        {"name": "noon1", "start_time": configs.session_1_start, "end_time": configs.session_1_end},
        {"name": "noon2", "start_time": configs.session_2_start, "end_time": configs.session_2_end},
        {"name": "noon3", "start_time": configs.session_3_start, "end_time": configs.session_3_end},
        {"name": "evening1", "start_time": configs.session_4_start, "end_time": configs.session_4_end},
        {"name": "evening2", "start_time": configs.session_5_start, "end_time": configs.session_5_end},
        {"name": "evening3", "start_time": configs.session_6_start, "end_time": configs.session_6_end},
    ]
    for session in session_list:
        delta = datetime.datetime.combine(datetime.date.today(), session["end_time"]) - \
                datetime.datetime.combine(datetime.date.today(), session["start_time"])
        if delta > timedelta(minutes=30) and datetime.time(6, 0, 0) < session["start_time"] < datetime.time(21, 0, 0):
            session["valid"] = True
        else:
            session["valid"] = False
    return render(request, 'recruit/company/seminar_select.html', locals())


@login_required(login_url='/company/login/')
def seminar_select_control(request):
    if request.method == "POST":
        post_data = json.loads(request.body.decode())
        action = post_data.get("action")
    else:
        raise Http404("What are u looking for?")

    # action query
    try:
        configs = RecruitConfigs.objects.all()[0]
    except IndexError:
        return render(request, 'recruit/error.html', {'error_msg' : "活動設定尚未完成，請聯絡行政人員設定"})
    if action == "query":
        slots = SeminarSlot.objects.all()
        return_data = {}
        for s in slots:
            # make index first night1_20160707
            index = "{}_{}".format(s.session, s.date.strftime("%Y%m%d"))
            # dict for return data
            return_data[index] = {}

            return_data[index]['place_color'] = None if not s.place else \
                s.place.css_color
            return_data[index]["cid"] = "None" if not s.company else \
                s.company.get_company_name()

            my_seminar_session = RecruitSignup.objects.filter(cid=request.user.cid).first().seminar

            # session wrong (signup noon but choose night)
            # and noon is not full yet
            if (my_seminar_session not in s.session) and \
                    (SeminarSlot.objects.filter(session__contains=my_seminar_session, company=None).exists()):
                # 選別人的時段，而且自己的時段還沒滿
                return_data[index]['valid'] = False
            else:
                return_data[index]['valid'] = True

        my_slot = SeminarSlot.objects.filter(company__cid=request.user.cid).first()
        if my_slot:
            return_data['my_slot'] = True
        else:
            return_data['my_slot'] = False

        try:
            my_select_time = SeminarOrder.objects.filter(company=request.user.cid).first().time
        except AttributeError:
            my_select_time = None

        # Open button for 77777777
        if (not my_select_time or timezone.now() < my_select_time) and request.user.username != '77777777':
            select_ctrl = dict()
            select_ctrl['display'] = True
            select_ctrl['msg'] = '目前非貴公司選位時間，可先參考實體說明會時間表，並待選位時間內選位'
            select_ctrl['select_btn'] = False
        else:
            select_ctrl = dict()
            select_ctrl['display'] = False
            select_ctrl['select_btn'] = True
            today = timezone.now().date()
            if (configs.seminar_btn_start <= today <= configs.seminar_btn_end) or request.user.username == "77777777":
                select_ctrl['btn_display'] = True
            else:
                select_ctrl['btn_display'] = False

        return JsonResponse({"success": True, "data": return_data, "select_ctrl": select_ctrl})

    # action select
    elif action == "select":
        mycid = request.user.cid
        # Open selection for 77777777
        if request.user.username != '77777777':
            my_select_time = SeminarOrder.objects.filter(company=mycid).first().time
            if not my_select_time or timezone.now() < my_select_time:
                return JsonResponse({"success": False, 'msg': '選位失敗，目前非貴公司選位時間'})

        slot_session, slot_date_str = post_data.get("slot").split('_')
        slot_date = datetime.datetime.strptime(slot_date_str, "%Y%m%d")
        try:
            slot = SeminarSlot.objects.get(date=slot_date, session=slot_session)
            my_signup = RecruitSignup.objects.get(cid=request.user.cid)
        except:
            return JsonResponse({"success": False, 'msg': '選位失敗，時段錯誤或貴公司未勾選參加實體說明會'})

        if slot.company != None:
            return JsonResponse({"success": False, 'msg': '選位失敗，該時段已被選定'})

        if slot and my_signup:
            # 不在公司時段，且該時段未滿
            if my_signup.seminar not in slot.session and \
                    SeminarSlot.objects.filter(session=my_signup.seminar, company=None):
                return JsonResponse({"success": False, "msg": "選位失敗，時段錯誤"})

            slot.company = my_signup
            slot.save()
            logger.info('{} select seminar slot {} {}'.format(my_signup.get_company_name(), slot.date, slot.session))
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False, 'msg': '選位失敗，時段錯誤或貴公司未勾選參加實體說明會'})

    # end of action select
    elif action == "cancel":

        my_slot = SeminarSlot.objects.filter(company__cid=request.user.cid).first()
        if my_slot:
            logger.info('{} cancel seminar slot {} {}'.format(
                my_slot.company.get_company_name(), my_slot.date, my_slot.session))
            my_slot.company = None
            my_slot.save()
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False, "msg": "刪除實體說明會選位失敗"})

    else:
        pass
    raise Http404("What are u looking for?")


@login_required(login_url='/company/login/')
def online_seminar_select_form_gen(request):
    # semantic ui control
    sidebar_ui = {'online_seminar_select': "active"}
    menu_ui = {'recruit': "active"}

    mycid = request.user.cid
    
    mycompany = Company.objects.filter(cid=request.user.cid).first()
    if mycompany.chinese_funded:
        return render(request, 'recruit/error.html', {'error_msg' : "本企業被政府判定為陸資企業，因此無法使用，請見諒"})
    
    try:
        my_signup = RecruitSignup.objects.get(cid=request.user.cid)
        # check the company have signup online seminar
        if my_signup.seminar_online == "":
            error_msg = "貴公司已報名本次活動，但並未勾選參加線上說明會選項。"
            return render(request, 'recruit/error.html', locals())
    except Exception as e:
        error_msg = "貴公司尚未報名本次活動，請於左方點選「填寫報名資料」"
        return render(request, 'recruit/error.html', locals())
    
    # check the company have been assigned a slot select order and time
    try:
        seminar_select_time = OnlineSeminarOrder.objects.filter(company=mycid).first().time
    except Exception as e:
        seminar_select_time = "選位時間及順序尚未排定，您可以先參考下方線上說明會時間表"

    seminar_session = my_signup.get_seminar_online_display()

    try:
        configs = RecruitConfigs.objects.all()[0]
    except IndexError:
        return render(request, 'recruit/error.html', {'error_msg' : "活動設定尚未完成，請聯絡行政人員設定"})
    seminar_start_date = configs.seminar_online_start_date
    seminar_end_date = configs.seminar_online_end_date
    table_start_date = seminar_start_date
    # find the nearest Monday
    while (table_start_date.weekday() != 0):
        table_start_date -= datetime.timedelta(days=1)
    # make the length to 5 multiples
    dates_in_week = list()
    weeks = seminar_end_date.isocalendar()[1] - seminar_start_date.isocalendar()[1] + 1
    for week in range(0, weeks):
        # separate into 5 in each list (there are 5 days in a week)
        dates_in_week.append([(table_start_date + datetime.timedelta(days=day + week * 7)) \
                              for day in range(0, 5)])

    session_list = [
        {"name": "noon1", "start_time": configs.session_online_1_start, "end_time": configs.session_online_1_end},
        {"name": "noon2", "start_time": configs.session_online_2_start, "end_time": configs.session_online_2_end},
        {"name": "evening1", "start_time": configs.session_online_3_start, "end_time": configs.session_online_3_end},
        {"name": "evening2", "start_time": configs.session_online_4_start, "end_time": configs.session_online_4_end},
        {"name": "evening3", "start_time": configs.session_online_5_start, "end_time": configs.session_online_5_end},
    ]
    for session in session_list:
        delta = datetime.datetime.combine(datetime.date.today(), session["end_time"]) - \
                datetime.datetime.combine(datetime.date.today(), session["start_time"])
        if delta > timedelta(minutes=30) and datetime.time(6, 0, 0) < session["start_time"] < datetime.time(21, 0, 0):
            session["valid"] = True
        else:
            session["valid"] = False
    return render(request, 'recruit/company/online_seminar_select.html', locals())


@login_required(login_url='/company/login/')
def online_seminar_select_control(request):
    if request.method == "POST":
        post_data = json.loads(request.body.decode())
        action = post_data.get("action")
    else:
        raise Http404("What are u looking for?")

    # action query
    try:
        configs = RecruitConfigs.objects.all()[0]
    except IndexError:
        return render(request, 'recruit/error.html', {'error_msg' : "活動設定尚未完成，請聯絡行政人員設定"})
    if action == "query":
        slots = OnlineSeminarSlot.objects.all()
        return_data = {}
        for s in slots:
            # make index first night1_20160707
            index = "{}_{}".format(s.session, s.date.strftime("%Y%m%d"))
            # dict for return data
            return_data[index] = {}

            return_data[index]["cid"] = "None" if not s.company else \
                s.company.get_company_name()

            my_seminar_session = RecruitSignup.objects.filter(cid=request.user.cid).first().seminar_online

            # session wrong (signup noon but choose night)
            # and noon is not full yet
            if OnlineSeminarSlot.objects.filter(session__contains=my_seminar_session, company=None).exists():
                # 選別人的時段，而且自己的時段還沒滿
                return_data[index]['valid'] = False
            else:
                return_data[index]['valid'] = True

        my_slot = OnlineSeminarSlot.objects.filter(company__cid=request.user.cid).first()
        if my_slot:
            return_data['my_slot'] = True
        else:
            return_data['my_slot'] = False

        try:
            my_select_time = OnlineSeminarOrder.objects.filter(company=request.user.cid).first().time
        except AttributeError:
            my_select_time = None

        # Open button for 77777777
        if (not my_select_time or timezone.now() < my_select_time) and request.user.username != '77777777':
            select_ctrl = dict()
            select_ctrl['display'] = True
            select_ctrl['msg'] = '目前非貴公司選位時間，可先參考說明會時間表，並待選位時間內選位'
            select_ctrl['select_btn'] = False
        else:
            select_ctrl = dict()
            select_ctrl['display'] = False
            select_ctrl['select_btn'] = True
            today = timezone.now().date()
            if (
                    configs.seminar_online_btn_start <= today <= configs.seminar_online_btn_end) or request.user.username == "77777777":
                select_ctrl['btn_display'] = True
            else:
                select_ctrl['btn_display'] = False

        return JsonResponse({"success": True, "data": return_data, "select_ctrl": select_ctrl})

    # action select
    elif action == "select":
        mycid = request.user.cid
        # Open selection for 77777777
        if request.user.username != '77777777':
            my_select_time = OnlineSeminarOrder.objects.filter(company=mycid).first().time
            if not my_select_time or timezone.now() < my_select_time:
                return JsonResponse({"success": False, 'msg': '選位失敗，目前非貴公司選位時間'})

        slot_session, slot_date_str = post_data.get("slot").split('_')
        slot_date = datetime.datetime.strptime(slot_date_str, "%Y%m%d")
        try:
            slot = OnlineSeminarSlot.objects.get(date=slot_date, session=slot_session)
            my_signup = RecruitSignup.objects.get(cid=request.user.cid)
        except:
            return JsonResponse({"success": False, 'msg': '選位失敗，時段錯誤或貴公司未勾選參加線上說明會'})

        if slot.company != None:
            return JsonResponse({"success": False, 'msg': '選位失敗，該時段已被選定'})

        if slot and my_signup:
            # 不在公司時段，且該時段未滿
            if my_signup.seminar_online not in slot.session and \
                    OnlineSeminarSlot.objects.filter(session=my_signup.seminar_online, company=None):
                return JsonResponse({"success": False, "msg": "選位失敗，時段錯誤"})

            slot.company = my_signup
            slot.save()
            logger.info('{} select seminar slot {} {}'.format(my_signup.get_company_name(), slot.date, slot.session))
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False, 'msg': '選位失敗，時段錯誤或貴公司未勾選參加線上說明會'})

    # end of action select
    elif action == "cancel":
        my_slot = OnlineSeminarSlot.objects.filter(company__cid=request.user.cid).first()
        if my_slot:
            logger.info('{} cancel seminar slot {} {}'.format(
                my_slot.company.get_company_name(), my_slot.date, my_slot.session))
            my_slot.company = None
            my_slot.save()
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False, "msg": "刪除線上說明會選位失敗"})

    else:
        pass
    raise Http404("What are u looking for?")


@login_required(login_url='/company/login/')
def jobfair_info(request):
    # semantic ui
    sidebar_ui = {'jobfair_info': "active"}
    menu_ui = {'recruit': "active"}

    mycompany = Company.objects.filter(cid=request.user.cid).first()
    if mycompany.chinese_funded:
        return render(request, 'recruit/error.html', {'error_msg' : "本企業被政府判定為陸資企業，因此無法使用，請見諒"})    

    try:
        company = RecruitSignup.objects.get(cid=request.user.cid)
    except Exception as e:
        error_msg = "貴公司尚未報名本次活動，請於上方點選「填寫報名資料」"
        return render(request, 'recruit/error.html', locals())

    try:
        jobfair_info_object = JobfairInfo.objects.get(company=company)
    except ObjectDoesNotExist:
        jobfair_info_object = None
        
    try:
        deadline = RecruitConfigs.objects.values('jobfair_info_deadline')[0]['jobfair_info_deadline']
        food_type = RecruitConfigs.objects.values('jobfair_food')[0]['jobfair_food']
    except IndexError:
        return render(request, 'recruit/error.html', {'error_msg' : "活動設定尚未完成，請聯絡行政人員設定"})
    
    reach_deadline =timezone.now() > deadline
    parking_form_set = inlineformset_factory(JobfairInfo, JobfairParking, max_num=1, extra=1,
                                             fields=('id', 'license_plate_number', 'info'),
                                             widgets={'license_plate_number': forms.TextInput(
                                                 attrs={'placeholder': '需要-連字號，例AA-1234、4321-BB'})})

    if request.POST:
        if not reach_deadline:
            data = request.POST.copy()
            form = JobfairInfoForm(data=data, instance=jobfair_info_object)
            formset = parking_form_set(data=data, instance=jobfair_info_object)
            if form.is_valid() and formset.is_valid():
                new_info = form.save(commit=False)
                company = RecruitSignup.objects.get(cid=request.user.cid)
                new_info.company = company
                new_info.save()
                formset.save()
                # return render(request, 'recruit/company/success.html', locals())
                return redirect(jobfair_info)
            else:
                print(form.errors)

        else:
            error_msg = "實體就博會資訊填寫時間已截止!若有更改需求，請來信或來電。"
            return render(request, 'recruit/error.html', locals())

    else:
        form = JobfairInfoForm(instance=jobfair_info_object)
        formset = parking_form_set(instance=jobfair_info_object)

    return render(request, 'recruit/company/jobfair_info.html', locals())


@login_required(login_url='/company/login/')
def jobfair_info_temp(request):
    try:
        company = RecruitSignup.objects.get(cid=request.user.cid)
    except Exception as e:
        error_msg = "貴公司尚未報名本次活動，請於上方點選「填寫報名資料」"
        return render(request, 'recruit/error.html', locals())

    try:
        jobfair_info = JobfairInfoTemp.objects.get(company=company)
    except ObjectDoesNotExist:
        jobfair_info = None

    if request.POST:
        data = request.POST.copy()
        form = JobfairInfoTempForm(data=data, instance=jobfair_info)
        if form.is_valid():
            new_info = form.save(commit=False)
            company = RecruitSignup.objects.get(cid=request.user.cid)
            new_info.company = company
            new_info.save()
            return redirect('jobfair_online', company_cid=request.user.cid)
        else:
            print(form.errors)
    else:
        form = JobfairInfoTempForm(instance=jobfair_info)

    # semantic ui
    sidebar_ui = {'jobfair_info': "active"}
    menu_ui = {'recruit': "active"}
    return render(request, 'recruit/company/jobfair_info_temp.html', locals())


@login_required(login_url='/company/login/')
def seminar_info(request):
    # semantic ui
    sidebar_ui = {'seminar_info': "active"}
    menu_ui = {'recruit': "active"}
    
    mycompany = Company.objects.filter(cid=request.user.cid).first()
    if mycompany.chinese_funded:
        return render(request, 'recruit/error.html', {'error_msg' : "本企業被政府判定為陸資企業，因此無法使用，請見諒"})

    try:
        company = RecruitSignup.objects.get(cid=request.user.cid)
    except Exception as e:
        error_msg = "貴公司尚未報名本次活動，請於左方點選「填寫報名資料」"
        return render(request, 'recruit/error.html', locals())

    try:
        seminar_info_object = SeminarInfo.objects.get(company=company)
    except ObjectDoesNotExist:
        seminar_info_object = None

    parking_form_set = inlineformset_factory(SeminarInfo, SeminarParking, max_num=2, extra=2,
                                             fields=('id', 'license_plate_number', 'info'),
                                             widgets={'license_plate_number': forms.TextInput(
                                                 attrs={'placeholder': '例AA-1234、4321-BB'})})

    if request.POST:
        data = request.POST.copy()
        data['company'] = company.cid
        form = SeminarInfoCreationForm(data=data, instance=seminar_info_object)
        formset = parking_form_set(data=data, instance=seminar_info_object)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            # return render(request, 'recruit/company/success.html', locals())
            return redirect(seminar_info)
        else:
            print(form.errors)
    else:
        form = SeminarInfoCreationForm(instance=seminar_info_object)
        formset = parking_form_set(instance=seminar_info_object)

    return render(request, 'recruit/company/seminar_info_form.html', locals())


@login_required(login_url='/company/login/')
def online_seminar_info(request):
    # semantic ui
    sidebar_ui = {'online_seminar_info': "active"}
    menu_ui = {'recruit': "active"}

    mycompany = Company.objects.filter(cid=request.user.cid).first()
    if mycompany.chinese_funded:
        return render(request, 'recruit/error.html', {'error_msg' : "本企業被政府判定為陸資企業，因此無法使用，請見諒"})

    try:
        company = RecruitSignup.objects.get(cid=request.user.cid)
    except Exception as e:
        error_msg = "貴公司尚未報名本次活動，請於左方點選「填寫報名資料」"
        return render(request, 'recruit/error.html', locals())

    try:
        online_seminar_info_object = OnlineSeminarInfo.objects.get(company=company)
    except ObjectDoesNotExist:
        online_seminar_info_object = None

    if request.POST:
        data = request.POST.copy()
        data['company'] = company.cid
        form = OnlineSeminarInfoCreationForm(data=data, instance=online_seminar_info_object)
        if form.is_valid():
            form.save()
            # return render(request, 'recruit/company/success.html', locals())
            return redirect(online_seminar_info)
        else:
            print(form.errors)
    else:
        form = SeminarInfoCreationForm(instance=online_seminar_info_object)

    return render(request, 'recruit/company/online_seminar_info_form.html', locals())


@login_required(login_url='/company/login/')
def seminar_info_temporary(request):
    try:
        company = RecruitSignup.objects.get(cid=request.user.cid)
    except Exception as e:
        error_msg = "貴公司尚未報名本次活動，請於左方點選「填寫報名資料」"
        return render(request, 'recruit/error.html', locals())

    try:
        seminar_info = SeminarInfoTemporary.objects.get(company=company)
    except ObjectDoesNotExist:
        seminar_info = None

    if request.POST:
        data = request.POST.copy()
        data['company'] = company.cid
        form = SeminarInfoTemporaryCreationForm(data=data, instance=seminar_info)
        if form.is_valid():
            form.save()
            return render(request, 'recruit/company/success.html', locals())
        else:
            print(form.errors)
    else:
        form = SeminarInfoTemporaryCreationForm(instance=seminar_info)

    # semantic ui
    sidebar_ui = {'seminar_info': "active"}
    menu_ui = {'recruit': "active"}
    return render(request, 'recruit/company/seminar_info_form_temporary.html', locals())


@login_required(login_url='/company/login/')
def jobfair_select_form_gen(request):
    # semanti ui control
    sidebar_ui = {'jobfair_select': "active"}
    menu_ui = {'recruit': "active"}

    mycompany = Company.objects.filter(cid=request.user.cid).first()
    if mycompany.chinese_funded:
        return render(request, 'recruit/error.html', {'error_msg' : "本企業被政府判定為陸資企業，因此無法使用，請見諒"})
    
    mycid = request.user.cid
    # check the company have signup recruit
    try:
        my_signup = RecruitSignup.objects.get(cid=request.user.cid)
        # check the company have signup seminar
        if my_signup.jobfair == 0:
            error_msg = "貴公司已報名本次校徵活動，但並未填寫實體就博會攤位。"
            return render(request, 'recruit/error.html', locals())
    except Exception as e:
        error_msg = "貴公司尚未報名本次活動，請於左方點選「填寫報名資料」"
        return render(request, 'recruit/error.html', locals())
    # check the company have been assigned a slot select order and time
    try:
        jobfair_select_time = JobfairOrder.objects.filter(company=mycid).first().time
    except Exception as e:
        jobfair_select_time = "選位時間及順序尚未排定，您可以先參考攤位圖"

    place_maps = Files.objects.filter(category='就博會攤位圖')

    return render(request, 'recruit/company/jobfair_select.html', locals())


@login_required(login_url='/company/login/')
def jobfair_select_control(request):
    if request.method == "POST":
        mycid = request.user.cid
        post_data = json.loads(request.body.decode())
        action = post_data.get("action")
    else:
        raise Http404("What are u looking for?")

    slot_group = [
        {"slot_type": "半導體", "display": "半導體", "category": ["半導體"], "slot_list": list(),
         "is_mygroup": False, "color": "pink"},

        {"slot_type": "資訊軟體", "display": "資訊軟體", "category": ["資訊軟體"], "slot_list": list(),
         "is_mygroup": False, "color": "blue"},

        {"slot_type": "消費電子", "display": "消費電子", "category": ["消費電子"], "slot_list": list(),
         "is_mygroup": False, "color": "yellow"},

        {"slot_type": "網路通訊", "display": "網路通訊", "category": ["網路通訊"], "slot_list": list(),
         "is_mygroup": False, "color": "teal"},

        {"slot_type": "光電光學", "display": "光電光學", "category": ["光電光學"], "slot_list": list(),
         "is_mygroup": False, "color": "grey"},

        {"slot_type": "綜合", "display": "綜合(綜合、集團、機構、人力銀行)"
            , "category": ["綜合", "集團", "機構", "人力銀行"],
         "slot_list": list(), "is_mygroup": False, "color": "purple"},

        {"slot_type": "新創", "display": "新創", "category": ["新創"], "slot_list": list(),
         "is_mygroup": False, "color": "brown"},
        {"slot_type": "主辦保留", "display": "主辦保留", "category": ["主辦保留"], "slot_list": list(),
         "is_mygroup": False, "color": "olive"},

        {"slot_type": "生科醫療", "display": "生科醫療", "category": ["生科醫療"], "slot_list": list(),
         "is_mygroup": False, "color": "red"},
        
        {"slot_type": "公家單位", "display": "公家單位", "category": ["公家單位"], "slot_list": list(),
         "is_mygroup": False, "color": "green"},
        {"slot_type": "通用", "display": "通用", "category": ["通用"], "slot_list": list(),
         "is_mygroup": True, "color": "purple"},
        
    ]
    try:
        my_signup = RecruitSignup.objects.get(cid=request.user.cid)
    except:
        ret = dict()
        ret['success'] = False
        ret['msg'] = "選位失敗，攤位錯誤或貴公司未勾選參加就博會"
        return JsonResponse(ret)
    # 把自己的group enable並放到最前面顯示
    try:
        company_category = my_signup.get_company().category
        my_slot_group = next(group for group in slot_group if company_category in group['category'])
        slot_group.remove(my_slot_group)
        my_slot_group['is_mygroup'] = True
        slot_group.insert(0, my_slot_group)
    except StopIteration:
        pass

    
    if action == "query":
        companyname = dict(Company.objects.values_list('cid', 'shortname'))
        for group in slot_group:
            slot_list = JobfairSlot.objects.filter(category__in=group["category"])
            for slot in slot_list:
                slot_info = dict()
                slot_info["serial_no"] = slot.serial_no
                slot_info["company"] = None if not slot.company_id else \
                    companyname[slot.company_id]
                group['slot_list'].append(slot_info)

        # remove those slot list is equal to 0
        for group in slot_group.copy():
            if  not group['slot_list']:
                slot_group.remove(group)
                
        my_slot_list = [slot.serial_no for slot in JobfairSlot.objects.filter(company__cid=request.user.cid)]

        try:
            my_select_time = JobfairOrder.objects.filter(company=request.user.cid).first().time
        except AttributeError:
            my_select_time = None

        # Open button for 77777777
        if (not my_select_time or timezone.now() < my_select_time) and request.user.username != '77777777':
            select_ctrl = dict()
            select_ctrl['display'] = True
            select_ctrl['msg'] = '目前非貴公司選位時間，可先參考攤位圖，並待選位時間內選位'
            select_ctrl['select_enable'] = False
            select_ctrl['btn_display'] = False
        else:
            select_ctrl = dict()
            select_ctrl['display'] = False
            select_ctrl['select_enable'] = True
            today = timezone.now().date()
            try:
                configs = RecruitConfigs.objects.values('jobfair_btn_start', 'jobfair_btn_end').all()[0]
            except IndexError:
                return render(request, 'recruit/error.html', {'error_msg' : "活動設定尚未完成，請聯絡行政人員設定"})
            if (configs['jobfair_btn_start'] <= today <= configs['jobfair_btn_end']) or request.user.username == '77777777':
                select_ctrl['btn_display'] = True
            else:
                select_ctrl['btn_display'] = False

        return JsonResponse({"success": True,
                             "slot_group": slot_group,
                             "my_slot_list": my_slot_list,
                             "select_ctrl": select_ctrl})

    elif action == "select":
        try:
            slot = JobfairSlot.objects.get(serial_no=post_data.get('slot'))
        except:
            ret = dict()
            ret['success'] = False
            ret['msg'] = "選位失敗，攤位錯誤"
            return JsonResponse(ret)
        if slot.company != None:
            return JsonResponse({"success": False, 'msg': '選位失敗，該攤位已被選定'})

        # Open selection for 77777777
        if request.user.username != '77777777':
            my_select_time = JobfairOrder.objects.filter(company=request.user.cid).first().time
            if timezone.now() < my_select_time:
                return JsonResponse({"success": False, 'msg': '選位失敗，目前非貴公司選位時間'})

        my_slot_list = JobfairSlot.objects.filter(company__cid=request.user.cid)
        if my_slot_list.count() >= my_signup.jobfair:
            return JsonResponse({"success": False, 'msg': '選位失敗，貴公司攤位數已達上限'})

        try:
            my_slot_group = next(group for group in slot_group if company_category in group['category'])
            if slot.category not in my_slot_group['category'] and slot.category != "通用":
                return JsonResponse({"success": False, 'msg': '選位失敗，該攤位非貴公司類別'})
        except StopIteration:
            pass
            
        if slot.category == '主辦保留':
            return JsonResponse({"success": False, 'msg': '選位失敗，該攤位非貴公司類別'})

        slot.company = my_signup
        slot.save()

        ip = get_client_ip(request)
        if ip is None:
            ip = "Unknown IP"
        logger.info('{} select jobfair slot {} from {}'.format(my_signup.get_company_name(), slot.serial_no, ip))
        return JsonResponse({"success": True})

    elif action == "cancel":
        cancel_slot_no = post_data.get('slot')
        cancel_slot = JobfairSlot.objects.filter(
            company__cid=request.user.cid,
            serial_no=cancel_slot_no
        ).first()
        if cancel_slot:
            cancel_slot.company = None
            cancel_slot.save()

            ip = get_client_ip(request)
            if ip is None:
                ip = "Unknown IP"
            logger.info(
                '{} canceled jobfair slot {} from {}'.format(my_signup.get_company_name(), cancel_slot.serial_no, ip))

            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False, "msg": "刪除就博會攤位失敗"})
    else:
        raise Http404("Invalid")


def Add_SponsorShip(sponsor_items, post_data, sponsor):
    """
    Clear old sponsorship and create a new one
    """
    success_item = list()
    fail_item = list()
    old_sponsorships = SponsorShip.objects.filter(company=sponsor)
    for item in old_sponsorships:
        item.delete()
    for item in sponsor_items:
        obj = None
        if item.name in post_data:
            if SponsorShip.objects.filter(sponsor_item=item).count() < item.number_limit:
                obj = SponsorShip.objects.create(company=sponsor, sponsor_item=item)
            if obj:
                success_item.append(item.name)
            else:
                fail_item.append(item.name)

    if success_item:
        success_msg = "贊助成功物品: {}".format(", ".join(success_item))
    else:
        success_msg = None

    if fail_item:
        fail_msg = "贊助失敗物品: {}".format(", ".join(fail_item))
    else:
        fail_msg = None
    return success_msg, fail_msg


@login_required(login_url='/company/login/')
def Sponsor(request):
    # semantic ui
    sidebar_ui = {'sponsor': "active"}
    menu_ui = {'recruit': "active"}

    mycompany = Company.objects.filter(cid=request.user.cid).first()
    if mycompany.chinese_funded:
        return render(request, 'recruit/error.html', {'error_msg' : "本企業被政府判定為陸資企業，因此無法使用，請見諒"})
    
    try:
        configs = RecruitConfigs.objects.all()[0]
    except IndexError:
        return render(request, 'recruit/error.html', {'error_msg' : "活動設定尚未完成，請聯絡行政人員設定"})
    if timezone.now() < configs.recruit_signup_start or timezone.now() > configs.recruit_signup_end:
        if request.user.username != "77777777":
            error_msg = "非贊助時間。期間為 {} 至 {}".format(
                timezone.localtime(configs.recruit_signup_start).strftime("%Y/%m/%d %H:%M:%S"),
                timezone.localtime(configs.recruit_signup_end).strftime("%Y/%m/%d %H:%M:%S"))
            return render(request, 'recruit/error.html', locals())
    # get form post
    try:
        sponsor = RecruitSignup.objects.get(cid=request.user.cid)
    except Exception as e:
        error_msg = "貴公司尚未報名本次「春季徵才」活動，請於左方點選「填寫報名資料」"
        return render(request, 'recruit/error.html', locals())

    if request.POST:
        sponsor_items = SponsorItem.objects.all()
        succ_msg, fail_msg = Add_SponsorShip(sponsor_items, request.POST, sponsor)
        msg = {
            "display": True,
            "content": "儲存成功!",
            "succ_msg": succ_msg,
            "fail_msg": fail_msg
        }

    # 活動專刊的部份是變動不大，且版面特殊，採客製寫法
    monograph_main = SponsorItem.objects.filter(name="活動專刊").first()
    monograph_items = SponsorItem.objects.filter(name__contains="活動專刊").exclude(name="活動專刊") \
        .annotate(num_sponsor=Count('sponsors'))
    other_items = SponsorItem.objects.all().exclude(name__contains="活動專刊") \
        .annotate(num_sponsor=Count('sponsors'))
    sponsorship = SponsorShip.objects.filter(company=sponsor)
    my_sponsor_items = [s.sponsor_item for s in sponsorship]
    return render(request, 'recruit/company/sponsor.html', locals())


@staff_member_required
def SponsorAdmin(request):
    site_header = "OpenHouse 管理後台"
    site_title = "OpenHouse"
    sponsor_items = SponsorItem.objects.all() \
        .annotate(num_sponsor=Count('sponsorship'))
    companies = RecruitSignup.objects.all()
    sponsorships_list = list()
    for c in companies:
        shortname = c.get_company_name()
        sponsorships = SponsorShip.objects.filter(company=c)
        counts = [SponsorShip.objects.filter(company=c, sponsor_item=item).count() for item in sponsor_items]
        amount = 0
        for s in sponsorships:
            amount += s.sponsor_item.price
        sponsorships_list.append({
            "cid": c.cid,
            "counts": counts,
            "amount": amount,
            "shortname": shortname,
            "id": c.id,
            "change_url": reverse('admin:recruit_recruitsignup_change',
                                               args=(c.id,))
        })

    return render(request, 'recruit/admin/sponsor_admin.html', locals())


@login_required(login_url='/company/login/')
def company_survey(request):
    # semantic ui
    sidebar_ui = {'survey': "active"}
    menu_ui = {'recruit': "active"}
    
    mycompany = Company.objects.filter(cid=request.user.cid).first()
    if mycompany.chinese_funded:
        return render(request, 'recruit/error.html', {'error_msg' : "本企業被政府判定為陸資企業，因此無法使用，請見諒"})
    
    try:
        configs = RecruitConfigs.objects.all()[0]
    except IndexError:
        return render(request, 'recruit/error.html', {'error_msg' : "活動設定尚未完成，請聯絡行政人員設定"})

    if timezone.now() > configs.survey_end or timezone.now() < configs.survey_start:
        if request.user.username != "77777777":
            error_msg = "問卷填答已結束。期間為 {} 至 {}".format(
                timezone.localtime(configs.survey_start).strftime("%Y/%m/%d %H:%M:%S"),
                timezone.localtime(configs.survey_end).strftime("%Y/%m/%d %H:%M:%S"))
            return render(request, 'recruit/error.html', locals())

    try:
        my_survey = CompanySurvey.objects.get(cid=request.user.cid)
    except ObjectDoesNotExist:
        my_survey = None
    if request.POST:
        data = request.POST.copy()
        # decide cid in the form
        data['cid'] = request.user.cid
        form = SurveyForm(data=data, instance=my_survey)
        if form.is_valid():
            form.save()
            return redirect(company_survey)
        else:
            (msg_display, msg_type, msg_content) = (True, "error", "儲存失敗，有未完成欄位")
            print(form.errors)
    else:
        form = SurveyForm(instance=my_survey)

    return render(request, 'recruit/company/survey_form.html', locals())


@staff_member_required
def sponsorship_admin(request):
    items = SponsorItem.objects.all()
    sponsorships = SponsorShip.objects.all()
    companys = SponsorShip.objects.all()
    return render(request, 'recruit/admin/sponsorship.html', locals())


@staff_member_required
def RegisterCard(request):
    if request.method == "POST":
        data = request.POST.copy()
        instance = recruit.models.Student.objects.filter(card_num=data['card_num']).first()
        form = StudentForm(data, instance=instance)
        if form.is_valid():
            form.save()
            ui_message = {"type": "green", "msg": "註冊成功"}
        else:
            ui_message = {"type": "error", "msg": "註冊失敗"}
    else:
        form = StudentForm()
    return render(request, 'recruit/admin/reg_card.html', locals())


@staff_member_required
def collect_points(request):
    """
    Select today session and place current session in first place
    """
    students = Student.objects.all()
    today = datetime.datetime.now().date()
    try:
        config = RecruitConfigs.objects.all()[0]
    except IndexError:
        return render(request, 'recruit/error.html', {'error_msg' : "活動設定尚未完成，請聯絡行政人員設定"})

    # Find the suitable session
    now = datetime.datetime.now()
    if (now - timedelta(minutes=20)).time() < config.session_1_end < (now + timedelta(minutes=20)).time():
        current_session = 'other1'
    elif (now - timedelta(minutes=20)).time() < config.session_2_end < (now + timedelta(minutes=20)).time():
        current_session = 'noon2'
    elif (now - timedelta(minutes=20)).time() < config.session_3_end < (now + timedelta(minutes=20)).time():
        current_session = 'other2'
    elif (now - timedelta(minutes=20)).time() < config.session_4_end < (now + timedelta(minutes=20)).time():
        current_session = 'other3'
    elif (now - timedelta(minutes=20)).time() < config.session_5_end < (now + timedelta(minutes=20)).time():
        current_session = 'other4'
    elif (now - timedelta(minutes=20)).time() < config.session_6_end < (now + timedelta(minutes=20)).time():
        current_session = 'other5'
    else:
        current_session = ''

    current_seminar = SeminarSlot.objects.filter(date=today, session=current_session).first()

    seminars = SeminarSlot.objects.filter(date=today)
    if (request.POST):
        card_num = request.POST['card_num']
        seminar_id = request.POST['seminar_id']
        student_obj, create = Student.objects.get_or_create(card_num=card_num)
        seminar_obj = SeminarSlot.objects.get(id=seminar_id)
        StuAttendance.objects.get_or_create(student=student_obj, seminar=seminar_obj)
    seminar_list = list(seminars)
    if (current_seminar):
        seminar_list.remove(current_seminar)
        seminar_list.insert(0, current_seminar)
    return render(request, 'recruit/admin/collect_points.html', locals())


@staff_member_required
def exchange_prize(request):
    if (request.GET):
        if 'card_num' in request.GET:
            student = Student.objects.filter(card_num=request.GET['card_num']).first()
            form = StudentForm(instance=student)
            exchange_form = ExchangeForm()

    if (request.POST):
        student = Student.objects.filter(card_num=request.POST['card_num']).first()
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
        data = request.POST.copy()
        data['student'] = student
        exchange_form = ExchangeForm(data)
        if exchange_form.is_valid():
            exchange_form.save()
    return render(request, 'recruit/admin/exchange_prize.html', locals())


@login_required(login_url='/company/login/')
def Status(request):
    if request.user.is_staff:
        return redirect("/admin")
    mycid = request.user.cid
    
    mycompany = Company.objects.filter(cid=request.user.cid).first()
    if mycompany.chinese_funded:
        return render(request, 'recruit/error.html', {'error_msg' : "本企業被政府判定為陸資企業，因此無法使用，請見諒"})
    # get the dates from the configs
    try:
        configs = recruit.models.RecruitConfigs.objects.all()[0]
    except IndexError:
        return render(request, 'recruit/error.html', {'error_msg' : "活動設定尚未完成，請聯絡行政人員設定"})
    signup_data = recruit.models.RecruitSignup.objects.filter(cid=mycid).first()

    pay_info_file = Files.objects.filter(category="繳費資訊").first()

    slot_info = {
        "seminar_select_time": "選位時間正在排定中",
        "jobfair_select_time": "選位時間正在排定中",
        "seminar_slot": "-",
        "jobfair_slot": "-",
    }
    seminar_session_display = {
        "noon1": "{}~{}".format(configs.session_1_start, configs.session_1_end),
        "noon2": "{}~{}".format(configs.session_2_start, configs.session_2_end),
        "noon3": "{}~{}".format(configs.session_3_start, configs.session_3_end),
        "evening1": "{}~{}".format(configs.session_4_start, configs.session_4_end),
        "evening2": "{}~{}".format(configs.session_5_start, configs.session_5_end),
        "evening3": "{}~{}".format(configs.session_6_start, configs.session_6_end),
    }

    # 問卷狀況
    try:
        recruit.models.CompanySurvey.objects.get(cid=request.user.cid)
        fill_survey = True
    except:
        fill_survey = False

    # 選位時間和數量狀態
    seminar_select_time = recruit.models.SeminarOrder.objects.filter(company=mycid).first()
    jobfair_select_time = recruit.models.JobfairOrder.objects.filter(company=mycid).first()
    if seminar_select_time:
        slot_info['seminar_select_time'] = seminar_select_time.time
    if jobfair_select_time:
        slot_info['jobfair_select_time'] = jobfair_select_time.time

    seminar_slot = recruit.models.SeminarSlot.objects.filter(company=mycid).first()
    jobfair_slot = recruit.models.JobfairSlot.objects.filter(company=mycid)
    if not seminar_slot:
        slot_info['seminar_slot'] = "請依時段於左方選單選位"
    else:
        slot_info['seminar_slot'] = "{} {}".format(seminar_slot.date,
                                                   seminar_session_display[seminar_slot.session])
    if not jobfair_slot:
        slot_info['jobfair_slot'] = "請依時段於左方選單選位"
    else:
        slot_info['jobfair_slot'] = [int(s.serial_no) for s in jobfair_slot]

    # Fee display
    fee = 0
    discount = 0
    discount_text = ""
    mycompany = Company.objects.get(cid=mycid)
    
    try:
        # session fee calculation
        if signup_data.seminar == 'attend_short':
            fee += configs.session_fee_short
        elif signup_data.seminar == 'attend_long':
            fee += configs.session_fee_long

        # ece fee calculation
        num_of_ece = len(signup_data.seminar_ece.all())
        if mycompany.ece_member:
            discount_num_of_ece = 0
            for ece_seminar in signup_data.seminar_ece.all():
                if ece_seminar.ece_member_discount:
                    discount_num_of_ece += 1
            discount += configs.session_ece_fee * discount_num_of_ece
        if num_of_ece:
            fee += configs.session_ece_fee * num_of_ece

        # jobfair fee calculation
        if signup_data.jobfair:
            if mycompany.ece_member or mycompany.gloria_normal:
                discount_text = "貴公司為電機研究所聯盟或Gloria會員，可享有第一攤免費優惠"
                discount += min(signup_data.jobfair, 1) * configs.jobfair_booth_fee
            elif mycompany.gloria_startup:
                discount_text = "貴公司為Gloria新創會員，可享有第一攤免費優惠"
                discount += min(signup_data.jobfair, 2) * configs.jobfair_booth_fee
            elif signup_data.first_participation:
                discount_text = "貴公司為首次參加本活動，可享有第一攤免費優惠"
                discount += min(signup_data.jobfair, 1) * configs.jobfair_booth_fee
            elif signup_data.zone and signup_data.zone != '一般企業':
                discount_text = "貴公司為{}專區，可享有第一攤免費優惠".format(signup_data.zone)
                discount += min(signup_data.jobfair, 1) * configs.jobfair_booth_fee
            fee += signup_data.jobfair * configs.jobfair_booth_fee

        if mycompany.category == '公家單位':
            discount_text = "貴公司為公家單位，可享有免費優惠"
            discount = fee
    except AttributeError:
        # Company has not sign up
        pass

    # Sponsor fee display
    sponsor_amount = 0
    sponsorships = recruit.models.SponsorShip.objects.filter(company=request.user.cid)
    for s in sponsorships:
        if '攤位升級' not in s.sponsor_item.name:
            sponsor_amount += s.sponsor_item.price

    # All the fee of Sponsor and Display

    all_fee = fee + sponsor_amount - discount

    # Seminar and Jobfair info status
    if signup_data:
        company = RecruitSignup.objects.get(cid=request.user.cid)
        try:
            seminar_info = recruit.models.SeminarInfo.objects.get(company=request.user.cid)
        except ObjectDoesNotExist:
            seminar_info = None
        try:
            jobfair_info = JobfairInfo.objects.get(company=company)
        except ObjectDoesNotExist:
            jobfair_info = None
    else:
        seminar_info = None
        jobfair_info = None
        
    # check recepit information whether submit or not
    
    target_company = Company.objects.get(cid=mycid)
    
    if target_company.receipt_title == ""  or target_company.receipt_postal_code == ""  \
        or target_company.receipt_postal_address == ""  or target_company.receipt_contact_name == ""  \
        or target_company.receipt_contact_phone == "" :
        fill_receipt = False
    else:
        fill_receipt = True
    

    # control semantic ui class
    step_ui = ["", "", ""]  # for step ui in template
    nav_recruit = "active"
    sidebar_ui = {'status': "active"}
    menu_ui = {'recruit': "active"}

    step_ui[0] = "completed" if signup_data else "active"

    return render(request, 'recruit/company/status.html', locals())


# ======================== Recruit public view =======================


def public(request):
    # semantic ui control
    sidebar_ui = {'index': "active"}

    recruit_info = recruit.models.RecruitInfo.objects.all()
    return render(request, 'recruit/public/public.html', locals())


def list_jobs(request):
    # semantic ui control
    sidebar_ui = {'list_jobs': "active"}

    categories = [category[0] for category in Company.CATEGORYS]
    companies = []
    category_filtered = request.GET.get('categories') if request.GET.get('categories') else None
    if category_filtered and category_filtered != 'all':
        if category_filtered not in categories:
            raise Http404("What are u looking for?")
        for company in RecruitSignup.objects.all():
            try:
                target_company = Company.objects.get(cid=company.cid, category=category_filtered)
                companies.append({
                    'cid': target_company.cid,
                    'logo': target_company.logo,
                    'name': target_company.name,
                    'category': target_company.category,
                    'brief': replace_urls_and_emails(target_company.brief),
                    'address': target_company.address,
                    'phone': target_company.phone,
                    'website': target_company.website,
                    'recruit_info': replace_urls_and_emails(target_company.recruit_info),
                    'recruit_url': replace_urls_and_emails(target_company.recruit_url),
                })
            except:
                pass
    else:
        for company in RecruitSignup.objects.all():
            try:
                target_company = Company.objects.get(cid=company.cid)
                companies.append({
                    'cid': target_company.cid,
                    'logo': target_company.logo,
                    'name': target_company.name,
                    'category': target_company.category,
                    'brief': replace_urls_and_emails(target_company.brief),
                    'address': target_company.address,
                    'phone': target_company.phone,
                    'website': target_company.website,
                    'recruit_info': replace_urls_and_emails(target_company.recruit_info),
                    'recruit_url': replace_urls_and_emails(target_company.recruit_url),
                })
            except:
                pass
    return render(request, 'recruit/public/list_jobs.html', locals())


def replace_urls_and_emails(original_str):
    urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', original_str)
    for url in urls:
        original_str = original_str.replace(url, '<a href="{}" target="_blank">連結</a>'.format(url))

    emails = re.findall(r'[\w\.-]+@[\w\.-]+(?:\.[\w]+)+', original_str, re.ASCII)
    for email in emails:
        original_str = original_str.replace(email, '<a href="mailto:{}" target="_blank">email</a>'.format(email))

    return '<span>' + original_str + '</span>'


def seminar(request):
    # semantic ui control
    sidebar_ui = {'seminar': "active"}
    
    try:
        recruit_config = RecruitConfigs.objects.all()[0]
    except IndexError:
        return render(request, 'recruit/error.html', {'error_msg' : "活動設定尚未完成，請聯絡行政人員設定"})
    
    start_date = recruit_config.seminar_start_date
    end_date = recruit_config.seminar_end_date
    recruit_seminar_info = recruit.models.RecruitSeminarInfo.objects.all()
    seminar_days = (end_date - start_date).days
    table_start_date = start_date
    # find the nearest Monday
    while (table_start_date.weekday() != 0):
        table_start_date -= datetime.timedelta(days=1)
    # make the length to 5 multiples
    # table_days = seminar_days + (seminar_days % 7) + 7
    table_days = seminar_days + (seminar_days % 7)
    dates_in_week = list()
    for week in range(0, int(table_days / 7)):
        # separate into 5 in each list (there are 5 days in a week)
        week_slot_info = []
        for day in range(5):
            today = table_start_date + datetime.timedelta(days=day + week * 7)
            noon1 = SeminarSlot.objects.filter(date=today, session='noon1').first()
            noon2 = SeminarSlot.objects.filter(date=today, session='noon2').first()
            noon3 = SeminarSlot.objects.filter(date=today, session='noon3').first()
            evening1 = SeminarSlot.objects.filter(date=today, session='evening1').first()
            evening2 = SeminarSlot.objects.filter(date=today, session='evening2').first()
            evening3 = SeminarSlot.objects.filter(date=today, session='evening3').first()
            week_slot_info.append(
                {
                    'date': today,
                    'noon1': '' if not noon1 or not noon1.company else
                    {
                        'company': noon1.company.get_company_name(),
                        'place_color': noon1.place.css_color if noon1.place else None
                    },
                    'noon2': '' if not noon2 or not noon2.company else
                    {
                        'company': noon2.company.get_company_name(),
                        'place_color': noon2.place.css_color if noon2.place else None
                    },
                    'noon3': '' if not noon3 or not noon3.company else
                    {
                        'company': noon3.company.get_company_name(),
                        'place_color': noon3.place.css_color if noon3.place else None
                    },
                    'evening1': '' if not evening1 or not evening1.company else
                    {
                        'company': evening1.company.get_company_name(),
                        'place_color': evening1.place.css_color if evening1.place else None
                    },
                    'evening2': '' if not evening2 or not evening2.company else
                    {
                        'company': evening2.company.get_company_name(),
                        'place_color': evening2.place.css_color if evening2.place else None
                    },
                    'evening3': '' if not evening3 or not evening3.company else
                    {
                        'company': evening3.company.get_company_name(),
                        'place_color': evening3.place.css_color if evening3.place else None
                    },
                }
            )
        dates_in_week.append(week_slot_info)
    locations = SlotColor.objects.all()
    return render(request, 'recruit/public/seminar.html', locals())


def seminar_temporary(request):
    # semantic ui control
    sidebar_ui = {'seminar': "active"}

    is_live = []
    not_live = []
    wo_info = []
    for company in RecruitSignup.objects.filter(~Q(seminar='none')):
        try:
            company_info = Company.objects.get(cid=company.cid)
            info = SeminarInfoTemporary.objects.get(company=company)
        except Company.DoesNotExist:
            pass
        except SeminarInfoTemporary.DoesNotExist:
            company_info = Company.objects.get(cid=company.cid)
            wo_info.append(
                {'name': company_info.get_short_name(),
                 'logo': company_info.logo.url,
                 'website': company_info.website,
                 }
            )
        else:
            video = parse_YT_video(info.video)
            if info.live:
                is_live.append(
                    {'name': company_info.get_short_name(),
                     'logo': company_info.logo.url,
                     'video': video,
                     'website': company_info.website,
                     'info': info,
                     })
            else:
                not_live.append(
                    {'name': company_info.get_short_name(),
                     'logo': company_info.logo.url,
                     'video': video,
                     'website': company_info.website,
                     'info': info,
                     }
                )

    is_live.sort(key=lambda x: x['info'].order, reverse=True)
    not_live.sort(key=lambda x: x['info'].order, reverse=True)
    session_all_info = is_live + not_live + wo_info

    recruit_seminar_info = recruit.models.RecruitSeminarInfo.objects.all()

    paginator = Paginator(session_all_info, 4)
    page_number = request.GET.get('page')

    try:
        session_info = paginator.page(page_number)
    except PageNotAnInteger:
        page_number = 1
        session_info = paginator.page(page_number)
    except EmptyPage:
        page_number = paginator.num_pages
        session_info = paginator.page(page_number)

    return render(request, 'recruit/public/seminar_temporary.html', locals())


def ece_seminar(request):
    # semantic ui control
    sidebar_ui = {'ece_seminar': "active"}

    recruit_seminar_info = recruit.models.RecruitECESeminarInfo.objects.all()

    return render(request, 'recruit/public/recruit_seminar_ece.html', locals())


def online_seminar(request):
    # semantic ui control
    sidebar_ui = {'online_seminar': "active"}
    
    try:
        recruit_config = RecruitConfigs.objects.all()[0]
    except IndexError:
        return render(request, 'recruit/error.html', {'error_msg' : "活動設定尚未完成，請聯絡行政人員設定"})
    
    start_date = recruit_config.seminar_online_start_date
    end_date = recruit_config.seminar_online_end_date
    recruit_seminar_info = recruit.models.RecruitOnlineSeminarInfo.objects.all()
    seminar_days = (end_date - start_date).days
    table_start_date = start_date
    # find the nearest Monday
    while (table_start_date.weekday() != 0):
        table_start_date -= datetime.timedelta(days=1)
    # make the length to 5 multiples
    # table_days = seminar_days + (seminar_days % 7) + 7
    table_days = seminar_days + (seminar_days % 7)
    dates_in_week = list()
    for week in range(0, int(table_days / 7)):
        # separate into 5 in each list (there are 5 days in a week)
        week_slot_info = []
        for day in range(5):
            today = table_start_date + datetime.timedelta(days=day + week * 7)
            noon1 = OnlineSeminarSlot.objects.filter(date=today, session='noon1').first()
            noon2 = OnlineSeminarSlot.objects.filter(date=today, session='noon2').first()
            evening1 = OnlineSeminarSlot.objects.filter(date=today, session='evening1').first()
            evening2 = OnlineSeminarSlot.objects.filter(date=today, session='evening2').first()
            evening3 = OnlineSeminarSlot.objects.filter(date=today, session='evening3').first()
            week_slot_info.append(
                {
                    'date': today,
                    'noon1': '' if not noon1 or not noon1.company else noon1.company.get_company_name(),
                    'noon2': '' if not noon2 or not noon2.company else noon2.company.get_company_name(),
                    'evening1': '' if not evening1 or not evening1.company else evening1.company.get_company_name(),
                    'evening2': '' if not evening2 or not evening2.company else evening2.company.get_company_name(),
                    'evening3': '' if not evening3 or not evening3.company else evening3.company.get_company_name(),
                }
            )
        dates_in_week.append(week_slot_info)
    return render(request, 'recruit/public/recruit_seminar_online.html', locals())


def jobfair(request):
    # semantic ui control
    sidebar_ui = {'jobfair': "active"}

    recruit_jobfair_info = RecruitJobfairInfo.objects.all()
    place_maps = Files.objects.filter(category='就博會攤位圖')
    jobfair_slots = JobfairSlot.objects.all().order_by('serial_no')
    elc_slots = JobfairSlot.objects.filter(category="消費電子").order_by('serial_no')
    semi_slots = JobfairSlot.objects.filter(category="半導體").order_by('serial_no')
    photo_slots = JobfairSlot.objects.filter(category="光電光學").order_by('serial_no')
    info_slots = JobfairSlot.objects.filter(category="資訊軟體").order_by('serial_no')
    network_slots = JobfairSlot.objects.filter(category="網路通訊").order_by('serial_no')
    synthesis_slots = JobfairSlot.objects.filter(category__in=["綜合", "集團", "人力銀行", "機構"]).order_by('serial_no')
    startup_slots = JobfairSlot.objects.filter(category="新創").order_by('serial_no')
    reserved_slots = JobfairSlot.objects.filter(category="主辦保留").order_by('serial_no')
    bio_slots = JobfairSlot.objects.filter(category="生科醫療").order_by('serial_no')
    # return render(request, 'recruit/public/jobfair_temp.html', locals())
    return render(request, 'recruit/public/jobfair.html', locals())


def jobfair_online(request, company_cid):
    try:
        # semantic ui control
        sidebar_ui = {'jobfair': "active"}

        comp_signup = RecruitSignup.objects.get(cid=company_cid)
        jobfair_info = JobfairInfoTemp.objects.get(company=comp_signup)

        video = parse_YT_video(jobfair_info.video)
        company = Company.objects.get(cid=company_cid)
        company_name = company.get_full_name()
        return render(request, 'recruit/public/jobfair_online.html', locals())
    except:
        return redirect('jobfair')


def online_jobfair(request):
    # semantic ui control
    sidebar_ui = {'online_jobfair': "active"}

    recruit_jobfair_info = RecruitOnlineJobfairInfo.objects.all()
    place_maps = Files.objects.filter(category='線上就博會攤位圖')
    jobfair_slots = OnlineJobfairSlot.objects.all().order_by('serial_no')
    elc_slots = OnlineJobfairSlot.objects.filter(category="消費電子").order_by('serial_no')
    semi_slots = OnlineJobfairSlot.objects.filter(category="半導體").order_by('serial_no')
    photo_slots = OnlineJobfairSlot.objects.filter(category="光電光學").order_by('serial_no')
    info_slots = OnlineJobfairSlot.objects.filter(category="資訊軟體").order_by('serial_no')
    network_slots = OnlineJobfairSlot.objects.filter(category="網路通訊").order_by('serial_no')
    synthesis_slots = OnlineJobfairSlot.objects.filter(category__in=["綜合", "集團", "人力銀行", "機構"]).order_by('serial_no')
    startup_slots = OnlineJobfairSlot.objects.filter(category="新創").order_by('serial_no')
    reserved_slots = OnlineJobfairSlot.objects.filter(category="主辦保留").order_by('serial_no')
    bio_slots = OnlineJobfairSlot.objects.filter(category="生科醫療").order_by('serial_no')
    return render(request, 'recruit/public/recruit_jobfair_online.html', locals())


def query_points(request):
    # semantic ui control
    sidebar_ui = {'query_points': "active"}

    student = None
    if (request.POST):
        student = Student.objects.filter(student_id=request.POST['student_id'],
                                         phone=request.POST['phone']).first()
        records = StuAttendance.objects.filter(student=student)
    return render(request, 'recruit/public/query_points.html', locals())
