from django.contrib import admin
from rdss import models
import company.models
from django.conf.urls import url, include
import rdss.export

admin.AdminSite.site_header = "OpenHouse 管理後台"
admin.AdminSite.site_title = "OpenHouse"


# admin.AdminSite.index_template="admin/admin_index.html"


class SponsorshipInline(admin.TabularInline):
    model = models.Sponsorship
    extra = 0


class StuAttendanceInline(admin.TabularInline):
    model = models.StuAttendance
    extra = 0


class StuAttendanceAdmin(admin.ModelAdmin):
    list_display = ['seminar', 'get_company', 'get_student_id', 'get_student_name',]
    search_fields = ('student__student_id', 'student__name')


admin.site.register(models.StuAttendance, StuAttendanceAdmin)


@admin.register(models.Student)
class StudentAdmin(admin.ModelAdmin):
    inlines = (StuAttendanceInline,)
    search_fields = ('idcard_no' ,'name', 'student_id')
    list_display = ('idcard_no', 'student_id', 'name', 'phone')


@admin.register(models.RedeemPrize)
class RedeemAdmin(admin.ModelAdmin):
    list_display = ('student', 'prize', 'points', 'updated')


@admin.register(models.ECESeminar)
class ECESeminarAdmin(admin.ModelAdmin):
    list_display = ('seminar_name','ece_member_discount',)

@admin.register(models.CompanyCatogories)
class CompanyCategoriesAdmin(admin.ModelAdmin):
    list_display = ('name', 'discount')

@admin.register(models.ZoneCatogories)
class ZoneCatogoriesAdmin(admin.ModelAdmin):
    list_display = ('name', 'discount', 'display_categories')
    list_filter = ('category', )
    def display_categories(self, obj):
        return ', '.join(category.name for category in obj.category.all())

    display_categories.short_description = 'Categories'

@admin.register(models.SeminarSlot)
class SeminarSlotAdmin(admin.ModelAdmin):
    list_display = ('date', 'session', 'company', 'place')


@admin.register(models.SponsorItems)
class SponsorItemsAdmin(admin.ModelAdmin):
    inlines = (SponsorshipInline,)
    list_display = ('name', 'description', 'price', 'limit', 'current_amount')

    def current_amount(self, obj):
        return rdss.models.Sponsorship.objects.filter(item=obj).count()

    current_amount.short_description = '目前贊助數'


@admin.register(models.Signup)
class SignupAdmin(admin.ModelAdmin):
    list_display = ('cid', 'company_name', 'seminar', 'jobfair', 'career_tutor', 'visit', 'lecture', 'payment')
    inlines = (SponsorshipInline,)
    search_fields = ('cid',)

    def company_name(self, obj):
        # com = company.models.Company.objects.filter(cid=obj.cid).first()
        return obj.get_company_name()

    # define export URLs eg:...admin/rdss/signup/export
    def get_urls(self):
        urls = super(SignupAdmin, self).get_urls()
        my_urls = [
            url(r'^export/$', rdss.export.Export_Signup),
        ]
        return my_urls + urls
    
    # Custom search for company name
    def get_search_results(self, request, queryset, search_term):
        queryset, may_have_duplicates = super().get_search_results(
            request, queryset, search_term,
        )
        try:
            companies = company.models.Company.objects.filter(name__icontains=search_term)
            companies = company.models.Company.objects.filter(shortname__icontains=search_term)
        except ValueError:
            pass
        else:
            if(companies):
                for com in companies :
                    queryset |= self.model.objects.filter(cid=com.cid)
        return queryset, may_have_duplicates


@admin.register(models.Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('cid', 'name', 'category', 'hr_name', 'hr_phone', 'hr_mobile', 'hr_email')
    search_fields = ['cid',]

    # Custom search for company name
    def get_search_results(self, request, queryset, search_term):
        queryset, may_have_duplicates = super().get_search_results(
            request, queryset, search_term,
        )
        try:
            companies = company.models.Company.objects.filter(name__icontains=search_term)
            companies = company.models.Company.objects.filter(shortname__icontains=search_term)
        except ValueError:
            pass
        else:
            if(companies):
                for com in companies :
                    queryset |= self.model.objects.filter(cid=com.cid)
        return queryset, may_have_duplicates

    def get_urls(self):
        urls = super(CompanyAdmin, self).get_urls()
        my_urls = [
            url(r'^export/$', rdss.export.Export_Company),
        ]
        return my_urls + urls

    def category(self, obj):
        com = company.models.Company.objects.filter(cid=obj.cid).first()
        return com.category

    def hr_name(self, obj):
        com = company.models.Company.objects.filter(cid=obj.cid).first()
        return com.hr_name

    def hr_phone(self, obj):
        com = company.models.Company.objects.filter(cid=obj.cid).first()
        return com.hr_phone

    def hr_mobile(self, obj):
        com = company.models.Company.objects.filter(cid=obj.cid).first()
        return com.hr_mobile

    def hr_email(self, obj):
        com = company.models.Company.objects.filter(cid=obj.cid).first()
        return com.hr_email
    def name(self, obj):
        com = company.models.Company.objects.filter(cid=obj.cid).first()
        return com.name

    category.short_description = '類型'
    hr_name.short_description = '人資姓名'
    hr_phone.short_description = '人資電話'
    hr_mobile.short_description = '人資手機'
    hr_email.short_description = '人資Email'


@admin.register(models.SeminarOrder)
class SeminarOrderAdmin(admin.ModelAdmin):
    list_display = ("company", "time", "updated")


@admin.register(models.JobfairOrder)
class JobfairOrderAdmin(admin.ModelAdmin):
    list_display = ("company", "time", "updated")


@admin.register(models.RdssConfigs)
class RdssConfigsAdmin(admin.ModelAdmin):
    list_display = ("configs",)

    def configs(self, obj):
        return "活動設定"


@admin.register(models.CompanySurvey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ("company",)

    # define export URLs eg:...admin/rdss/signup/export
    def get_urls(self):
        urls = super(SurveyAdmin, self).get_urls()
        my_urls = [
            url(r'^export/$', rdss.export.ExportSurvey),
        ]
        return my_urls + urls


@admin.register(models.Files)
class RDSSFilesAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'upload_file', 'updated')


@admin.register(models.SlotColor)
class SlotColorAdmin(admin.ModelAdmin):
    list_display = ('place', 'css_color', 'place_info')


class SeminarParkingInline(admin.StackedInline):
    model = models.SeminarParking
    extra = 1
    max_num = 2


@admin.register(models.SeminarInfo)
class SeminarInfoAdmin(admin.ModelAdmin):
    inlines = [SeminarParkingInline]
    list_display = ('company', 'topic', 'speaker', 'speaker_title', 'contact',
                    'contact_email', 'contact_mobile', 'updated')


@admin.register(models.SeminarParking)
class SeminarParkingAdmin(admin.ModelAdmin):
    list_display = ('license_plate_number', 'info')


class JobfairParkingInline(admin.StackedInline):
    model = models.JobfairParking
    extra = 1
    max_num = 3


@admin.register(models.JobfairInfo)
class JobfairInfoAdmin(admin.ModelAdmin):
    inlines = [JobfairParkingInline]
    list_display = ('company', 'signname', 'meat_lunchbox', 'vege_lunchbox',
                    'contact_email', 'contact_mobile', 'updated')


@admin.register(models.JobfairParking)
class JobfairParkingAdmin(admin.ModelAdmin):
    list_display = ('license_plate_number', 'info')


@admin.register(models.RdssInfo)
class RdssInfoAdmin(admin.ModelAdmin):
    list_display = ('title',)

    def has_add_permission(self, request):
        count = rdss.models.RdssInfo.objects.all().count()
        if count == 0:
            return True
        return False


@admin.register(models.RdssCompanyInfo)
class RdssInfoAdmin(admin.ModelAdmin):
    list_display = ('title',)

    def has_add_permission(self, request):
        count = rdss.models.RdssCompanyInfo.objects.all().count()
        if count == 0:
            return True
        return False


@admin.register(models.RdssSeminarInfo)
class SeminarContentAdmin(admin.ModelAdmin):
    list_display = ('title',)

    def has_add_permission(self, request):
        count = rdss.models.RdssSeminarInfo.objects.all().count()
        if count == 0:
            return True
        return False


@admin.register(models.RdssJobfairInfo)
class JobfairContentAdmin(admin.ModelAdmin):
    list_display = ('title',)

    def has_add_permission(self, request):
        count = rdss.models.RdssJobfairInfo.objects.all().count()
        if count == 0:
            return True
        return False


# @admin.register(models.RdssOnlineJobfairInfo)
# class OnlineJobfairContentAdmin(admin.ModelAdmin):
#     list_display = ('title',)

#     def has_add_permission(self, request):
#         count = rdss.models.RdssOnlineJobfairInfo.objects.all().count()
#         if count == 0:
#             return True
#         return False


@admin.register(models.Sponsorship)
class SponsorshipAdmin(admin.ModelAdmin):
    list_display = ('company_id', 'item_id', 'updated',)
    list_filter = ('item_id',)


# Register your models here.
# admin.site.register(models.Sponsorship)
admin.site.register(models.JobfairSlot)
# admin.site.register(models.OnlineJobfairSlot)
