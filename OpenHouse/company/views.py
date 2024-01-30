from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from company.forms import CompanyCreationForm, CompanyEditForm, CompanyPasswordResetForm
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from .models import Company, ChineseFundedCompany, Job
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import SetPasswordForm
from company.forms import CompanyCreationForm, CompanyEditForm, ItemModelFormSet, JobUploadForm
import rdss.models
import recruit.models
import company.models
from oauth2_provider.decorators import protected_resource
from oauth.models import CustomAccessToken
from django.http import Http404
from openpyxl import load_workbook


# Create your views here.

@login_required(login_url='/company/login/')
def CompanyIndex(request):
    # semantic ui control
    menu_ui = {'index': "active"}

    # rdss files
    rdss_file_list = rdss.models.Files.objects.all().order_by('-updated')
    recruit_file_list = recruit.models.Files.objects.all().order_by('-updated')
    return render(request, 'company_index.html', locals())


@login_required(login_url='/company/login/')
def CompanyInfo(request):
    # semantic ui control
    menu_ui = {'info': "active"}

    company_info = company.models.Company.objects.get(cid=request.user.cid)
    jobs = company.models.Job.objects.filter(cid=request.user.id)
    return render(request, 'company_info.html', locals())


def CompanyCreation(request):
    submit_btn_name = "創建帳號"
    if request.POST:
        form = CompanyCreationForm(request.POST, request.FILES)
        try:
            ChineseFundedCompany.objects.get(cid=request.POST['cid'])
            error_display = True
            error_msg = "此統編已被政府列為中資企業，若有註冊需求，歡迎來信詢求協助!"
            return render(request, 'company_create_form.html', locals())
        except ChineseFundedCompany.DoesNotExist:
            pass
        if form.is_valid():
            form.save()
            user = authenticate(username=form.clean_cid(), password=form.clean_password2())
            login(request, user)
            messages.success(request, '公司帳號創建成功！請至編輯頁最下方新增公司招募職缺')
            return redirect(CompanyEdit)
        else:
            error_display = True
            error_msg = form.errors
            return render(request, 'company_create_form.html', locals())
    form = CompanyCreationForm()
    return render(request, 'company_create_form.html', locals())


@login_required(login_url='/company/login/')
def CompanyEdit(request):

    submit_btn_name = "確認修改"
    if request.user and request.user.is_authenticated:
        user = request.user
    else:
        user = None
        
    company_info = company.models.Company.objects.get(cid=request.user.cid)
    jobs = Job.objects.filter(cid=request.user.id)

    if request.POST:
        form = CompanyEditForm(request.POST, request.FILES, instance=user)

        if form.is_valid():
            if user and (form.data["cid"] != user.cid or form.data["category"] != user.category):
                if not user.is_staff:
                    # only staff can change cid & category
                    form = CompanyEditForm(instance=user)
                    job_formset = ItemModelFormSet(instance=user)
                    job_formset.extra = 1 if job_formset.queryset.count() < 1 else 0

            user = form.save()
            job_formset = ItemModelFormSet(request.POST, instance=user)
            job_upload_form = JobUploadForm(request.POST, request.FILES)
            if job_formset.is_valid():
                job_formset.save()
            else:
                print(job_formset.errors)
                messages.error(request, '「職缺列表」填入資料有誤，請重新修改公司資料')
                return render(request, 'company_edit_form.html', locals())
            
            if job_upload_form.is_valid():
                try:
                    wb = load_workbook(job_upload_form.cleaned_data['file'])
                    ws = wb.active
                    for row in ws.iter_rows(min_row=2):
                        job = Job()
                        job.cid = user
                        job.name = row[0].value
                        job.number = row[1].value
                        job.save()
                except Exception as e:
                    print(e)
                    messages.error(request, '填入資料有誤，請重新修改公司資料')
                    return render(request, 'company_edit_form.html', locals())
            else:
                print(job_upload_form.errors)
                messages.error(request, '「職缺上傳檔案」有誤，請重新修改公司資料')
                return render(request, 'company_edit_form.html', locals())

            # messages.success(request, _("User '{0}' created.").format(user))
            return redirect(CompanyInfo)
        else:
            messages.error(request, '「公司資料」填入資料有誤，請重新修改公司資料')
            return render(request, 'company_edit_form.html', locals())
    else:
        form = CompanyEditForm(instance=user)
        job_formset = ItemModelFormSet(instance=user)
        job_formset.extra = 1 if job_formset.queryset.count() < 1 else 0
        job_upload_form = JobUploadForm()

    
    if (len(jobs) == 0):
        messages.info(request, '目前沒有招募職缺，請新增公司招募職缺')    
    if (company_info.category == '其他'):
        print(company_info.category)
        messages.error(request, '目前公司類別為其他，請至公司主要營業項目修改公司類別')

    return render(request, 'company_edit_form.html', locals())


def CompanyLogin(request):
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
            next_url = request.GET.get('next')
            if user.is_staff:
                if next_url == None:
                    return redirect('/admin/')
                else:
                    return redirect(next_url)
            else:
                if next_url == None:
                    return redirect('/company/')
                else:
                    return redirect(next_url)
        else:
            error_display = True
            error_msg = "帳號或密碼錯誤"

    return render(request, 'login.html', locals())


def CompanyLogout(request):
    logout(request)
    return redirect('/company/login/')


def forget_password(request):
    send = None
    if request.method == 'POST':
        data = request.POST.copy()
        data['email'] = "dummy@e.mail"
        form = CompanyPasswordResetForm(data)
        if form.is_valid():
            form.save(request=request)
            company_obj = company.models.Company.objects.get(cid=form.cleaned_data.get('user'))
            return render(request, 'notify_password_reset.html', locals())
    else:
        form = CompanyPasswordResetForm()
    return render(request, 'forget_password.html', {'form': form, 'send': send})


def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = Company.objects.get(pk=uid)
    except(TypeError):
        user = None

    # the link is valid
    if user is not None and default_token_generator.check_token(user, token):
        validlink = True
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                return redirect('/company/login/')
        else:
            form = SetPasswordForm(user)
            return render(request, 'password_reset_confirm.html', {'form': form})

    # the link is not valid
    else:
        validlink = False
    return redirect('/')


def ResetPassword(request):
    user = Company.objects.get(cid=request.user.cid)
    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            return redirect(CompanyInfo)
    form = SetPasswordForm(user)
    return render(request, 'password_reset_confirm.html', {'form': form})

@protected_resource()
def get_company_id(request):

    access_token = CustomAccessToken.objects.get(token=request.META.get('HTTP_AUTHORIZATION').split(' ')[1])

    data = {
        "company_id": access_token.user.cid,
    }
    return JsonResponse(data)

@staff_member_required
def regitered_chinese_funded_company(request):
    
    registered_chinese_funded_company = []
    
    companies = Company.objects.all()
    
    for company in companies:
        if len(ChineseFundedCompany.objects.filter(cid=company.cid)) == 1:
            registered_chinese_funded_company.append(company)
    
    
    return render(request, 'admin/registered_chinese_funded_company.html', locals())

def CompanyDetail(request, companyId):
    """
    Function displaying specific company info to public
    """
    company_info = Company.objects.get(cid=companyId)
    id = company_info.id
    jobs = company.models.Job.objects.filter(cid=id)

    return render(request, 'company_detail.html', locals())
