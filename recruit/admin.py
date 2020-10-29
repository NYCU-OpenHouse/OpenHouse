from django.contrib import admin
from django.conf.urls import url
from django.db.models import F
from .models import RecruitConfigs, RecruitSignup, JobfairSlot, JobfairInfo, SponsorItem, SponsorShip, \
    Files, RecruitConfigs, CompanySurvey, Company, SeminarSlot, SlotColor, SeminarOrder, SeminarInfo, Student, \
    StuAttendance, SeminarInfoTemporary, SeminarParking, JobfairParking
from .models import JobfairInfoTemp
from .models import JobfairOrder, ExchangePrize
from company.models import Company
from recruit import export
import recruit.models as models


@admin.register(ExchangePrize)
class ExchangePrizeAdmin(admin.ModelAdmin):
    list_display = ['student', 'prize', 'points']


class SponsorshipInline(admin.TabularInline):
    model = SponsorShip
    extra = 0


@admin.register(RecruitConfigs)
class RecruitConfigAdmin(admin.ModelAdmin):
    list_display = ['title']

    def title(self, obj):
        return '活動設定'


class StuAttendanceInline(admin.TabularInline):
    model = StuAttendance
    extra = 0


@admin.register(StuAttendance)
class StuAttendanceAdmin(admin.ModelAdmin):
    list_display = ['seminar']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    inlines = (StuAttendanceInline,)
    list_display = ('card_num', 'student_id', 'name', 'phone')


@admin.register(RecruitSignup)
class RecruitSignupAdmin(admin.ModelAdmin):
    search_fields = ('cid', 'seminar',)
    list_display = ('cid', 'company_name', 'seminar', 'jobfair', 'career_tutor', 'company_visit', 'lecture', 'payment')
    list_filter = ('seminar', 'career_tutor', 'company_visit', 'lecture', 'payment',)
    inlines = (SponsorshipInline,)

    # custom search the company name field in other db
    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super(RecruitSignupAdmin, self).get_search_results(request, queryset, search_term)

        company_list = Company.objects.filter(name__icontains=search_term)
        company_list |= Company.objects.filter(shortname__icontains=search_term)
        for company in company_list:
            queryset |= self.model.objects.filter(cid=company.cid)
        return queryset, use_distinct

    def company_name(self, obj):
        return obj.get_company_name()


@admin.register(SeminarSlot)
class SeminarSlotAdmin(admin.ModelAdmin):
    list_display = ('date', 'session', 'company', 'place')
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
    list_display = ('place', 'css_color', 'place_info')


@admin.register(JobfairOrder)
class JobfairOrderAdmin(admin.ModelAdmin):
    list_display = ('company', 'time', "updated")
    raw_id_fields = ("company",)


@admin.register(JobfairSlot)
class JobfairSlotAdmin(admin.ModelAdmin):
    list_display = ('serial_no', 'category', 'company', 'updated')


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
    list_display = ("company",)

    # define export URLs eg:...admin/recruit/signup/export
    def get_urls(self):
        urls = super(SurveyAdmin, self).get_urls()
        my_urls = [
            url(r'^export/$', export.ExportSurvey, name="recruit_survey_export"),
        ]
        return my_urls + urls


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
