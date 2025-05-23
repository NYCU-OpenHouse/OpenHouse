from django.contrib import admin
from django.conf.urls import url
from django.db.models import F, Q
from .models import RecruitConfigs, RecruitSignup, JobfairSlot, JobfairInfo, SponsorItem, SponsorShip, \
    Files, RecruitConfigs, CompanySurvey, SeminarSlot, SlotColor, SeminarOrder, SeminarInfo, Student, \
    StuAttendance, SeminarInfoTemporary, SeminarParking, JobfairParking, \
    ECESeminar
from .models import JobfairInfoTemp
from .models import JobfairOrder, ExchangePrize
from company.models import Company
from recruit import export
import recruit.models as models

def _get_company_name_search_results(queryset, model, search_term):
    if search_term:
        company_list = Company.objects.filter(Q(name__icontains=search_term) | Q(shortname__icontains=search_term))
        for company in company_list:
            queryset |= model.objects.filter(cid=company.cid)
    return queryset

@admin.register(ExchangePrize)
class ExchangePrizeAdmin(admin.ModelAdmin):
    list_display = ['student', 'prize', 'points', 'updated']


class StuAttendanceInline(admin.TabularInline):
    model = StuAttendance
    extra = 0


@admin.register(StuAttendance)
class StuAttendanceAdmin(admin.ModelAdmin):
    list_display = ['seminar', 'get_company', 'get_student_id', 'get_student_name',]
    search_fields = ('student__student_id', 'student__name')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    inlines = (StuAttendanceInline,)
    search_fields = ('card_num' ,'name', 'student_id')
    list_display = ('card_num', 'student_id', 'name', 'phone')


class SponsorshipInline(admin.TabularInline):
    model = SponsorShip
    extra = 0

class ConfigSeminarSessionInline(admin.StackedInline):
    model = models.ConfigSeminarSession
    fields = ('session_start', 'session_end', 'qualification')
    extra = 0

class ConfigSeminarChoiceInline(admin.StackedInline):
    model = models.ConfigSeminarChoice
    fields = ('name', 'session_fee')
    extra = 0

@admin.register(RecruitConfigs)
class RecruitConfigAdmin(admin.ModelAdmin):
    list_display = ['title']
    inlines = [ConfigSeminarChoiceInline, ConfigSeminarSessionInline]

    def title(self, obj):
        return '活動設定'

@admin.register(ECESeminar)
class ECESeminarAdmin(admin.ModelAdmin):
    list_display = ('seminar_name', 'ece_member_discount')

@admin.register(models.CompanyCategories)
class CompanyCategoriesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'discount')
    # disable add button
    def has_add_permission(self, request):
        return False

    # disable delete button
    def has_delete_permission(self, request, obj=None):
        return False

    change_list_template = "admin/companycategories_change_list.html"

@admin.register(models.ZoneCategories)
class ZoneCategoriesAdmin(admin.ModelAdmin):
    list_display = ('name', 'discount', 'display_categories')
    list_filter = ('category', )
    def display_categories(self, obj):
        return ', '.join(category.name for category in obj.category.all())

    display_categories.short_description = 'Categories'

@admin.register(models.HistoryParticipation)
class HistoryParticipationAdmin(admin.ModelAdmin):
    fields = ('name', 'short_name')

@admin.register(RecruitSignup)
class RecruitSignupAdmin(admin.ModelAdmin):
    search_fields = ('cid', 'seminar', 'jobfair')
    list_display = ('cid', 'company_name', 'company_join_date', 'seminar', 'jobfair',
                    'company_visit', 'lecture', 'payment', 'company_other_ps')
    list_filter = ('seminar', 'jobfair', 'payment', 'first_participation', 'zone')
    inlines = (SponsorshipInline,)

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        queryset = _get_company_name_search_results(queryset, self.model, search_term)
        return queryset, use_distinct

    def company_name(self, obj):
        return obj.get_company_name()


@admin.register(SeminarSlot)
class SeminarSlotAdmin(admin.ModelAdmin):
    list_display = ('date', 'session_from_config', 'company', 'place')
    raw_id_fields = ("company",)


@admin.register(SeminarOrder)
class SeminarOrderAdmin(admin.ModelAdmin):
    list_display = ("company", "time", "updated")
    raw_id_fields = ("company",)


class SeminarParkingInline(admin.StackedInline):
    model = models.SeminarParking
    extra = 1
    max_num = 2


@admin.register(SeminarInfo)
class SeminarInfoAdmin(admin.ModelAdmin):
    inlines = [SeminarParkingInline]
    list_display = ('company', 'topic', 'speaker', 'speaker_title', 'contact',
                    'contact_email', 'contact_mobile', 'updated')


@admin.register(SeminarParking)
class SeminarParkingAdmin(admin.ModelAdmin):
    list_display = ('license_plate_number', 'info')


@admin.register(SeminarInfoTemporary)
class SeminarInfoTemporaryAdmin(admin.ModelAdmin):
    list_display = ('company', 'contact_email', 'contact_mobile', 'live', 'order', 'updated')
    actions = ['increase_priority_by_1', 'increase_priority_by_2', 'increase_priority_by_3', 'decrease_priority_by_1',
               'decrease_priority_by_2', 'decrease_priority_by_3']

    def increase_priority_by_1(self, request, queryset):
        for obj in queryset:
            obj.order = F('order') + 1 if obj.order < 32767 else 32767
            obj.save()
        self.message_user(request, '{}個廠商優先度被提升1'.format(len(queryset)))

    increase_priority_by_1.short_description = '優先度提升1'

    def increase_priority_by_2(self, request, queryset):
        for obj in queryset:
            obj.order = F('order') + 2 if obj.order < 32766 else 32767
            obj.save()
        self.message_user(request, '{}個廠商優先度被提升2'.format(len(queryset)))

    increase_priority_by_2.short_description = '優先度提升2'

    def increase_priority_by_3(self, request, queryset):
        for obj in queryset:
            obj.order = F('order') + 3 if obj.order < 32765 else 32767
            obj.save()
        self.message_user(request, '{}個廠商優先度被提升3'.format(len(queryset)))

    increase_priority_by_3.short_description = '優先度提升3'

    def decrease_priority_by_1(self, request, queryset):
        for obj in queryset:
            obj.order = F('order') - 1 if obj.order > 1 else 1
            obj.save()
        self.message_user(request, '{}個廠商優先度被降低1'.format(len(queryset)))

    decrease_priority_by_1.short_description = '優先度降低1'

    def decrease_priority_by_2(self, request, queryset):
        for obj in queryset:
            obj.order = F('order') - 2 if obj.order > 2 else 1
            obj.save()
        self.message_user(request, '{}個廠商優先度被降低2'.format(len(queryset)))

    decrease_priority_by_2.short_description = '優先度降低2'

    def decrease_priority_by_3(self, request, queryset):
        for obj in queryset:
            obj.order = F('order') - 3 if obj.order > 3 else 1
            obj.save()
        self.message_user(request, '{}個廠商優先度被降低3'.format(len(queryset)))

    decrease_priority_by_3.short_description = '優先度降低3'


@admin.register(SlotColor)
class SlotColorAdmin(admin.ModelAdmin):
    list_display = ('place', 'css_color', 'zone', 'place_info')


@admin.register(JobfairOrder)
class JobfairOrderAdmin(admin.ModelAdmin):
    list_display = ('company', 'time', "updated")
    raw_id_fields = ("company",)


@admin.register(JobfairSlot)
class JobfairSlotAdmin(admin.ModelAdmin):
    list_display = ('serial_no', 'zone', 'company', 'updated')
    zones = models.ZoneCategories.objects.all()
    change_list_template = "admin/jobfairslot_change_list.html"



class JobfairParkingInline(admin.StackedInline):
    model = models.JobfairParking
    extra = 1
    max_num = 3


@admin.register(JobfairInfo)
class JobfairInfoAdmin(admin.ModelAdmin):
    inlines = [JobfairParkingInline]
    list_display = ('company',)


@admin.register(JobfairParking)
class JobfairParkingAdmin(admin.ModelAdmin):
    list_display = ('license_plate_number', 'info')


@admin.register(JobfairInfoTemp)
class JobfairInfoTempAdmin(admin.ModelAdmin):
    list_display = ('company',)


@admin.register(SponsorItem)
class SponsorItemAdmin(admin.ModelAdmin):
    inlines = (SponsorshipInline,)
    list_display = ('name', 'description', 'price', 'number_limit', 'current_amount')

    def current_amount(self, obj):
        return SponsorShip.objects.filter(sponsor_item=obj).count()

    current_amount.short_description = '目前贊助數'


@admin.register(SponsorShip)
class SponsorShipAdmin(admin.ModelAdmin):
    pass


@admin.register(CompanySurvey)
class SurveyAdmin(admin.ModelAdmin):
    search_fields = ('cid', )
    list_display = ('cid', 'company_name')

    # define export URLs eg:...admin/recruit/signup/export
    def get_urls(self):
        urls = super(SurveyAdmin, self).get_urls()
        my_urls = [
            url(r'^export/$', export.ExportSurvey, name="recruit_survey_export"),
        ]
        return my_urls + urls

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        queryset = _get_company_name_search_results(queryset, self.model, search_term)
        return queryset, use_distinct


@admin.register(Files)
class RecruitFilesAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'upload_file', 'updated')


@admin.register(models.RecruitInfo)
class RecruitContentAdmin(admin.ModelAdmin):
    list_display = ('title',)

    def has_add_permission(self, request):
        count = models.RecruitInfo.objects.all().count()
        if count == 0:
            return True
        return False


@admin.register(models.RecruitCompanyInfo)
class RecruitCompanyContentAdmin(admin.ModelAdmin):
    list_display = ('title',)

    def has_add_permission(self, request):
        count = models.RecruitCompanyInfo.objects.all().count()
        if count == 0:
            return True
        return False


@admin.register(models.RecruitJobfairInfo)
class RecruitJobfairContentAdmin(admin.ModelAdmin):
    list_display = ('title',)

    def has_add_permission(self, request):
        count = models.RecruitJobfairInfo.objects.all().count()
        if count == 0:
            return True
        return False


@admin.register(models.RecruitSeminarInfo)
class RecruitSeminarContentAdmin(admin.ModelAdmin):
    list_display = ('title',)

    def has_add_permission(self, request):
        count = models.RecruitSeminarInfo.objects.all().count()
        if count == 0:
            return True
        return False


@admin.register(models.RecruitECESeminarInfo)
class RecruitECESeminarContentAdmin(admin.ModelAdmin):
    list_display = ('title',)

    def has_add_permission(self, request):
        count = models.RecruitECESeminarInfo.objects.all().count()
        if count == 0:
            return True
        return False


@admin.register(models.RedeemDailyPrize)
class RedeemDailyPrizeAdmin(admin.ModelAdmin):
    list_display = ('date', 'redeem', 'updated')
