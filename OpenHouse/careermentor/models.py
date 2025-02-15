from django.db import models
from company import models as company
from django.utils import timezone
from company.models import CompanyCategories


class Mentor(models.Model):
    MENTOR_CAT = (
        ('職場導師', '職場導師'),
        ('職涯教練', '職涯教練'),
        ('職涯講座', '職涯講座'),
    )
    ATTEND_MODE = (
        ('線上及實體','線上及實體'),
        ('僅限線上','僅限線上'),
        ('僅限實體','僅限實體'),
    )
    
    id = models.AutoField(primary_key=True)
    company = models.CharField(u'廠商', max_length=100)
    cid = models.CharField(u'公司統一編號', max_length=8, default='', blank=True)
    category = models.CharField(u'類型', max_length=10, choices=MENTOR_CAT)
    title = models.CharField(u'標題', max_length=100)
    abstract = models.TextField(u'大綱')
    signup_deadline = models.DateField(u'報名截止日期', help_text='報名時間到當日23:59截止', default=timezone.now)
    date = models.DateField(u'日期')
    start_time = models.TimeField(u'開始時間')
    end_time = models.TimeField(u'結束時間')
    set_attend_mode = models.CharField(u'設定參加方式', max_length=20, default='線上及實體', choices=ATTEND_MODE)
    set_meal = models.BooleanField(u'提供餐點', default=True)
    mentor = models.CharField(u'導師', max_length=100, default='', blank=True)
    mentor_brief = models.TextField(u'導師介紹')
    mentor_title = models.CharField(u'導師稱謂', max_length=100, default='', blank=True)
    mentor_email = models.EmailField(u'導師Email', max_length=254, default='', blank=True)
    mode = models.CharField(u'進行方式', max_length=100, default='', blank=True)
    place = models.CharField(u'地點', max_length=100)
    limit = models.IntegerField(u'人數限制', help_text='0表不限')
    remark = models.CharField(u'備註', max_length=100, default='', blank=True)
    updated = models.DateTimeField(u'更新時間', auto_now=True)

    class Meta:
        managed = True
        verbose_name = u"企業職場導師/職涯教練"
        verbose_name_plural = u"企業職場導師/職涯教練"
        ordering = ['-date', 'start_time']

    def __str__(self):
        return "{} / {} {}~{}".format(self.company, self.date, self.start_time, self.end_time)


class Signup(models.Model):
    ATTEND_CAT = (
        ('實體', '實體(Onsite)'),
        ('線上', '線上(Online)'),
    )
    MEAL_CATEGORY = (
        ('不提供餐點','不提供餐點(No Meal)'),
        ('無','不需要(No Need)'),
        ('葷', '葷(Meat)'),
        ('素','素(Vegetarian)'),
    )
    
    id = models.AutoField(primary_key=True)
    mentor = models.ForeignKey(Mentor, to_field='id',
                               verbose_name=u'場次/編號',
                               on_delete=models.CASCADE)
    name = models.CharField(u'姓名(Name)', max_length=64)
    student_id = models.CharField(u'學號(Student ID)', max_length=20)
    dep = models.CharField(u'系所/年級(Department and Grade)', max_length=16)
    phone = models.CharField(u'手機(Cellphone)', max_length=20,
                             help_text='格式：0987654321')
    email = models.EmailField(u'Email', max_length=64)
    time_available = models.CharField(u'場次時段內可以的時間(Available Time)', max_length=100, default='', blank=True)
    question = models.CharField(u'諮詢的內容(Enquiry)', max_length=100, default='')
    remark = models.CharField(u'備註(Remark)', max_length=100, default='', blank=True)
    cv_en = models.FileField(u'CV upload', upload_to='career_mentor', blank=True, null=True,
                             help_text="Optional, Better to have")
    cv_zh = models.FileField(u'履歷(中文)上傳', upload_to='career_mentor', blank=True, null=True,
                             help_text="非必要，能讓導師事先了解情況")
    other = models.FileField(u'Other / 其它資料上傳', upload_to='career_mentor', blank=True, null=True)
    updated = models.DateTimeField(u'更新時間', auto_now=True)
    preferred_categories = models.ManyToManyField(
        CompanyCategories,
        verbose_name=u'感興趣的企業類別(可複選)',
        blank=True
    )

    class Meta:
        managed = True
        verbose_name = u"學生登記"
        verbose_name_plural = u"學生登記"
