import typing
from django.shortcuts import render, redirect
from django.http import JsonResponse, Http404, HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
import rdss.forms
import company.models
import rdss.models
import datetime, json
from datetime import timedelta
from company.models import Company
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Sum, IntegerField
from .data_import import ImportStudentCardID
from django.db.utils import IntegrityError
from django.urls import reverse
import re
from django.db.models.functions import Cast

import recruitment_common.views as views_helper

# for logging
import logging

# Create your views here.

logger = logging.getLogger('rdss')
collect_pts_logger = logging.getLogger('stu_attend')


@login_required(login_url='/company/login/')
def RDSSCompanyIndex(request):
    # semantic ui control
    menu_ui = {'rdss': "active"}
    sidebar_ui = {'index': "active"}
    
    try:
        configs = rdss.models.RdssConfigs.objects.all()[0]
    except IndexError:
        return render(request, 'error.html', {'error_msg' : "活動設定尚未完成，請聯絡行政人員設定"})
    rdss_company_info = rdss.models.RdssCompanyInfo.objects.all()
    plan_file = rdss.models.Files.objects.filter(category="企畫書").first()
    return render(request, 'company/rdss_company_entrance.html', locals())


@login_required(login_url='/company/login/')
def Status(request):
    if request.user.is_staff:
        return redirect("/admin")
    mycid = request.user.cid
    # get the dates from the configs
    try:
        configs = rdss.models.RdssConfigs.objects.all()[0]
    except IndexError:
        return render(request, 'error.html', {'error_msg' : "活動設定尚未完成，請聯絡行政人員設定"})
    signup_data = rdss.models.Signup.objects.filter(cid=mycid).first()
    mycompany = company.models.Company.objects.filter(cid=mycid).first()

    if mycompany.chinese_funded:
        return render(request, 'error.html', {'error_msg' : "本企業被政府判定為陸資企業，因此無法使用，請見諒"})

    pay_info_file = rdss.models.Files.objects.filter(category="繳費資訊").first()

    slot_info = {
        "seminar_select_time": "選位時間正在排定中",
        "jobfair_select_time": "選位時間正在排定中",
        "seminar_slot": "-",
        "jobfair_slot": "-",
    }

    # 問卷狀況
    try:
        rdss.models.CompanySurvey.objects.get(cid=request.user.cid)
        fill_survey = True
    except:
        fill_survey = False

    # 選位時間和數量狀態
    seminar_select_time = rdss.models.SeminarOrder.objects.filter(company=mycid).first()
    jobfair_select_time = rdss.models.JobfairOrder.objects.filter(company=mycid).first()
    seminar_slot = rdss.models.SeminarSlot.objects.filter(company=mycid).first()
    jobfair_slot = rdss.models.JobfairSlot.objects.filter(company=mycid)
    if seminar_select_time and not seminar_slot:
        slot_info['seminar_select_time'] = seminar_select_time.time
        slot_info['seminar_slot'] = "請依時段於左方選單選位"
    if jobfair_select_time and not jobfair_slot:
        slot_info['jobfair_select_time'] = jobfair_select_time.time
        slot_info['jobfair_slot'] = "請依時段於左方選單選位"

    if seminar_slot:
        slot_info['seminar_slot'] = "{} {}".format(seminar_slot.date,
                                                   seminar_slot.session_from_config.get_display_name()
                                                   )
    if jobfair_slot:
        slot_info['jobfair_slot'] = [int(s.serial_no) for s in jobfair_slot]

    # Fee display
    total_fee = 0
    discount = 0
    discount_text: list[str] = []
    fee = 0
    try:
        # session fee calculation
        if signup_data.seminar == 'attend':
            seminar_fee = signup_data.seminar_type.session_fee
            seminar_fee_text = f"說明會 ({seminar_fee} 元)"
            fee += seminar_fee

        # ece seminar fee
        if mycompany.ece_member:
            discount_num_of_ece = 0
            for ece_seminar in signup_data.seminar_ece.all():
                if ece_seminar.ece_member_discount:
                    discount_num_of_ece += 1
            discount += configs.session_ece_fee * discount_num_of_ece
            discount_text.append(f"貴公司為電機研究所聯盟永久會員，可享有ECE說明會場次免費優惠 -{discount}元")
        num_of_ece = len(signup_data.seminar_ece.all())
        if num_of_ece:
            ece_seminar_fee = configs.session_ece_fee * num_of_ece
            fee += ece_seminar_fee

        # jobfair fee calculation
        if signup_data.jobfair:
            if mycompany.ece_member or mycompany.gloria_normal:
                ece_discount = min(signup_data.jobfair, 1) * configs.jobfair_booth_fee
                discount_text.append(f"貴公司為電機研究所聯盟永久會員或Gloria會員，可享有第一攤免費優惠 -{ece_discount}元")
                discount += ece_discount
            elif mycompany.gloria_startup:
                startup_discount = min(signup_data.jobfair, 1) * configs.jobfair_booth_fee
                discount_text.append(f"貴公司為Gloria新創會員，可享有第一攤免費優惠 -{startup_discount}元")
                discount += startup_discount
            elif signup_data.zone and signup_data.zone.name != '一般企業':
                zone_discount = min(signup_data.jobfair, 1) * signup_data.zone.discount
                discount_text.append(f"貴公司為{signup_data.zone}專區，可享有第一攤優惠減免{signup_data.zone.discount}元")
                discount += zone_discount

            jobfair_fee = signup_data.jobfair * configs.jobfair_booth_fee
            fee += jobfair_fee

        rdss_mycompany_category = rdss.models.CompanyCategories.objects.get(name=mycompany.categories.name)
        if rdss_mycompany_category.discount:
            discount_text = [(f"貴公司類別為{rdss_mycompany_category.name}，可享有免費優惠")]
            discount = fee

    except AttributeError:
        pass

    # Sponsor fee display
    sponsor_amount = 0
    sponsorships = rdss.models.Sponsorship.objects.filter(company__cid=request.user.cid)
    for s in sponsorships:
        sponsor_amount += s.item.price

    total_fee += fee + sponsor_amount - discount

    # Seminar and Jobfair info status
    try:
        seminar_info = rdss.models.SeminarInfo.objects.get(company=request.user.cid)
    except ObjectDoesNotExist:
        seminar_info = None
    try:
        jobfair_info = rdss.models.JobfairInfo.objects.get(company=request.user.cid)
    except ObjectDoesNotExist:
        jobfair_info = None

    # control semantic ui class
    step_ui = ["", "", ""]  # for step ui in template
    nav_rdss = "active"
    sidebar_ui = {'status': "active"}
    menu_ui = {'rdss': "active"}

    step_ui[0] = "completed" if signup_data else "active"
    step_ui[1] = "completed" if jobfair_slot or seminar_slot else "active"
    step_ui[2] = "completed" if jobfair_info or seminar_info else "active"

    return render(request, 'company/status.html', locals())

def _check_category_in_right_zone(zone: rdss.models.ZoneCategories, mycompany: Company) -> bool:
    if zone.name != "一般企業":
        my_company_category = rdss.models.CompanyCategories.objects.get(
            name=mycompany.categories.name
        )
        if my_company_category not in zone.category.all():
            return False
    return True

@login_required(login_url='/company/login/')
def SignupRdss(request):
    if request.user.is_staff:
        return redirect("/admin")

    # semanti ui control
    sidebar_ui = {'signup': "active"}
    menu_ui = {'rdss': "active"}

    try:
        configs = rdss.models.RdssConfigs.objects.all()[0]
        seminar_choices = rdss.models.ConfigSeminarChoice.objects.all()
        seminar_sessions = rdss.models.ConfigSeminarSession.objects.all().order_by('session_start')
    except IndexError:
        return render(request, 'error.html', {'error_msg' : "活動設定尚未完成，請聯絡行政人員設定"})

    grouped_sessions = {}
    for session in seminar_sessions:
        key = session.qualification.name if session.qualification else "none"
        if key not in grouped_sessions:
            grouped_sessions[key] = []
        grouped_sessions[key].append(session)

    mycompany = Company.objects.filter(cid=request.user.cid).first()
    if mycompany.chinese_funded:
        return render(request, 'error.html', {'error_msg' : "本企業被政府判定為陸資企業，因此無法使用，請見諒"})

    # use timezone now to get current time with GMT+8
    if timezone.now() > configs.rdss_signup_end or timezone.now() < configs.rdss_signup_start:
        if request.user.username != "77777777":
            error_msg = "現在並非報名時間。報名期間為 {} 至 {}".format(
                timezone.localtime(configs.rdss_signup_start).strftime("%Y/%m/%d %H:%M:%S"),
                timezone.localtime(configs.rdss_signup_end).strftime("%Y/%m/%d %H:%M:%S"))
            return render(request, 'error.html', locals())

    plan_file = rdss.models.Files.objects.filter(category="企畫書").first()
    # Check if the company has filled the survey. If not, disable the signup button
    try:
        rdss.models.CompanySurvey.objects.get(cid=request.user.cid)
        fill_survey = True
    except ObjectDoesNotExist:
        fill_survey = False
        messages.error(request, '尚未填寫問卷，請先填寫問卷才能送出/儲存報名資料')

    try:
        signup_info = rdss.models.Signup.objects.get(cid=request.user.cid)
    except ObjectDoesNotExist:
        signup_info = None

    if request.POST:
        # copy the data from post
        data = request.POST.copy()
        # decide cid in the form
        data['cid'] = request.user.cid
        filtered_zone = data.get('zone', None)
        try:
            filtered_zone_obj = rdss.models.ZoneCategories.objects.get(id=filtered_zone)
        except ObjectDoesNotExist:
            filtered_zone_obj = None

        # check if the company is right zone
        if not _check_category_in_right_zone(filtered_zone_obj, mycompany):
            messages.error(request, f'貴公司不屬於{filtered_zone_obj.name}專區指定類別，請重新選擇')
            form = rdss.forms.SignupCreationForm(data, instance=signup_info)
            return render(request, 'company/signup_form.html', locals())
        else:
            form = rdss.forms.SignupCreationForm(data, instance=signup_info)

        if form.is_valid():
            form.save()
            form.save_m2m()
        else:
            # for debug usage
            print(form.errors.items())
        return redirect(SignupRdss)
    else:
        form = rdss.forms.SignupCreationForm(instance=signup_info)
    return render(request, 'company/signup_form.html', locals())


@login_required(login_url='/company/login/')
def SeminarInfo(request):
    # semantic ui control
    sidebar_ui = {'seminar_info': "active"}
    menu_ui = {'rdss': "active"}

    try:
        company = rdss.models.Signup.objects.get(cid=request.user.cid)
    except Exception as e:
        error_msg = "貴公司尚未報名本次「秋季招募」活動，請於左方點選「填寫報名資料」"
        return render(request, 'error.html', locals())
    if company.seminar == "none":
        return render(request, 'error.html', {'error_msg' : "貴公司已報名本次秋季招募活動，但並末勾選參加說明會選項。"})

    mycompany = Company.objects.filter(cid=request.user.cid).first()
    if mycompany.chinese_funded:
        return render(request, 'error.html', {'error_msg' : "本企業被政府判定為陸資企業，因此無法使用，請見諒"})
    try:
        seminar_info = rdss.models.SeminarInfo.objects.get(company=company)
    except ObjectDoesNotExist:
        seminar_info = None
    
    try:
        deadline = rdss.models.RdssConfigs.objects.values('seminar_info_deadline')[0]['seminar_info_deadline']
    except IndexError:
        return render(request, 'error.html', {'error_msg' : "活動設定尚未完成，請聯絡行政人員設定"})

    if timezone.now() > deadline:
        error_msg = "企業說明會資訊填寫時間已截止!若有更改需求，請來信或來電。"
        return render(request, 'error.html', locals())


    if request.POST:
        data = request.POST.copy()
        data['company'] = company.cid
        form = rdss.forms.SeminarInfoCreationForm(data=data, instance=seminar_info)
        if form.is_valid():
            form.save()
            return redirect(SeminarInfo)
        else:
            print(form.errors)
    else:
        form = rdss.forms.SeminarInfoCreationForm(instance=seminar_info)

    # semantic ui
    sidebar_ui = {'seminar_info': "active"}
    menu_ui = {'rdss': "active"}

    return render(request, 'company/seminar_info_form.html', locals())


@login_required(login_url='/company/login/')
def JobfairInfo(request):
    # semantic ui control
    sidebar_ui = {'jobfair_info': "active"}
    menu_ui = {'rdss': "active"}

    mycompany = Company.objects.filter(cid=request.user.cid).first()
    if mycompany.chinese_funded:
        return render(request, 'error.html', {'error_msg' : "本企業被政府判定為陸資企業，因此無法使用，請見諒"})

    try:
        configs = rdss.models.RdssConfigs.objects.all()[0]
        food_type = configs.jobfair_food
        food_info = configs.jobfair_food_info
        deadline = configs.jobfair_info_deadline
    except IndexError:
        return render(request, 'error.html', {'error_msg' : "活動設定尚未完成，請聯絡行政人員設定"})
    reach_deadline =timezone.now() > deadline

    try:
        company = rdss.models.Signup.objects.get(cid=request.user.cid)
        if company.jobfair == 0:
            error_msg = "貴公司已報名本次秋季招募活動，但並末填寫就博會攤位。"
            return render(request, 'error.html', locals())
        booth_num = company.jobfair
        booth_quantity = booth_num * 3
        # (2025 rdss) Not distribute parking tickets anymore.
        # Temporary left this variable and hide the field in the frontend form.
        booth_parking_tickets = booth_num * 2
    except Exception as e:
        error_msg = "貴公司尚未報名本次「秋季招募」活動，請於左方點選「填寫報名資料」"
        return render(request, 'error.html', locals())

    # check whether the company job fair info is in the DB
    try:
        jobfair_info = rdss.models.JobfairInfo.objects.get(company=company)
    except ObjectDoesNotExist:
        jobfair_info = None
    
    initial_data = {'meat_lunchbox': booth_quantity}

    if request.POST:
        data = request.POST.copy()
        form = rdss.forms.JobfairInfoCreationForm(data=data, instance=jobfair_info, max_num=booth_num)
        if form.is_valid():
            new_info = form.save(commit=False)
            company = rdss.models.Signup.objects.get(cid=request.user.cid)
            new_info.company = company
            new_info.save()
            return redirect(JobfairInfo)
        else:
            print(form.errors)
    else:
        form = rdss.forms.JobfairInfoCreationForm(instance=jobfair_info, max_num=booth_num, initial=initial_data)

    # semantic ui
    sidebar_ui = {'jobfair_info': "active"}
    menu_ui = {'rdss': "active"}

    return render(request, 'company/jobfair_info_form.html', locals())


@login_required(login_url='/company/login/')
def SeminarSelectFormGen(request):
    # semantic ui control
    sidebar_ui = {'seminar_select': "active"}
    menu_ui = {'rdss': "active"}

    mycid = request.user.cid
    mycompany = Company.objects.filter(cid=request.user.cid).first()
    if mycompany.chinese_funded:
        return render(request, 'error.html', {'error_msg' : "本企業被政府判定為陸資企業，因此無法使用，請見諒"})
    # check the company have signup rdss
    try:
        my_signup = rdss.models.Signup.objects.get(cid=request.user.cid)
        # check the company have signup seminar
        if my_signup.seminar == "none":
            error_msg = "貴公司已報名本次秋季招募活動，但並末勾選參加說明會選項。"
            return render(request, 'error.html', locals())
    except Exception as e:
        error_msg = "貴公司尚未報名本次「秋季招募」活動，請於左方點選「填寫報名資料」"
        return render(request, 'error.html', locals())

    # check the company have been assigned a slot select order and time
    try:
        seminar_select_time = rdss.models.SeminarOrder.objects.filter(company=mycid).first().time
    except Exception as e:
        seminar_select_time = "選位時間及順序尚未排定，您可以先參考下方說明會時間表"

    seminar_type = my_signup.seminar_type

    try:
        configs = rdss.models.RdssConfigs.objects.all()[0]
    except IndexError:
        return render(request, 'error.html', {'error_msg' : "活動設定尚未完成，請聯絡行政人員設定"})
    seminar_start_date = configs.seminar_start_date
    seminar_end_date = configs.seminar_end_date
    seminar_days = (seminar_end_date - seminar_start_date).days
    table_start_date = seminar_start_date
    enable_time = configs.seminar_btn_enable_time
    disable_time = configs.seminar_btn_disable_time
    # find the nearest Monday
    while table_start_date.weekday() != 0:
        table_start_date -= datetime.timedelta(days=1)
    # make the length to 5 multiples
    # table_days = seminar_days + (seminar_days % 7) + 7
    dates_in_week = list()
    weeks = seminar_end_date.isocalendar()[1] - seminar_start_date.isocalendar()[1] + 1
    for week in range(0, weeks):
        # separate into 5 in each list (there are 5 days in a week)
        dates_in_week.append([(table_start_date + datetime.timedelta(days=day + week * 7)) \
                              for day in range(0, 5)])

    slot_colors = rdss.models.SlotColor.objects.all()

    config_session_list = rdss.models.ConfigSeminarSession.objects \
        .all().order_by('session_start')
    return render(request, 'company/seminar_select.html', locals())


@login_required(login_url='/company/login/')
def SeminarSelectControl(request):
    if request.method == "POST":
        post_data = json.loads(request.body.decode())
        action = post_data.get("action")
    else:
        raise Http404("What are u looking for?")

    # action query
    try:
        configs = rdss.models.RdssConfigs.objects.all()[0]
    except IndexError:
        return render(request, 'error.html', {'error_msg' : "活動設定尚未完成，請聯絡行政人員設定"})
    if action == "query":
        try:
            my_signup = rdss.models.Signup.objects.get(cid=request.user.cid)
        except rdss.models.Signup.DoesNotExist:
            return JsonResponse({"success": False, "msg": "貴公司尚未報名本次活動"})

        slots = rdss.models.SeminarSlot.objects.all()
        return_data = {}
        for s in slots:
            index = "{}_{}_{}".format(s.session_from_config, s.date.strftime("%Y%m%d"), s.place.id if s.place else 0)
            return_data[index] = {}

            return_data[index]['place_color'] = None if not s.place else \
                s.place.css_color
            return_data[index]["cid"] = "None" if not s.company else \
                s.company.get_company_name()

            my_seminar_session_type = rdss.models.Signup.objects.filter(cid=request.user.cid).first().seminar_type

            # session wrong (signup A type seminar but choose B type)
            if s.session_from_config.qualification and \
                s.session_from_config.qualification != my_seminar_session_type:
                return_data[index]['valid'] = False
            else:
                return_data[index]['valid'] = True

            # check if the company is in right zone and the special user
            if s.place and s.place.zone.name != "一般企業" and request.user.cid != '77777777':
                if s.place.zone != my_signup.zone:
                    return_data[index]['valid'] = False

        my_slot = rdss.models.SeminarSlot.objects.filter(company__cid=request.user.cid).first()
        if my_slot:
            return_data['my_slot'] = True
        else:
            return_data['my_slot'] = False

        try:
            my_select_time = rdss.models.SeminarOrder.objects.filter(company=request.user.cid).first().time
        except AttributeError:
            my_select_time = None

        # Open button for 77777777
        if (not my_select_time or timezone.now() < my_select_time) and request.user.username != '77777777':
            select_ctrl = {}
            select_ctrl['display'] = True
            select_ctrl['msg'] = '目前非貴公司選位時間，可先參考說明會時間表，並待選位時間內選位'
            select_ctrl['select_btn'] = False
        else:
            select_ctrl = {}
            select_ctrl['display'] = False
            select_ctrl['select_btn'] = True
            now_time = datetime.datetime.now()
            in_date_range = configs.seminar_btn_start <= now_time.date() <= configs.seminar_btn_end
            in_time_range = (
                configs.seminar_btn_enable_time <= now_time.time() <= configs.seminar_btn_disable_time
            )
            is_special_user = request.user.username == '77777777'
            print(now_time, configs.seminar_btn_enable_time, configs.seminar_btn_disable_time)
            print(in_date_range, in_time_range)
            select_ctrl['btn_display'] = (in_date_range and in_time_range) or is_special_user

        return JsonResponse({"success": True, "data": return_data, "select_ctrl": select_ctrl})

    # action select
    elif action == "select":
        mycid = request.user.cid
        # Open selection for 77777777
        if request.user.username != '77777777':
            my_select_time = rdss.models.SeminarOrder.objects.filter(company=mycid).first().time
            if not my_select_time or timezone.now() < my_select_time:
                return JsonResponse({"success": False, 'msg': '選位失敗，目前非貴公司選位時間'})

        _, start_str, end_str, slot_date_str, slot_place_id = post_data.get("slot").split('_')
        slot_date = datetime.datetime.strptime(slot_date_str, "%Y%m%d")
        slot_session_start = datetime.datetime.strptime(start_str, "%H%M").time()
        slot_session_end = datetime.datetime.strptime(end_str, "%H%M").time()

        try:
            slot_session = rdss.models.ConfigSeminarSession.objects.get(
                session_start=slot_session_start, session_end=slot_session_end
            )
            slot = rdss.models.SeminarSlot.objects.get(date=slot_date, session_from_config=slot_session, place=slot_place_id)
            my_signup = rdss.models.Signup.objects.get(cid=request.user.cid)
        except:
            return JsonResponse({"success": False, 'msg': '選位失敗，時段錯誤或貴公司未勾選參加說明會'})

        if slot.company != None:
            return JsonResponse({"success": False, 'msg': '選位失敗，該時段已被選定'})

        if slot and my_signup:
            slot.company = my_signup
            slot.save()
            logger.info('{} select seminar slot {} {}'.format(my_signup.get_company_name(), slot.date, slot.session_from_config))
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False, 'msg': '選位失敗，時段錯誤或貴公司未勾選參加說明會'})

    # end of action select
    elif action == "cancel":

        my_slot = rdss.models.SeminarSlot.objects.filter(company__cid=request.user.cid).first()
        if my_slot:
            logger.info('{} cancel seminar slot {} {}'.format(
                my_slot.company.get_company_name(), my_slot.date, my_slot.session_from_config))
            my_slot.company = None
            my_slot.save()
            return JsonResponse({"success": True})
        else:
            logger.error(f'Cancel seminar slot failed. Cannot find slot for company {request.user.cid}')
            return JsonResponse({"success": False, "msg": "刪除說明會選位失敗"})

    else:
        pass
    raise Http404("What are u looking for?")


@login_required(login_url='/company/login/')
def JobfairSelectFormGen(request):
    # semantic ui control
    sidebar_ui = {'jobfair_select': "active"}
    menu_ui = {'rdss': "active"}

    mycompany = Company.objects.filter(cid=request.user.cid).first()
    if mycompany.chinese_funded:
        return render(request, 'error.html', {'error_msg' : "本企業被政府判定為陸資企業，因此無法使用，請見諒"})
    mycid = request.user.cid
    # check the company have signup rdss
    try:
        my_signup = rdss.models.Signup.objects.get(cid=request.user.cid)
        # check the company have signup seminar
        if my_signup.jobfair == 0:
            error_msg = "貴公司已報名本次秋季招募活動，但並末填寫就博會攤位。"
            return render(request, 'error.html', locals())
    except Exception as e:
        error_msg = "貴公司尚未報名本次「秋季招募」活動，請於左方點選「填寫報名資料」"
        return render(request, 'error.html', locals())

    # check the company have been assigned a slot select order and time
    try:
        jobfair_select_time = rdss.models.JobfairOrder.objects.filter(company=mycid).first().time
    except Exception as e:
        jobfair_select_time = "選位時間及順序尚未排定，您可以先參考攤位圖"

    slots = rdss.models.JobfairSlot.objects.all()
    place_map = rdss.models.Files.objects.filter(category='就博會攤位圖').first()
    enable_time = rdss.models.RdssConfigs.objects.all()[0].jobfair_btn_enable_time
    disable_time = rdss.models.RdssConfigs.objects.all()[0].jobfair_btn_disable_time
    return render(request, 'company/jobfair_select.html', locals())


@login_required(login_url='/company/login/')
def JobfairSelectControl(request):
    if request.method == "POST":
        mycid = request.user.cid
        post_data = json.loads(request.body.decode())
        action = post_data.get("action")
    else:
        raise Http404("What are u looking for?")

    try:
        my_signup = rdss.models.Signup.objects.get(cid=request.user.cid)
    except:
        ret = dict()
        ret['success'] = False
        ret['msg'] = "選位失敗，攤位錯誤或貴公司未勾選參加就博會"
        return JsonResponse(ret)
    
    try:
        configs = rdss.models.RdssConfigs.objects.all()[0]
    except IndexError:
        return render(request, 'error.html', {'error_msg' : "活動設定尚未完成，請聯絡行政人員設定"})

    if action == "query":
        zones = rdss.models.ZoneCategories.objects.all()
        slot_group = []
        for zone in zones:
            slot_list = rdss.models.JobfairSlot.objects.filter(zone=zone).annotate(
                serial_no_int=Cast('serial_no', IntegerField())
            ).order_by('serial_no_int')
            return_data = []
            for slot in slot_list:
                slot_info = {}
                slot_info["serial_no"] = slot.serial_no
                slot_info["company"] = None if not slot.company_id else \
                    slot.company.get_company_name()
                return_data.append(slot_info)
            is_myzone = (
                (rdss.models.Signup.objects.filter(cid=request.user.cid).first().zone == zone) 
                or
                (zone.name == '一般企業')
            )
            slot_group.append({
                'slot_type': zone.id,
                'display': zone.name,
                'slot_list': return_data,
                'is_myzone': bool(is_myzone),
            })

        my_slot_list = [slot.serial_no for slot in
                        rdss.models.JobfairSlot.objects.filter(company__cid=request.user.cid)]

        try:
            my_select_time = rdss.models.JobfairOrder.objects.filter(company=request.user.cid).first().time
        except AttributeError:
            my_select_time = None

        # Open button for 77777777
        if (not my_select_time or timezone.now() < my_select_time) and request.user.username != '77777777':
            select_ctrl = dict()
            select_ctrl['display'] = True
            select_ctrl['msg'] = '目前非貴公司選位時間，可先參考攤位圖，並待選位時間內選位'
            select_ctrl['select_enable'] = False
            select_ctrl['select_btn'] = False
        else:
            select_ctrl = dict()
            select_ctrl['display'] = False
            select_ctrl['select_btn'] = True
            select_ctrl['select_enable'] = True
            now_time = datetime.datetime.now()
            in_date_range = configs.jobfair_btn_start <= now_time.date() <= configs.jobfair_btn_end
            in_time_range = (
                configs.jobfair_btn_enable_time <= now_time.time() <= configs.jobfair_btn_disable_time
            )
            is_special_user = request.user.username == '77777777'

            select_ctrl['btn_display'] = (in_date_range and in_time_range) or is_special_user

        return JsonResponse({"success": True,
                             "data": slot_group,
                             "my_slot_list": my_slot_list,
                             "select_ctrl": select_ctrl})
    
    elif action == "select":
        try:
            slot = rdss.models.JobfairSlot.objects.get(serial_no=post_data.get('slot'))
            my_signup = rdss.models.Signup.objects.get(cid=request.user.cid)
        except:
            ret = dict()
            ret['success'] = False
            ret['msg'] = "選位失敗，攤位錯誤或貴公司未勾選參加就博會"
            return JsonResponse(ret)
        if slot.company != None:
            return JsonResponse({"success": False, 'msg': '選位失敗，該攤位已被選定'})

        # Open selection for 77777777
        if request.user.username != '77777777':
            my_select_time = rdss.models.JobfairOrder.objects.filter(company=request.user.cid).first().time
            if timezone.now() < my_select_time:
                return JsonResponse({"success": False, 'msg': '選位失敗，目前非貴公司選位時間'})

        my_slot_list = rdss.models.JobfairSlot.objects.filter(company__cid=request.user.cid)
        if my_slot_list.count() >= my_signup.jobfair:
            return JsonResponse({"success": False, 'msg': '選位失敗，貴公司攤位數已達上限'})

        slot.company = my_signup
        slot.save()
        logger.info('{} select jobfair slot {}'.format(my_signup.get_company_name(), slot.serial_no))
        return JsonResponse({"success": True})

    elif action == "cancel":
        cancel_slot_no = post_data.get('slot')
        cancel_slot = rdss.models.JobfairSlot.objects.filter(
            company__cid=request.user.cid,
            serial_no=cancel_slot_no).first()
        if cancel_slot:
            logger.info(
                '{} cancel jobfair slot {}'.format(cancel_slot.company.get_company_name(), cancel_slot.serial_no))
            cancel_slot.company = None
            cancel_slot.save()
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False, "msg": "刪除就博會攤位失敗"})
    else:
        raise Http404("Invalid")


def Add_SponsorShip(sponsor_items, post_data, sponsor):
    # clear sponsor ships objects
    success_item = list()
    fail_item = list()
    old_sponsorships = rdss.models.Sponsorship.objects.filter(company=sponsor)
    for item in old_sponsorships:
        item.delete()
    for item in sponsor_items:
        obj = None
        if item.name in post_data:
            if rdss.models.Sponsorship.objects.filter(item=item).count() < item.limit:
                obj = rdss.models.Sponsorship.objects.create(company=sponsor, item=item)
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
    menu_ui = {'rdss': "active"}

    try:
        configs = rdss.models.RdssConfigs.objects.all()[0]
    except IndexError:
        return render(request, 'error.html', {'error_msg' : "活動設定尚未完成，請聯絡行政人員設定"})
    
    mycompany = company.models.Company.objects.filter(cid=request.user.cid).first()
    if mycompany.chinese_funded:
        return render(request, 'error.html', {'error_msg' : "本企業被政府判定為陸資企業，因此無法使用，請見諒"})
    
    if timezone.now() < configs.rdss_signup_start or timezone.now() > configs.rdss_signup_end:
        if request.user.username != "77777777":
            error_msg = "非贊助時間。期間為 {} 至 {}".format(
                timezone.localtime(configs.rdss_signup_start).strftime("%Y/%m/%d %H:%M:%S"),
                timezone.localtime(configs.rdss_signup_end).strftime("%Y/%m/%d %H:%M:%S"))
            return render(request, 'error.html', locals())
    # get form post
    try:
        sponsor = rdss.models.Signup.objects.get(cid=request.user.cid)
    except Exception as e:
        error_msg = "貴公司尚未報名本次「秋季招募」活動，請於左方點選「填寫報名資料」"
        return render(request, 'error.html', locals())

    if request.POST:
        sponsor_items = rdss.models.SponsorItems.objects.all()
        succ_msg, fail_msg = Add_SponsorShip(sponsor_items, request.POST, sponsor)
        msg = {
            "display": True,
            "content": "儲存成功!",
            "succ_msg": succ_msg,
            "fail_msg": fail_msg
        }

    # 活動專刊的部份是變動不大，且版面特殊，採客製寫法
    monograph_main = rdss.models.SponsorItems.objects.filter(name="活動專刊").first()
    monograph_items = rdss.models.SponsorItems.objects.filter(name__contains="活動專刊").exclude(name="活動專刊") \
        .annotate(num_sponsor=Count('sponsorship'))
    other_items = rdss.models.SponsorItems.objects.all().exclude(name__contains="活動專刊") \
        .annotate(num_sponsor=Count('sponsorship'))
    sponsorship = rdss.models.Sponsorship.objects.filter(company=sponsor)
    my_sponsor_items = [s.item for s in sponsorship]
    return render(request, 'company/sponsor.html', locals())


@staff_member_required
def SponsorAdmin(request):
    site_header = "OpenHouse 管理後台"
    site_title = "OpenHouse"

    # get sponsor and company object
    sponsor_items = rdss.models.SponsorItems.objects.all() \
        .annotate(num_sponsor=Count('sponsorship'))
    companies = rdss.models.Signup.objects.all()

    # handle search item
    search_term = request.GET.get('q', '').strip()
    if search_term:
        companies = list(companies.filter(cid__icontains=search_term)) + [
                c for c in companies if search_term in c.get_company_name()
            ]

    # Make sponsorship info
    sponsorships_list = list()
    for c in companies:
        shortname = company.models.Company.objects.filter(cid=c.cid).first().shortname
        sponsorships = rdss.models.Sponsorship.objects.filter(company=c)
        counts = [rdss.models.Sponsorship.objects.filter(company=c, item=item).count() for item in sponsor_items]
        amount = 0
        latest_sponsorship = rdss.models.Sponsorship.objects.filter(company=c).order_by('-updated').first()

        for s in sponsorships:
            amount += s.item.price
        sponsorships_list.append({
            "cid": c.cid,
            "counts": counts,
            "amount": amount,
            "shortname": shortname,
            "update_time": latest_sponsorship.updated if latest_sponsorship else None,
            "id": c.id,
            "change_url": reverse('admin:rdss_signup_change',
                                               args=(c.id,))
        })

    return render(request, 'admin/sponsor_admin.html', locals())


@login_required(login_url='/company/login/')
def CompanySurvey(request):
    try:
        configs = rdss.models.RdssConfigs.objects.all()[0]
    except IndexError:
        return render(request, 'error.html', {'error_msg' : "活動設定尚未完成，請聯絡行政人員設定"})

    mycompany = Company.objects.filter(cid=request.user.cid).first()
    if mycompany.chinese_funded:
        return render(request, 'error.html', {'error_msg' : "本企業被政府判定為陸資企業，因此無法使用，請見諒"})
    # semantic ui
    sidebar_ui = {'survey': "active"}
    menu_ui = {'rdss': "active"}

    if timezone.now() > configs.survey_end or timezone.now() < configs.survey_start:
        if request.user.username != "77777777":
            error_msg = "問卷填答已結束。期間為 {} 至 {}".format(
                timezone.localtime(configs.survey_start).strftime("%Y/%m/%d %H:%M:%S"),
                timezone.localtime(configs.survey_end).strftime("%Y/%m/%d %H:%M:%S"))
            return render(request, 'error.html', locals())

    try:
        my_survey = rdss.models.CompanySurvey.objects.get(cid=request.user.cid)
    except ObjectDoesNotExist:
        my_survey = None

    try:
        is_sign_up = rdss.models.Signup.objects.get(cid=request.user.cid)
    except ObjectDoesNotExist:
        is_sign_up = None

    if request.POST:
        data = request.POST.copy()
        # decide cid in the form
        data['cid'] = request.user.cid
        form = rdss.forms.SurveyForm(data=data, instance=my_survey)
        if form.is_valid():
            form.save()
            (msg_display, msg_type, msg_content) = (True, "green", "問卷填寫完成，感謝您")
            if not is_sign_up:
                messages.success(request, '滿意度問卷填答成功，可以進行報名')
                return redirect(Status)
        else:
            (msg_display, msg_type, msg_content) = (True, "error", "儲存失敗，有未完成欄位")
            print(form.errors)
    else:
        (msg_type, msg_content) = ("green", "問卷填寫完成，感謝您")
        form = rdss.forms.SurveyForm(instance=my_survey)

    return render(request, 'company/survey_form.html', locals())

# ========================RDSS admin view for seminar points=================
def _reach_seminar_daily_threshold(student_obj) -> typing.Tuple[bool, str, bool]:
    """
    Check whether the student has attended all/specific number of seminars a day.

    Args:
        student_obj: Student object
    Returns:
        tuple[bool, str, bool]
            bool: Whether the student has reached the daily threshold.
            str: The date of the redeemed prize.
            bool: Whether the student has redeemed.
    """
    today = datetime.datetime.now().date()
    attended_seminar = rdss.models.StuAttendance.objects.filter(student=student_obj,
                                                                seminar__date=today).count()
    total_seminar = rdss.models.SeminarSlot.objects.filter(date=today).count()

    try:
        configs = rdss.models.RdssConfigs.objects.all()[0]
        daily_threshold = configs.seminar_prize_threshold
        is_all_attendance_has_prize = configs.seminar_prize_all
    except IndexError:
        daily_threshold = 10
        is_all_attendance_has_prize = False

    if (is_all_attendance_has_prize and attended_seminar == total_seminar) or \
        (attended_seminar >= daily_threshold):
        redeem_date = str(today)
        redeem_obj, _ = rdss.models.RedeemDailyPrize.objects.get_or_create(
            student=student_obj,
            date=redeem_date
        )
        return True, redeem_date, redeem_obj.redeem
    return False, None, None

@staff_member_required
def show_student_with_daily_seminar_prize(request):
    site_header = "OpenHouse 管理後台"
    site_title = "OpenHouse"
    title = "每日說明會參與達成＆兌換名單"
    try:
        configs = rdss.models.RdssConfigs.objects.all()[0]
        daily_threshold = configs.seminar_prize_threshold
        is_all_attendance_has_prize = configs.seminar_prize_all
    except IndexError:
        daily_threshold = 10
        is_all_attendance_has_prize = False
    attended_students = rdss.models.RedeemDailyPrize.objects.all()
    return render(request, 'admin/seminar_show_student_with_daily_seminar_prize.html', locals())

@staff_member_required
def redeem_seminar_daily_prize(request, card_num, date):
    referer = request.META.get('HTTP_REFERER')

    try:
        student_obj = rdss.models.Student.objects.filter(idcard_no=card_num).first()
    except Exception as e:
        messages.error(request, f"學生證卡號不存在: {e}，請註冊學生證")
        return redirect(referer)

    try:
        rdss.models.RedeemPrize.objects.get_or_create(
            student=student_obj, prize=f"每日獎品-{date}"
        )
        rdss.models.RedeemDailyPrize.objects.filter(
            student=student_obj, date=date
        ).update(redeem=True)
        messages.success(request, f"學生 {student_obj.student_id} 兌換每日獎品成功，日期: {date}")
        collect_pts_logger.info('student %s succeeded to get daily seminar prize, date: %s', student_obj.student_id, date)
    except Exception as e:
        messages.error(request, f"兌換失敗: {e}")
    return redirect(referer)

@staff_member_required
def CollectPoints(request):
    site_header = "OpenHouse 管理後台"
    site_title = "OpenHouse"
    title = "秋招說明會集點"

    try:
        configs = rdss.models.RdssConfigs.objects.all()[0]
    except IndexError:
        return render(request, 'error.html', {'error_msg' : "活動設定尚未完成，請聯絡行政人員設定"})
    today = datetime.datetime.now().date()
    now = datetime.datetime.now()

    # Find place of session
    seminar_places = rdss.models.SlotColor.objects.all()
    seminar_list = rdss.models.SeminarSlot.objects.filter(date=today)
    seminar_place_id = request.GET.get('seminar_place', '')

    if seminar_place_id:
        seminar_list = seminar_list.filter(place=seminar_place_id)
        seminar_place_name = seminar_places.filter(id=seminar_place_id).first()
        lower_bound = (now - timedelta(minutes=40)).time()
        upper_bound = (now + timedelta(minutes=20)).time()

        matching_session = rdss.models.ConfigSeminarSession.objects.filter(
            session_end__gt=lower_bound,
            session_end__lt=upper_bound
        ).first()

        current_seminar = seminar_list.filter(session_from_config=matching_session).first()
        if seminar_list and current_seminar in seminar_list:
            # put current seminar to the default
            seminar_list = list(seminar_list)
            seminar_list.remove(current_seminar)
            seminar_list.insert(0, current_seminar)

    if request.method == "POST":
        idcard_no = request.POST['idcard_no']
        seminar_id = request.POST['seminar_id']
        seminar_obj = rdss.models.SeminarSlot.objects.get(id=seminar_id)
        student_obj, created = rdss.models.Student.objects.get_or_create(
            idcard_no=idcard_no
        )
        attendance_obj, created = rdss.models.StuAttendance.objects.get_or_create(
            student=student_obj,
            seminar=seminar_obj
        )
        student_obj = rdss.models.Student.objects.filter(idcard_no=idcard_no).annotate(
            points=Sum('attendance__points')).first()
        collect_pts_logger.info('{} attend {} {}'.format(idcard_no, seminar_obj.date, seminar_obj.session_from_config))

        # check if the student can get the daily seminar prize
        is_redeem, redeem_date, already_redeemed = _reach_seminar_daily_threshold(student_obj)
        redeem_target = f"{redeem_date} 說明會"
        if is_redeem:
            if already_redeemed:
                ui_message = {"type": "yellow", "msg": f"學號{student_obj.student_id} 已兌換 {redeem_target} 每日獎品"}
            else:
                ui_message = {"type": "green", "msg": f"學號{student_obj.student_id} 參加 {redeem_target}，可兌換每日獎品"}

        # maintain current seminar from post
        current_seminar = seminar_obj

    return render(request, 'admin/collect_points.html', locals())

@staff_member_required
def RedeemPrize(request):
    site_header = "OpenHouse 管理後台"
    site_title = "OpenHouse"
    title = "集點兌換"

    if request.method == "GET":
        idcard_no = request.GET.get('idcard_no', '')
        if idcard_no:
            student_obj = rdss.models.Student.objects.filter(idcard_no=idcard_no).annotate(
                points=Sum('attendance__points')).first()

            if student_obj:
                student_form = rdss.forms.StudentForm(instance=student_obj)
                redeem_form = rdss.forms.RedeemForm()

    if request.method == "POST":
        data = request.POST.copy()
        student_obj = rdss.models.Student.objects.filter(idcard_no=data['idcard_no']).first()
        redeem_obj = rdss.models.RedeemPrize.objects.create(
            student=student_obj
        )

        form = rdss.forms.StudentForm(data, instance=student_obj)
        if form.is_valid():
            form.save()
        else:
            ui_message = {"type": "error", "msg": "註冊失敗"}
        redeem_form = rdss.forms.RedeemForm(data, instance=redeem_obj)
        if redeem_form.is_valid():
            redeem_form.save()
            ui_message = {"type": "green", "msg": "儲存成功，已兌換{}，花費{}點".format(
                data['prize'], data['points'])}
            redeem_form = rdss.forms.RedeemForm()
        else:
            ui_message = {"type": "error", "msg": "註冊失敗"}

        student_form = rdss.forms.StudentForm(instance=student_obj)

    return render(request, 'admin/redeem_prize.html', locals())


@staff_member_required
def RegisterCard(request):
    site_header = "OpenHouse 管理後台"
    site_title = "OpenHouse"
    title = "學生證註冊"

    if request.method == "POST":
        data = request.POST.copy()
        instance = rdss.models.Student.objects.filter(idcard_no=data['idcard_no']).first()
        form = rdss.forms.StudentForm(data, instance=instance)
        if form.is_valid():
            form.save()
            ui_message = {"type": "green", "msg": "註冊成功"}
            collect_pts_logger.info('{} registered {} {}'.format(data['idcard_no'], data['student_id'],
                                                                 data['phone']))
        else:
            print(form.errors)
            ui_message = {"type": "red", "msg": "註冊失敗"}

    form = rdss.forms.StudentForm()
    return render(request, 'admin/reg_card.html', locals())


@staff_member_required
def SeminarAttendedStudent(request):
    
    seminars = rdss.models.SeminarSlot.objects.all()
    try:
        configs = rdss.models.RdssConfigs.objects.all()[0]
    except IndexError:
        return render(request, 'error.html', {'error_msg' : "活動設定尚未完成，請聯絡行政人員設定"})
    
    seminar_session_display = {
        "forenoon": "{}~{}".format(configs.session0_start, configs.session0_end),
        "noon": "{}~{}".format(configs.session1_start, configs.session1_end),
        "night1": "{}~{}".format(configs.session2_start, configs.session2_end),
        "night2": "{}~{}".format(configs.session3_start, configs.session3_end),
        "night3": "{}~{}".format(configs.session4_start, configs.session4_end),
        "extra": "補場",
        "jobfair": "就博會",
    }
    
    for ele in seminars:
        student_count = rdss.models.StuAttendance.objects.filter(seminar=ele).count()
        ele.time = seminar_session_display[ele.session]
        ele.student_count = student_count

    return render(request, 'admin/seminar_attended_student.html', locals())

@staff_member_required
def SeminarAttendedStudentDetail(request, seminar_id):
    try:
        seminar = rdss.models.SeminarSlot.objects.get(id=seminar_id)
    except rdss.models.SeminarSlot.DoesNotExist:
        return HttpResponse(status=404)
    
    attendances = rdss.models.StuAttendance.objects.filter(seminar=seminar)
    
    return render(request, 'admin/seminar_attended_student_detail.html', locals())

# Import Student Card Information from excel file
@staff_member_required
def ImportStudentCardInfo(request):

    if request.method == "POST":
        
        form = rdss.forms.ImportStudentCardInfoForm(request.POST, request.FILES)
        
        if form.is_valid():
            if not request.FILES["excel_file"].name.endswith('.xlsx'):
                success = False
                error_message = "只接受 .xlsx 副檔名"
                return render(request, 'admin/import_student_card_info.html', locals())


            try:
                ImportStudentCardID(request.FILES["excel_file"])
                success = True
            except IntegrityError as e:
                if e.args[0] == 1062:
                    success = False
                    error_message = "請確認是否有相同卡號，但是姓名或學號不同的資料"
            except Exception as ee:
                success = False
                error_message = f"{ee}"
            
    
    else:
        form = rdss.forms.ImportStudentCardInfoForm()

    return render(request, 'admin/import_student_card_info.html', locals())

@staff_member_required
def ClearStudentInfo(request):
    rdss.models.Student.objects.all().delete()
    success = True
    message = "刪除成功！"

    return render(request, 'admin/message.html', locals())

# ========================RDSS admin tools view=================
@staff_member_required
def bulk_add_jobfairslot(request):
    zones = rdss.models.ZoneCategories.objects.all()
    if request.method == 'POST':
        number = int(request.POST.get('number'))
        zone_id = int(request.POST.get('zone'))
        zone = rdss.models.ZoneCategories.objects.get(id=zone_id)
        max_serial_no = rdss.models.JobfairSlot.objects.all().last()
        max_serial_no = (int(max_serial_no.serial_no)) if max_serial_no else 0

        for i in range(1, number + 1):
            new_serial_no = max_serial_no + i
            rdss.models.JobfairSlot.objects.create(serial_no=str(new_serial_no), zone=zone)

        messages.success(request, f'Successfully added {number} new JobfairSlots of {zone}.')
        return redirect('/admin/rdss/jobfairslot/')

    return render(request, 'admin/bulk_add_jobfairslot.html', locals())

@staff_member_required
def sync_company_categories(request):
    try:
        company_categories = company.models.CompanyCategories.objects.all()
        for category in company_categories:
            rdss.models.CompanyCategories.objects.update_or_create(
                id=category.id,
                defaults={
                    'name': category.name,
                    'discount': category.discount,
                }
            )
        messages.success(request, f'Successfully synchronized company categories')
        return redirect('/admin/rdss/companycategories/')
    except Exception as e:
        messages.error(request, f'Failed to synchronize company categories: {e}')
        return redirect('/admin/rdss/companycategories/')

# ========================RDSS public view=================
def RDSSPublicIndex(request):
    # semantic ui control
    sidebar_ui = {'index': "active"}
    try:
        all_company = company.models.Company.objects.all()
        rdss_company = rdss.models.Signup.objects.all().order_by('cid')
        rdss_info = rdss.models.RdssInfo.objects.all()
        company_list = []
        for signup in rdss_company:
            com = all_company.get(cid=signup.cid)
            com.website = views_helper.change_website_start_with_http(com.website)
            company_list.append(com)
        # sorted bt company categories id
        company_list = sorted(company_list, key=lambda x: x.categories.id)

    except Exception as e:
        error_msg = f"error: {e}"
        return render(request, 'error.html', locals())
    return render(request, 'public/rdss_index.html', locals())


def SeminarPublic(request):
    # semantic ui control
    sidebar_ui = {'seminar': "active"}

    try:
        configs = rdss.models.RdssConfigs.objects.all()[0]
    except IndexError:
        return render(request, 'error.html', {'error_msg' : "活動設定尚未完成，請聯絡行政人員設定"})
    seminar_start_date = configs.seminar_start_date
    seminar_end_date = configs.seminar_end_date
    seminar_days = (seminar_end_date - seminar_start_date).days
    table_start_date = seminar_start_date
    rdss_seminar_info = rdss.models.RdssSeminarInfo.objects.all()
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
            forenoon_slot = rdss.models.SeminarSlot.objects.filter(date=today, session='forenoon').first()
            noon_slot = rdss.models.SeminarSlot.objects.filter(date=today, session='noon').first()
            night1_slot = rdss.models.SeminarSlot.objects.filter(date=today, session='night1').first()
            night2_slot = rdss.models.SeminarSlot.objects.filter(date=today, session='night2').first()
            night3_slot = rdss.models.SeminarSlot.objects.filter(date=today, session='night3').first()
            week_slot_info.append(
                {
                    'date': today,
                    'forenoon': '' if not forenoon_slot or not forenoon_slot.company else
                    {
                        'company': forenoon_slot.company.get_company_name(),
                        'place_color': forenoon_slot.place.css_color if forenoon_slot.place else None
                    },
                    'noon': '' if not noon_slot or not noon_slot.company else
                    {
                        'company': noon_slot.company.get_company_name(),
                        'place_color': noon_slot.place.css_color if noon_slot.place else None
                    },
                    'night1': '' if not night1_slot or not night1_slot.company else
                    {
                        'company': night1_slot.company.get_company_name(),
                        'place_color': night1_slot.place.css_color if night1_slot.place else None
                    },
                    'night2': '' if not night2_slot or not night2_slot.company else
                    {
                        'company': night2_slot.company.get_company_name(),
                        'place_color': night2_slot.place.css_color if night2_slot.place else None
                    },
                    'night3': '' if not night3_slot or not night3_slot.company else
                    {
                        'company': night3_slot.company.get_company_name(),
                        'place_color': night3_slot.place.css_color if night3_slot.place else None
                    },
                }
            )
        dates_in_week.append(week_slot_info)

    slot_colors = rdss.models.SlotColor.objects.all()
    return render(request, 'public/rdss_seminar.html', locals())


def JobfairPublic(request):
    # semantic ui control
    sidebar_ui = {'jobfair': "active"}

    place_map = rdss.models.Files.objects.filter(category='就博會攤位圖').first()
    slots = rdss.models.JobfairSlot.objects.all()
    rdss_jobfair_info = rdss.models.RdssJobfairInfo.objects.all()
    return render(request, 'public/rdss_jobfair.html', locals())


def OnlineJobfairPublic(request):
    # semantic ui control
    sidebar_ui = {'online_jobfair': "active"}

    place_map = rdss.models.Files.objects.filter(category='線上就博會攤位圖').first()
    slots = rdss.models.OnlineJobfairSlot.objects.all()
    rdss_online_jobfair_info = rdss.models.RdssOnlineJobfairInfo.objects.all()
    return render(request, 'public/rdss_online_jobfair.html', locals())


def QueryPoints(request):
    # semantic ui control
    sidebar_ui = {'query_points': "active"}

    if request.method == 'POST':
        data = request.POST.copy()
        student_id = data.get('student_id')
        cellphone = data.get('cellphone')
        student_obj = rdss.models.Student.objects.filter(student_id=student_id, phone=cellphone).first()
        records = rdss.models.StuAttendance.objects.filter(student=student_obj)
        redeems = rdss.models.RedeemPrize.objects.filter(student=student_obj)

    return render(request, 'public/rdss_querypts.html', locals())


def ListJobs(request):
    # semantic ui control
    sidebar_ui = {'list_jobs': "active"}

    categories = [category.name for category in rdss.models.CompanyCategories.objects.all()]
    companies = []
    category_filtered = request.GET.get('categories') if request.GET.get('categories') else None

    if category_filtered and category_filtered != 'all':
        if category_filtered not in categories:
            raise Http404("What are u looking for?")
        for signup in rdss.models.Signup.objects.all():
            try:
                target_category = company.models.CompanyCategories.objects.get(name=category_filtered)
                target_company = company.models.Company.objects.get(cid=signup.cid, categories=target_category)
                companies.append({
                    'cid': target_company.cid,
                    'logo': target_company.logo,
                    'name': target_company.name,
                    'category': target_company.categories.name,
                    'brief': replace_urls_and_emails(target_company.brief),
                    'address': target_company.address,
                    'phone': target_company.phone,
                    'website': views_helper.change_website_start_with_http(target_company.website),
                    'recruit_info': replace_urls_and_emails(target_company.recruit_info),
                    'recruit_url': replace_urls_and_emails(target_company.recruit_url),
                })
            except:
                pass
    else:
        for signup in rdss.models.Signup.objects.all():
            try:
                target_company = company.models.Company.objects.get(cid=signup.cid)
                companies.append({
                    'cid': target_company.cid,
                    'logo': target_company.logo,
                    'name': target_company.name,
                    'category': target_company.categories.name,
                    'brief': replace_urls_and_emails(target_company.brief),
                    'address': target_company.address,
                    'phone': target_company.phone,
                    'website': views_helper.change_website_start_with_http(target_company.website),
                    'recruit_info': replace_urls_and_emails(target_company.recruit_info),
                    'recruit_url': replace_urls_and_emails(target_company.recruit_url),
                })
            except:
                pass
    # if cid = 66666666, 77777777 exists, move these 2 companies to the head of the list
    for i, com in enumerate(companies):
        if com['cid'] == '66666666':
            companies.insert(0, companies.pop(i))
        if com['cid'] == '77777777':
            companies.insert(0, companies.pop(i))
    return render(request, 'public/rdss_jobs.html', locals())


def replace_urls_and_emails(original_str):
    urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', original_str)
    for url in urls:
        original_str = original_str.replace(url, '<a href="{}" target="_blank">連結</a>'.format(url))

    emails = re.findall(r'[\w\.-]+@[\w\.-]+(?:\.[\w]+)+', original_str, re.ASCII)
    for email in emails:
        original_str = original_str.replace(email, '<a href="mailto:{}" target="_blank">email</a>'.format(email))

    return '<span>' + original_str + '</span>'
