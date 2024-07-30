from django.shortcuts import render, redirect
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
import company.models


@staff_member_required
def Export_Company(request):
    # Create the HttpResponse object with the appropriate Excel header.
    if request.user and request.user.is_authenticated:
        if not request.user.is_superuser:
            return HttpResponse(status=403)
    else:
        return HttpResponse(status=403)
    filename = "all_company_{}.xlsx".format(
        timezone.localtime(timezone.now()).strftime("%m%d-%H%M"))
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=' + filename

    company_list = list(company.models.Company.objects.all())

    fieldname_list = ['cid', 'name', 'english_name', 'shortname', 'categories', 'phone',
                      'postal_code', 'address', 'website',
                      'hr_name', 'hr_phone', 'hr_mobile', 'hr_email',
                      'hr2_name', 'hr2_phone', 'hr2_mobile', 'hr2_email', 'hr_ps',
                      'brief', 'recruit_info', 'receipt_title', 'receipt_code', 'receipt_postal_code',
                      'receipt_postal_address', 'receipt_contact_name', 'receipt_contact_phone',
                      'total_jobs_types', 'total_jobs',
                      'foreign_job_types', 'foreign_jobs', 'liberal_job_types', 'liberal_jobs']
    title_pairs = dict()
    for fieldname in fieldname_list:
        if fieldname == 'foreign_job_types':
            title_pairs[fieldname] = '外籍職缺種類'
        elif fieldname == 'foreign_jobs':
            title_pairs[fieldname] = '外籍職缺數量'
        elif fieldname == 'liberal_job_types':
            title_pairs[fieldname] = '文組職缺種類'
        elif fieldname == 'liberal_jobs':
            title_pairs[fieldname] = '文組職缺數量'
        elif fieldname == 'total_jobs_types':
            title_pairs[fieldname] = '職缺種類'
        elif fieldname == 'total_jobs':
            title_pairs[fieldname] = '職缺數量'
        else:
            title_pairs[fieldname] = company.models.Company._meta.get_field(fieldname).verbose_name

    workbook = xlsxwriter.Workbook(response)
    worksheet = workbook.add_worksheet()

    for index, fieldname in enumerate(fieldname_list):
        worksheet.write(0, index, title_pairs[fieldname])

    for row_count, company_obj in enumerate(company_list):
        # Query the related jobs for the company
        total_jobs = company.models.Job.objects.filter(cid=company_obj)
        foreign_jobs = total_jobs.filter(is_foreign=True)
        liberal_jobs = total_jobs.filter(is_liberal=True)
        
        # Count the unique job types and total job quantity
        foreign_job_types = foreign_jobs.values('title').distinct().count()
        liberal_job_types = liberal_jobs.values('title').distinct().count()
        foreign_jobs_quantity = foreign_jobs.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
        liberal_jobs_quantity = liberal_jobs.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
        total_jobs_types = total_jobs.values('title').distinct().count()
        total_jobs_quantity = total_jobs.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
        
        for col_count, fieldname in enumerate(fieldname_list):
            if fieldname == 'foreign_job_types':
                worksheet.write(row_count + 1, col_count, foreign_job_types)
            elif fieldname == 'foreign_jobs':
                worksheet.write(row_count + 1, col_count, foreign_jobs_quantity)
            elif fieldname == 'liberal_job_types':
                worksheet.write(row_count + 1, col_count, liberal_job_types)
            elif fieldname == 'liberal_jobs':
                worksheet.write(row_count + 1, col_count, liberal_jobs_quantity)
            elif fieldname == 'total_jobs_types':
                worksheet.write(row_count + 1, col_count, total_jobs_types)
            elif fieldname == 'total_jobs':
                worksheet.write(row_count + 1, col_count, total_jobs_quantity)
            elif fieldname == 'categories':
                worksheet.write(row_count + 1, col_count, company_obj.categories.name)
            else:
                worksheet.write(row_count + 1, col_count, getattr(company_obj, fieldname))

    workbook.close()
    return response
