from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.core import serializers
from django.forms.models import model_to_dict
from django.utils import timezone
from django.db.models import Count, Sum
from django.conf import settings
import xlsxwriter
import json
import datetime
import recruit.models
import company.models
import re


@staff_member_required
def ExportAll(request):
    # Create the HttpResponse object with the appropriate Excel header.
    if request.user and request.user.is_authenticated:
        if not request.user.is_superuser:
            return HttpResponse(status=403)
    else:
        return HttpResponse(status=403)
    filename = "recruit_export_{}.xlsx".format(timezone.localtime(timezone.now()).strftime("%m%d-%H%M"))
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=' + filename
    workbook = xlsxwriter.Workbook(response)

    # Company Basic Info
    signup_cid_list = [s.cid for s in recruit.models.RecruitSignup.objects.all()]
    company_list = list()
    for cid in signup_cid_list:
        company_list.append(
            company.models.Company.objects.filter(cid=cid).first())

    fieldname_list = ['cid', 'name', 'english_name', 'shortname', 'category', 'phone',
                      'postal_code', 'address', 'website',
                      'hr_name', 'hr_phone', 'hr_mobile', 'hr_email',
                      'hr2_name', 'hr2_phone', 'hr2_mobile', 'hr2_email', 'hr_ps',
                      'brief', 'recruit_info']
    # avoid 'can't subtract offset-naive and offset-aware datetimes'

    title_pairs = dict()
    for fieldname in fieldname_list:
        title_pairs[fieldname] = company.models.Company._meta.get_field(fieldname).verbose_name
    # add job related fields
    fieldname_list += [
        'foreign_job_types', 'foreign_jobs', 'liberal_job_types', 'liberal_jobs', 'total_job_types', 'total_jobs'
    ]
    title_pairs.update({
        'foreign_job_types': '外籍職缺種類',
        'foreign_jobs': '外籍職缺數量',
        'liberal_job_types': '文組職缺種類',
        'liberal_jobs': '文組職缺數量',
        'total_job_types': '總職缺種類',
        'total_jobs': '總職缺數量'
    })

    info_worksheet = workbook.add_worksheet("廠商資料")

    for index, fieldname in enumerate(fieldname_list):
        info_worksheet.write(0, index, title_pairs[fieldname])

    for row_count, company_obj in enumerate(company_list):
        jobs = company.models.Job.objects.filter(cid=company_obj)

        foreign_jobs = jobs.filter(is_foreign=True)
        liberal_jobs = jobs.filter(is_liberal=True)

        foreign_job_types = foreign_jobs.values('title').distinct().count()
        foreign_jobs_quantity = foreign_jobs.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
        liberal_job_types = liberal_jobs.values('title').distinct().count()
        liberal_jobs_quantity = liberal_jobs.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
        total_jobs_quantity = jobs.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
        total_job_types = jobs.values('title').distinct().count()

        for col_count, fieldname in enumerate(fieldname_list):
            if fieldname == 'foreign_job_types':
                info_worksheet.write(row_count + 1, col_count, foreign_job_types)
            elif fieldname == 'foreign_jobs':
                info_worksheet.write(row_count + 1, col_count, foreign_jobs_quantity)
            elif fieldname == 'liberal_job_types':
                info_worksheet.write(row_count + 1, col_count, liberal_job_types)
            elif fieldname == 'liberal_jobs':
                info_worksheet.write(row_count + 1, col_count, liberal_jobs_quantity)
            elif fieldname == 'total_job_types':
                info_worksheet.write(row_count + 1, col_count, total_job_types)
            elif fieldname == 'total_jobs':
                info_worksheet.write(row_count + 1, col_count, total_jobs_quantity)
            else:
                info_worksheet.write(row_count + 1, col_count, getattr(company_obj, fieldname))

     # ============= end of company basic info =============

    # Company Signup
    signups = recruit.models.RecruitSignup.objects.all()

    title_pairs = [
        {'fieldname': 'cid', 'title': '公司統一編號'},
        {'fieldname': 'shortname', 'title': '公司簡稱'},
        {'fieldname': 'first_participation', 'title': '首次參加'},
        {'fieldname': 'zone', 'title': '專區類別'},
        {'fieldname': 'history', 'title': '歷史參加調查'},
        {'fieldname': 'seminar', 'title': '實體說明會場次'},
        {'fieldname': 'seminar_ece', 'title': '實體ECE說明會'},
        # {'fieldname': 'seminar_online', 'title': '線上說明會場次'},
        {'fieldname': 'jobfair', 'title': '實體就博會攤位數'},
        # {'fieldname': 'jobfair_online', 'title': '線上就博會'},
        {'fieldname': 'company_visit', 'title': '提供企業參訪'},
        {'fieldname': 'career_tutor', 'title': '提供職場導師'},
        {'fieldname': 'lecture', 'title': '提供就業講座'},
        {'fieldname': 'payment', 'title': '是否繳費'},
        # {'fieldname': 'receipt_year', 'title': '收據年份'},
        {'fieldname': 'ps', 'title': '備註'},
    ]

    signup_worksheet = workbook.add_worksheet("廠商報名情況")

    for index, pair in enumerate(title_pairs):
        signup_worksheet.write(0, index, pair['title'])

    for row_count, signup in enumerate(signups):
        signup_dict = model_to_dict(signup)
        # join company info
        company_obj = company.models.Company.objects.get(
            cid=signup_dict['cid'])
        company_dict = model_to_dict(company_obj)
        for key, value in company_dict.items():
            signup_dict[key] = value
        for col_count, pairs in enumerate(title_pairs):
            if pairs['fieldname'] == 'seminar':
                signup_worksheet.write(row_count + 1, col_count,
                                       signup.get_seminar_display())
            elif pairs['fieldname'] == 'seminar_ece':
                signup_worksheet.write(row_count + 1, col_count,
                                       ', '.join(ece.seminar_name for ece in signup.seminar_ece.all()))
            elif pairs['fieldname'] == 'zone':
                zone_name_first_two_chars = signup.zone.name[:2]
                signup_worksheet.write(row_count + 1, col_count, zone_name_first_two_chars)
            elif pairs['fieldname'] == 'history':
                signup_worksheet.write(row_count + 1, col_count,
                                       ', '.join(h.short_name for h in signup.history.all()))
            # elif pairs['fieldname'] == 'seminar_online':
            #     signup_worksheet.write(row_count + 1, col_count,
            #                            signup.get_seminar_online_display())
            else:
                signup_worksheet.write(row_count + 1, col_count,
                                       signup_dict[pairs['fieldname']])

    #only export those signed up company receipt information 
    receipt_worksheet = workbook.add_worksheet("收據相關資訊")
    
    receipt_title_pairs = [
        {'fieldname': 'cid', 'title': '公司統一編號'},
        {'fieldname': 'shortname', 'title': '公司簡稱'},
        {'fieldname': 'english_name', 'title': '公司英文名稱'},
        {'fieldname': 'receipt_title', 'title': '公司收據抬頭'},
        {'fieldname': 'receipt_code', 'title': '公司收據統編'},
        {'fieldname': 'receipt_postal_code', 'title': '收據寄送郵遞區號'},
        {'fieldname': 'receipt_postal_address', 'title': '收據寄送地址'},
        {'fieldname': 'receipt_contact_name', 'title': '收據聯絡人姓名'},
        {'fieldname': 'receipt_contact_phone', 'title': '收據聯絡人公司電話'},
        # {'fieldname': 'receipt_year', 'title': '收據年份'},
    ]

    for index, pair in enumerate(receipt_title_pairs):
            receipt_worksheet.write(0, index, pair['title'])
            
    for row_count, signup in enumerate(signups):
        signup_dict = model_to_dict(signup)
        # join company info
        company_obj = company.models.Company.objects.get(
            cid=signup_dict['cid'])
        company_dict = model_to_dict(company_obj)
        for key, value in company_dict.items():
            signup_dict[key] = value
        for col_count, pairs in enumerate(receipt_title_pairs):
            receipt_worksheet.write(row_count + 1, col_count,
                                    signup_dict[pairs['fieldname']])


    # Sponsorships
    sponsor_items = recruit.models.SponsorItem.objects.all().annotate(num_sponsor=Count('sponsorship'))
    sponsorships_list = list()
    for c in signups:
        shortname = company.models.Company.objects.filter(cid=c.cid).first().shortname
        sponsorships = recruit.models.SponsorShip.objects.filter(company=c)
        counts = [recruit.models.SponsorShip.objects.filter(company=c, sponsor_item=item).count() for item in
                  sponsor_items]
        amount = 0
        for s in sponsorships:
            amount += s.sponsor_item.price
        sponsorships_list.append({
            "cid": c.cid,
            "counts": counts,
            "amount": amount,
            "shortname": shortname,
            "id": c.id,
        })
    spon_worksheet = workbook.add_worksheet("贊助")
    spon_worksheet.write(0, 0, "廠商/贊助品")
    spon_worksheet.write(1, 0, "目前數量/上限")
    spon_worksheet.write(0, len(sponsor_items) + 2, "贊助額")
    for index, item in enumerate(sponsor_items):
        spon_worksheet.write(0, index + 2, item.name)
        spon_worksheet.write(1, index + 2, "{}/{}".format(item.num_sponsor, item.number_limit))

    row_offset = 2
    for row_count, com in enumerate(sponsorships_list):
        spon_worksheet.write(row_count + row_offset, 0, com['shortname'])
        spon_worksheet.write(row_count + row_offset, 1, com['cid'])
        for col_count, count in enumerate(com['counts']):
            spon_worksheet.write(row_count + row_offset, col_count + 2, count)
        spon_worksheet.write(row_count + row_offset, len(com['counts']) + 2, com['amount'])

    # ece seminar information
    
    signups = recruit.models.RecruitSignup.objects.all()
    signups_dict = json.loads(serializers.serialize('json', signups))
    # join company info
    for signup in signups_dict:
        company_obj = company.models.Company.objects.get(
            cid=signup['fields']['cid'])
        company_dict = model_to_dict(company_obj)
        for key, value in company_dict.items():
            signup['fields'][key] = value
    
    signup_worksheet = workbook.add_worksheet("ece 廠商報名情況")
    
    ece = recruit.models.ECESeminar.objects.all()
    
    i = 0
    title_pairs = [
        {'fieldname': 'cid', 'title': '公司統一編號'},
        {'fieldname': 'shortname', 'title': '公司簡稱'},
    ]
    
    for index, pair in enumerate(title_pairs):
        signup_worksheet.write(0, i, pair['title'])
        i += 1
    
    for index, pair in enumerate(ece):
        signup_worksheet.write(0, i, pair.seminar_name)
        i += 1
    
    for row_count, signup in enumerate(signups_dict):
        for col_count, pairs in enumerate(title_pairs):
            signup_worksheet.write(row_count + 1, col_count,
                                   signup['fields'][pairs['fieldname']])
        print(signup['fields']['seminar_ece'])
        for ece in signup['fields']['seminar_ece']:
            signup_worksheet.write(row_count + 1, col_count + ece,
                                   "TRUE")
    
    workbook.close()
    return response


@staff_member_required
def export_seminar_info(request):
    if request.user and request.user.is_authenticated:
        if not request.user.is_superuser:
            return HttpResponse(status=403)
    else:
        return HttpResponse(status=403)
    filename = "recruit_seminar_info.xlsx"
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=' + filename
    workbook = xlsxwriter.Workbook(response)
    worksheet = workbook.add_worksheet("實體說明會資訊")

    fields = recruit.models.SeminarInfo._meta.get_fields()[2:-1]
    displacement = 0
    for index, field in enumerate(fields):
        worksheet.write(0, index + displacement, field.verbose_name)
        if field.verbose_name == '公司':
            displacement += 1
            worksheet.write(0, index + displacement, '企業統一編號')
    license_start_loc = len(fields)
    for index in range(2):
        worksheet.write(0, license_start_loc + index, '車牌號碼{}'.format(index + 1))
    company_list = recruit.models.SeminarInfo.objects.all()

    for i, info in enumerate(company_list):
        displacement = 0
        for j, field in enumerate(fields):
            if field.name != 'company' and field.name != 'updated':
                worksheet.write(i + 1, j + displacement, getattr(info, field.name))
            elif field.name == 'company':
                cid = getattr(getattr(info, field.name), 'cid')
                company_name = company.models.Company.objects.get(cid=cid).name
                worksheet.write(i + 1, j + displacement, company_name)
                displacement += 1
                worksheet.write(i + 1, j + displacement, cid)
        for index, lic in enumerate(recruit.models.SeminarParking.objects.filter(info=info)[:2]):
            worksheet.write(i + 1, license_start_loc + index, lic.license_plate_number)
    workbook.close()
    return response

@staff_member_required
def ExportJobs(request):
    if request.user and request.user.is_authenticated:
        if not request.user.is_superuser:
            return HttpResponse(status=403)
    else:
        return HttpResponse(status=403)

    filename = "recruit_jobs_{}.xlsx".format(
        timezone.localtime(timezone.now()).strftime("%m%d-%H%M"))
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=' + filename

    signup_cid_list = [s.cid for s in recruit.models.RecruitSignup.objects.all()]
    company_list = list()
    for cid in signup_cid_list:
        company_list.append(
            company.models.Company.objects.filter(cid=cid).first())

    fieldname_list = ['title', 'is_liberal', 'is_foreign', 
                    'description', 'quantity', 'note', 
                    'english_title', 'english_description','english_note']

    title_pairs = dict()
    for fieldname in fieldname_list:
        title_pairs[fieldname] = company.models.Job._meta.get_field(fieldname).verbose_name

    workbook = xlsxwriter.Workbook(response)
    
    for company_obj in company_list:
        worksheet = workbook.add_worksheet(company_obj.shortname)

        for index, fieldname in enumerate(fieldname_list):
            worksheet.write(0, index, title_pairs[fieldname])

        job_listings = company.models.Job.objects.filter(cid=company_obj)

        for row_count, job_obj in enumerate(job_listings):
            for col_count, fieldname in enumerate(fieldname_list):
                worksheet.write(row_count + 1, col_count, getattr(job_obj, fieldname))

    workbook.close()
    return response

@staff_member_required
def export_online_seminar_info(request):
    if request.user and request.user.is_authenticated:
        if not request.user.is_superuser:
            return HttpResponse(status=403)
    else:
        return HttpResponse(status=403)
    filename = "recruit_online_seminar_info.xlsx"
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=' + filename
    workbook = xlsxwriter.Workbook(response)
    worksheet = workbook.add_worksheet("線上說明會資訊")

    fields = recruit.models.OnlineSeminarInfo._meta.get_fields()[1:-1]
    displacement = 0
    for index, field in enumerate(fields):
        worksheet.write(0, index + displacement, field.verbose_name)
        if field.verbose_name == '公司':
            displacement += 1
            worksheet.write(0, index + displacement, '企業統一編號')
    company_list = recruit.models.OnlineSeminarInfo.objects.all()

    for i, info in enumerate(company_list):
        displacement = 0
        for j, field in enumerate(fields):
            if field.name != 'company' and field.name != 'updated':
                worksheet.write(i + 1, j + displacement, getattr(info, field.name))
            elif field.name == 'company':
                cid = getattr(getattr(info, field.name), 'cid')
                company_name = company.models.Company.objects.get(cid=cid).name
                worksheet.write(i + 1, j + displacement, company_name)
                displacement += 1
                worksheet.write(i + 1, j + displacement, cid)
    workbook.close()
    return response


@staff_member_required
def export_jobfair_info(request):
    if request.user and request.user.is_authenticated:
        if not request.user.is_superuser:
            return HttpResponse(status=403)
    else:
        return HttpResponse(status=403)
    filename = "recruit_jobfair_info.xlsx"
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=' + filename
    workbook = xlsxwriter.Workbook(response)
    worksheet = workbook.add_worksheet("實體就博會資訊")

    fields = recruit.models.JobfairInfo._meta.get_fields()[2:]
    displacement = 0
    for index, field in enumerate(fields):
        worksheet.write(0, index + displacement, field.verbose_name)
        if field.verbose_name == '公司':
            displacement += 1
            worksheet.write(0, index + displacement, '企業統一編號')
    license_start_loc = len(fields)
    for index in range(3):
        worksheet.write(0, license_start_loc + index, '車牌號碼{}'.format(index + 1))
    company_list = recruit.models.JobfairInfo.objects.all()

    for i, info in enumerate(company_list):
        displacement = 0
        for j, field in enumerate(fields):
            if field.name != 'company' and field.name != 'updated':
                worksheet.write(i + 1, j + displacement, getattr(info, field.name))
            elif field.name == 'company':
                cid = getattr(getattr(info, field.name), 'cid')
                company_name = company.models.Company.objects.get(cid=cid).name
                worksheet.write(i + 1, j + displacement, company_name)
                displacement += 1
                worksheet.write(i + 1, j + displacement, cid)
        for index, lic in enumerate(recruit.models.JobfairParking.objects.filter(info=info)[:3]):
            worksheet.write(i + 1, license_start_loc + index, lic.license_plate_number)
    workbook.close()
    return response


@staff_member_required
def ExportSurvey(request):
    if request.user and request.user.is_authenticated:
        if not request.user.is_superuser:
            return HttpResponse(status=403)
    else:
        return HttpResponse(status=403)
    # Create the HttpResponse object with the appropriate Excel header.
    filename = "recruit_survey_{}.xlsx".format(timezone.localtime(timezone.now()).strftime("%m%d-%H%M"))
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=' + filename
    workbook = xlsxwriter.Workbook(response)

    survey_worksheet = workbook.add_worksheet("廠商滿意度問卷")
    survey_worksheet.write(0, 0, "公司簡稱")
    survey_worksheet.write(0, 1, "公司統一編號")
    # start from index 1 because I don't want id field
    fields = recruit.models.CompanySurvey._meta.get_fields()[1:]
    for index, field in enumerate(fields):
        survey_worksheet.write(0, index + 2, field.verbose_name)

    survey_list = recruit.models.CompanySurvey.objects.all()
    for row_count, survey in enumerate(survey_list):
        # find company short name by cid
        shortname = company.models.Company.objects.filter(cid=survey.cid).first().shortname
        survey_worksheet.write(row_count + 1, 0, shortname)
        survey_worksheet.write(row_count + 1, 1, survey.cid)
        # export timestamp cause problem, TODO:FIX the fields[:-1] to fields
        for col_count, field in enumerate(fields[:-1]):
            survey_worksheet.write(row_count + 1, col_count + 2, getattr(survey, field.name))

    workbook.close()
    return response


@staff_member_required
def ExportActivityInfo(request):
    # Create the HttpResponse object with the appropriate Excel header.
    if request.user and request.user.is_authenticated:
        if not request.user.is_superuser:
            return HttpResponse(status=403)
    else:
        return HttpResponse(status=403)
    filename = "recruit_activity_info_{}.xlsx".format(timezone.localtime(timezone.now()).strftime("%m%d-%H%M"))
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=' + filename
    workbook = xlsxwriter.Workbook(response)
    worksheet = workbook.add_worksheet("實體說明會資訊")
    worksheet.write(0, 0, "廠商")
    # Ignore id and cid which is index 0 and 1
    fields = recruit.models.SeminarInfo._meta.get_fields()[2:]
    for index, field in enumerate(fields):
        worksheet.write(0, index + 1, field.verbose_name)

    seminar_info_list = recruit.models.SeminarInfo.objects.all()
    for row_count, info in enumerate(seminar_info_list):
        worksheet.write(row_count + 1, 0, info.company.get_company_name())
        for col_count, field in enumerate(fields):
            try:
                worksheet.write(row_count + 1, col_count + 1, getattr(info, field.name))
            except TypeError as e:
                # xlsxwriter do not accept django timzeone aware time, so use
                # except, to write string
                worksheet.write(row_count + 1, col_count + 1, info.updated.strftime("%Y-%m-%d %H:%M:%S"))

    worksheet = workbook.add_worksheet("線上說明會資訊")
    worksheet.write(0, 0, "廠商")
    # Ignore id and cid which is index 0 and 1
    fields = recruit.models.OnlineSeminarInfo._meta.get_fields()[2:]
    for index, field in enumerate(fields):
        worksheet.write(0, index + 1, field.verbose_name)

    seminar_online_info_list = recruit.models.OnlineSeminarInfo.objects.all()
    for row_count, info in enumerate(seminar_online_info_list):
        worksheet.write(row_count + 1, 0, info.company.get_company_name())
        for col_count, field in enumerate(fields):
            try:
                worksheet.write(row_count + 1, col_count + 1, getattr(info, field.name))
            except TypeError as e:
                # xlsxwriter do not accept django timzeone aware time, so use
                # except, to write string
                worksheet.write(row_count + 1, col_count + 1, info.updated.strftime("%Y-%m-%d %H:%M:%S"))

    worksheet = workbook.add_worksheet("實體就博會資訊")
    worksheet.write(0, 0, "廠商")
    # ignore id and cid which is index 0 and 1
    fields = recruit.models.JobfairInfo._meta.get_fields()[2:]
    for index, field in enumerate(fields):
        worksheet.write(0, index + 1, field.verbose_name)

    jobfair_into_list = recruit.models.JobfairInfo.objects.all()
    for row_count, info in enumerate(jobfair_into_list):
        worksheet.write(row_count + 1, 0, info.company.get_company_name())
        for col_count, field in enumerate(fields):
            try:
                worksheet.write(row_count + 1, col_count + 1, getattr(info, field.name))
            except TypeError as e:
                # same as above
                worksheet.write(row_count + 1, col_count + 1, info.updated.strftime("%Y-%m-%d %H:%M:%S"))

    workbook.close()
    return response


@staff_member_required
def ExportAdFormat(request):
    if request.user and request.user.is_authenticated:
        if not request.user.is_superuser:
            return HttpResponse(status=403)
    else:
        return HttpResponse(status=403)
    all_company = company.models.Company.objects.all()
    recruit_company = recruit.models.RecruitSignup.objects.all()
    company_list = []
    for c in recruit_company:
        target_company = all_company.get(cid=c.cid)
        company_list.append({
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
    company_list.sort(key=lambda item: item['category'])

    return render(request, 'admin/export_ad.html', locals())


def replace_urls_and_emails(original_str):
    urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', original_str)
    for url in urls:
        original_str = original_str.replace(url, '<a href="{}" target="_blank">連結</a>'.format(url))

    emails = re.findall(r'[\w\.-]+@[\w\.-]+(?:\.[\w]+)+', original_str, re.ASCII)
    for email in emails:
        original_str = original_str.replace(email, '<a href="mailto:{}" target="_blank">email</a>'.format(email))

    return '<span>' + original_str + '</span>'


def PayInfo(request):
    with open('static/data/payinfo.doc', 'rb') as pay:
        response = HttpResponse(pay.read())
        response['content_type'] = 'application/pdf'
        response['Content-Disposition'] = 'attachment;filename=payinfo.doc'
    return response

@staff_member_required
def ExportPointsInfo(request):

    filename = "recruit_points_info_{}.xlsx".format(timezone.localtime(timezone.now()).strftime("%m%d-%H%M"))
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=' + filename
    workbook = xlsxwriter.Workbook(response)
    worksheet = workbook.add_worksheet("春徵集點總覽")
    
    student_list = recruit.models.Student.objects.annotate(
                points=Sum('attendance__points')).order_by('-points')
    
    fields = recruit.models.Student._meta.get_fields()[3:8]
    
    for index, field in enumerate(fields):
        worksheet.write(0, index, field.verbose_name)
    worksheet.write(0, index, "累積點數")
    
    for row_count, info in enumerate(student_list):
        col_count = 0
        for col_count, field in enumerate(fields):
            worksheet.write(row_count + 1, col_count , getattr(info, field.name))
        if getattr(info, "points") is None:
            worksheet.write(row_count + 1, col_count, 0)
        else:
            worksheet.write(row_count + 1, col_count, getattr(info, "points"))
            

    workbook.close()
    return response
