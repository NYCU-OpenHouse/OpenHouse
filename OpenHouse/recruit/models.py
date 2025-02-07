from django.db import models
from django.db.models import Q
from django.core.validators import RegexValidator, MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from django.utils import timezone
import datetime
import company.models


def validate_license_plate_number(string):
    validators = [
        RegexValidator(regex='^[0-9A-Z]{2,4}-[0-9A-Z]{2,4}$', message='車牌格式為：2至4個數字或大寫英文符號-2至4個數字或大寫英文符號')
    ]
    err = None
    for validator in validators:
        try:
            validator(string)
            return string
        except ValidationError as e:
            err = e
    raise err

CATEGORYS = (
    (u'半導體', u'半導體'),
    (u'消費電子', u'消費電子'),
    (u'網路通訊', u'網路通訊'),
    (u'光電光學', u'光電光學'),
    (u'資訊軟體', u'資訊軟體'),
    (u'集團', u'集團'),
    (u'人力銀行', u'人力銀行'),
    (u'新創', u'新創'),
    (u'生科醫療', u'生科醫療'),
    (u'金融/保險/不動產', u'金融/保險/不動產'),
    (u'出版影音/藝術、娛樂及休閒服務業', u'出版影音/藝術、娛樂及休閒服務業'),
    (u'醫療保健及社會工作服務業', u'醫療保健及社會工作服務業'),
    (u'公家單位', u'公家單位'),
    (u'財團/社團/行政法人', u'財團/社團/行政法人'),
    (u'住宿/餐飲業', u'住宿/餐飲業'),
    (u'批發及零售/運輸及倉儲業', u'批發及零售/運輸及倉儲業'),
    (u'電力及燃氣供應業', u'電力及燃氣供應業'),
    (u'傳統製造業', u'傳統製造業'),
    (u'其他', u'其他'),
)

class CompanyCategories(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(u'公司類別名稱', max_length=50)
    discount = models.BooleanField(u'公家機關優惠', default=False)

    def __str__(self):
        return u'{}'.format(self.name)

    class Meta:
        managed = True
        verbose_name = u'公司類別設定'
        verbose_name_plural = u'公司類別設定'

class ZoneCategories(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(u'專區名稱', max_length=20)
    discount = models.IntegerField(u'就博攤位第一攤減免優惠', default=0)
    category = models.ManyToManyField('CompanyCategories', verbose_name=u'公司類別', blank=True)
    
    def __str__(self):
        return u'{}'.format(self.name)

    class Meta:
        managed = True
        verbose_name = u'專區設定'
        verbose_name_plural = u'專區設定'

class HistoryParticipation(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(u'過往參加活動名稱', max_length=30)
    short_name = models.CharField(u'過往參加活動簡稱', max_length=10, default="", help_text="請填寫簡稱，用於匯出資訊")

    def __str__(self):
        return u'{}'.format(self.name)

    class Meta:
        managed = True
        verbose_name = u'過往參加活動調查選項設定'
        verbose_name_plural = u'過往參加活動調查選項設定'


class RecruitConfigs(models.Model):
    id = models.AutoField(primary_key=True)
    register_start = models.DateTimeField(u'廠商註冊開始時間')
    register_end = models.DateTimeField(u'廠商註冊結束時間')
    recruit_signup_start = models.DateTimeField(u'校徵報名開始時間')
    recruit_signup_end = models.DateTimeField(u'校徵報名結束時間')

    survey_start = models.DateTimeField(u'滿意度問卷開始填答')
    survey_end = models.DateTimeField(u'滿意度問卷結束填答')

    # 說明會相關
    seminar_start_date = models.DateField(u'說明會開始日期', default=datetime.date.today)
    seminar_end_date = models.DateField(u'說明會結束日期', default=datetime.date.today)
    seminar_info_deadline = models.DateTimeField(u'說明會資訊截止填寫時間', default=timezone.now)

    # ECE說明會相關
    seminar_ece_start_date = models.DateField(u'ECE說明會開始日期', default=datetime.date.today)
    seminar_ece_end_date = models.DateField(u'ECE說明會結束日期', default=datetime.date.today)
    # 費用
    session_ece_fee = models.IntegerField(u'ECE說明會_費用', default=0)

    # 就博會相關
    jobfair_date = models.DateField(u'就博會日期', default=datetime.date.today)
    jobfair_start = models.TimeField(u'就博會開始時間', default='00:00')
    jobfair_end = models.TimeField(u'就博會結束時間', default='00:00')
    jobfair_place = models.CharField(u'就博會地點', max_length=150, default="")
    jobfair_info_deadline = models.DateTimeField(u'就博會資訊截止填寫時間', default=timezone.now)
    JOBFAIR_FOOD_CHOICES = (
        ('lunch_box', u'餐盒(蛋奶素)'),
        ('bento', u'便當(葷素)')
    )
    jobfair_food = models.CharField(u'就業博覽會餐點', max_length=10, choices=JOBFAIR_FOOD_CHOICES, default='餐盒(蛋奶素)')
    jobfair_food_info = RichTextField(u'餐點注意事項', max_length=128, blank=True, null=True)
    # 費用
    jobfair_booth_fee = models.IntegerField(u'就博會攤位費用(每攤)', default=0)

    seminar_btn_start = models.DateField(u'說明會選位按鈕開啟日期', null=True)
    seminar_btn_end = models.DateField(u'說明會選位按鈕關閉日期', null=True)
    seminar_btn_enable_time = models.TimeField(u'說明會按鈕每日開啟時間', default="8:00", help_text="按鈕將於每日此時間開啟")
    seminar_btn_disable_time = models.TimeField(u'說明會按鈕每日關閉時間', default="18:00", help_text="按鈕將於每日此時間關閉")
    jobfair_btn_start = models.DateField(u'就博會選位按鈕開啟日期', null=True)
    jobfair_btn_end = models.DateField(u'就博會選位按鈕關閉日期', null=True)
    jobfair_btn_enable_time = models.TimeField(u'就博會按鈕每日開啟時間', default="8:00", help_text="按鈕將於每日此時間開啟")
    jobfair_btn_disable_time = models.TimeField(u'就博會按鈕每日關閉時間', default="18:00", help_text="按鈕將於每日此時間關閉")

    class Meta:
        managed = True
        verbose_name = u'1. 春季徵才活動設定'
        verbose_name_plural = u'1. 春季徵才活動設定'


class ECESeminar(models.Model):
    id = models.AutoField(primary_key=True)
    seminar_name = models.CharField(u'ECE說明會名稱', max_length=50)
    ece_member_discount = models.BooleanField(u'電機資源產學聯盟優惠', default=False)

    def __str__(self):
        return u'{}'.format(self.seminar_name)

    class Meta:
        managed = True
        verbose_name = u'3. ECE說明會設定'
        verbose_name_plural = u'3. ECE說明會設定'

class RecruitSignup(models.Model):
    SEMINAR_CHOICES = (
        (u'none', u'不參加說明會'),
        (u'attend', u'參加說明會'),
    )

    id = models.AutoField(primary_key=True)
    cid = models.CharField(u'公司統一編號', max_length=8, unique=True)
    zone = models.ForeignKey('ZoneCategories', verbose_name=u'專區類別', on_delete=models.CASCADE, null=True)
    history = models.ManyToManyField('HistoryParticipation', verbose_name=u'歷史參加調查', blank=True)
    first_participation = models.BooleanField(u'首次參加', default=False)
    seminar = models.CharField(u'說明會場次', choices=SEMINAR_CHOICES, max_length=15, default='none', blank=True)
    seminar_type = models.ForeignKey('ConfigSeminarChoice', verbose_name=u'說明會場次類型', on_delete=models.CASCADE, default=1)
    seminar_ece = models.ManyToManyField('ECESeminar', verbose_name=u'ECE說明會場次', blank=True)
    jobfair = models.IntegerField(u'徵才展示會攤位數量', default=0, validators=[MinValueValidator(0)])
    career_tutor = models.BooleanField(u'諮詢服務', default=False)
    company_visit = models.BooleanField(u'企業參訪', default=False)
    lecture = models.BooleanField(u'就職講座', default=False)
    payment = models.BooleanField(u'完成付款', default=False)
    ps = models.TextField(u'備註', blank=True, null=True)
    added = models.TimeField(u'報名時間', auto_now_add=True)
    updated = models.TimeField(u'更新時間', auto_now=True)

    def __str__(self):
        try:
            com = company.models.Company.objects.get(cid=self.cid)
        except:
            return "資料庫不同步，請連絡資訊組"
        return com.shortname
    
    def clean(self):
        if  self.cid != '77777777' and self.jobfair > 6:
            raise ValidationError('企業攤位範圍為6攤')

    def get_company_name(self):
        com = company.models.Company.objects.filter(cid=self.cid).first()
        return "資料庫不同步，請連絡資訊組" if com is None else com.shortname
    
    def company_join_date(self):
        com = company.models.Company.objects.filter(cid=self.cid).first()
        if com:
            return com.date_join
        else:
            return None

    def company_other_ps(self):
        com = company.models.Company.objects.filter(cid=self.cid).first()
        if com:
            return com.other_ps
        else:
            return None

    def get_company(self):
        com = company.models.Company.objects.filter(cid=self.cid).first()
        return "資料庫不同步，請連絡資訊組" if com is None else com

    class Meta:
        managed = True
        verbose_name = u'4. 活動報名情況'
        verbose_name_plural = u'4. 活動報名情況'

class ConfigSeminarChoice(models.Model):
    id = models.AutoField(primary_key=True)
    config = models.ForeignKey(
        RecruitConfigs, on_delete=models.CASCADE, related_name='config_seminar_choice'
    )
    name = models.CharField(u'說明會場次名稱', max_length=30, help_text="例如：上午場、下午場、晚場")
    session_fee = models.IntegerField(u'說明會場次_費用', default=0)

    class Meta:
        managed = True
        # TODO: Remove self defined db table name
        db_table = 'config_seminar_choice'

        verbose_name = u"說明會場次類型＆費用設定"
        verbose_name_plural = u"說明會場次類型＆費用設定"

    def __str__(self):
        return self.name

    def get_session_fee(self):
        return self.session_fee


class ConfigSeminarSession(models.Model):
    id = models.AutoField(primary_key=True)
    config = models.ForeignKey(
        RecruitConfigs, on_delete=models.CASCADE, related_name='config_seminar_session'
    )
    session_start = models.TimeField(u'說明會場次_開始時間', default='00:00')
    session_end = models.TimeField(u'說明會場次_結束時間', default='00:00')
    qualification = models.ForeignKey(
        ConfigSeminarChoice,
        verbose_name="說明會種類",
        on_delete=models.CASCADE,
        related_name='seminar_session',
        null=True
    )

    class Meta:
        managed = True
        # TODO: Remove self defined db table name
        db_table = 'config_seminar_session'

        verbose_name = u"說明會場次時間設定"
        verbose_name_plural = u"說明會場次時間設定"

    def __str__(self):
        return f"s_{self.session_start.strftime('%H%M')}" \
               f"_{self.session_end.strftime('%H%M')}"
    
    def get_display_name(self):
        return f"{self.session_start.strftime('%H:%M')} - {self.session_end.strftime('%H:%M')}"

    def clean(self):
        delta = datetime.datetime.combine(datetime.date.today(), self.session_end) - \
                datetime.datetime.combine(datetime.date.today(), self.session_start)
        if delta <= datetime.timedelta(minutes=30):
            raise ValidationError("開始時間與結束時間的間隔必須大於 30 分鐘")
    
        if not (datetime.time(6, 0, 0) <= self.session_start <= datetime.time(21, 0, 0)):
            raise ValidationError("開始時間必須在 6:00 至 21:00 之間")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class Files(models.Model):
    FILE_CAT = (
        ('企畫書', '企畫書'),
        ('報名說明書', '報名說明書'),
        ('選位相關', '選位相關'),
        ('就博會攤位圖', '就博會攤位圖'),
        ('就博會攤位圖-新', '就博會攤位圖-新'),
        ('線上就博會攤位圖', '線上就博會攤位圖'),
        ('繳費資訊', '繳費資訊'),
        ('其它', '其它'),
    )
    id = models.AutoField(primary_key=True)
    title = models.CharField(u'標題', max_length=30)
    category = models.CharField(u'類型', max_length=10, choices=FILE_CAT)
    upload_file = models.FileField(u'上傳檔案',
                                   upload_to='rdss_files', null=False)
    updated = models.DateTimeField(u'更新時間', auto_now=True)

    class Meta:
        verbose_name = u"活動檔案"
        verbose_name_plural = u"活動檔案"

class JobfairSlot(models.Model):
    id = models.AutoField(primary_key=True)
    serial_no = models.CharField(u'攤位編號', max_length=10)
    zone = models.ForeignKey('ZoneCategories', verbose_name=u'專區類別', on_delete=models.CASCADE, null=True)
    company = models.ForeignKey('RecruitSignup', to_field='cid',
                                verbose_name=u'公司',
                                on_delete=models.CASCADE, blank=True, null=True)
    updated = models.DateTimeField(u'更新時間', auto_now=True)

    class Meta:
        managed = True
        verbose_name = u'就博會攤位'
        verbose_name_plural = u'就博會攤位'

    def __str__(self):
        return self.serial_no

# 線上就博會攤位
class OnlineJobfairSlot(models.Model):
    id = models.AutoField(primary_key=True)
    serial_no = models.CharField(u'攤位編號', max_length=10)
    category = models.CharField(u'類別', max_length=37, choices=CATEGORYS)
    company = models.ForeignKey('RecruitSignup', to_field='cid',
                                verbose_name=u'公司',
                                limit_choices_to={'jobfair_online': True},
                                on_delete=models.CASCADE, blank=True, null=True)
    updated = models.DateTimeField(u'更新時間', auto_now=True)

    class Meta:
        managed = True
        verbose_name = u"線上就博會攤位"
        verbose_name_plural = u"線上就博會攤位"

    def __str__(self):
        return self.serial_no


class SeminarSlot(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateField(u'日期', default=datetime.date.today)
    session_from_config = models.ForeignKey(
        "ConfigSeminarSession",
        on_delete=models.CASCADE,
        verbose_name="時段(new)",
        related_name="seminar_slots",
        help_text="於活動設定中指定時段及對應價格",
        null=True,
        blank=True,
    )
    company = models.ForeignKey('RecruitSignup', to_field='cid',
                                   verbose_name=u'公司',
                                   on_delete=models.CASCADE, null=True, blank=True, unique=False)
    place = models.ForeignKey('SlotColor', verbose_name=u'場地', on_delete=models.CASCADE, default=1)
    points = models.SmallIntegerField(u'集點點數', default=1)
    updated = models.DateTimeField(u'更新時間', auto_now=True)
    session = models.CharField(u'時段(棄用、勿填)', max_length=10, null=True, blank=True)

    class Meta:
        managed = True
        verbose_name = u"說明會場次"
        verbose_name_plural = u"說明會場次"

    def __str__(self):
        return '{} {}'.format(self.date, self.session)

# 線上說明會場次
class OnlineSeminarSlot(models.Model):
    # (value in db, display name)
    SESSIONS = (
        ("noon1", "中午場1"),
        ("noon2", "中午場2"),
        ("evening1", "晚場1"),
        ("evening2", "晚場2"),
        ("evening3", "晚場3"),
    )
    id = models.AutoField(primary_key=True)
    date = models.DateField(u'日期', default=datetime.date.today)
    session = models.CharField(u'時段', max_length=10, choices=SESSIONS)
    company = models.OneToOneField('RecruitSignup', to_field='cid',
                                   verbose_name=u'公司',
                                   on_delete=models.CASCADE, null=True, blank=True)
    points = models.SmallIntegerField(u'集點點數', default=1)
    updated = models.DateTimeField(u'更新時間', auto_now=True)

    class Meta:
        managed = True
        verbose_name = u"線上說明會場次"
        verbose_name_plural = u"線上說明會場次"

    def __str__(self):
        return '{} {}'.format(self.date, self.session)


class SeminarOrder(models.Model):
    id = models.AutoField(primary_key=True)
    time = models.DateTimeField(u'選位開始時間')
    company = models.OneToOneField('RecruitSignup', to_field='cid',
                                   verbose_name=u'公司',
                                   limit_choices_to=~Q(seminar='none'),
                                   on_delete=models.CASCADE)
    updated = models.DateTimeField(u'更新時間', auto_now=True)

    class Meta:
        managed = True
        verbose_name = u"說明會選位順序"
        verbose_name_plural = u"說明會選位順序"

# 線上說明會選位順序
class OnlineSeminarOrder(models.Model):
    id = models.AutoField(primary_key=True)
    time = models.DateTimeField(u'選位開始時間')
    company = models.OneToOneField('RecruitSignup', to_field='cid',
                                   verbose_name=u'公司',
                                   limit_choices_to=~Q(seminar_online=''),
                                   on_delete=models.CASCADE, null=True, blank=True)
    updated = models.DateTimeField(u'更新時間', auto_now=True)

    class Meta:
        managed = True
        verbose_name = u"線上說明會選位順序"
        verbose_name_plural = u"線上說明會選位順序"


class JobfairOrder(models.Model):
    id = models.AutoField(primary_key=True)
    time = models.DateTimeField(u'選位開始時間')
    company = models.OneToOneField(RecruitSignup, to_field='cid',
                                   verbose_name=u'公司',
                                   limit_choices_to=~Q(jobfair=0),
                                   on_delete=models.CASCADE)
    updated = models.DateTimeField(u'更新時間', auto_now=True)

    class Meta:
        managed = True
        verbose_name = u"就博會選位順序"
        verbose_name_plural = u"就博會選位順序"


class JobfairInfo(models.Model):
    id = models.AutoField(primary_key=True)
    company = models.OneToOneField(RecruitSignup, verbose_name=u'公司', on_delete=models.CASCADE)
    sign_name = models.CharField(u'攤位招牌名稱', max_length=20)
    sign_eng_name = models.CharField(u'攤位招牌英文名稱', max_length=50, help_text="請填寫英文名稱, 限制50字元內", default="")
    disable_proofread = models.BooleanField(u'無需校對', default=False)
    contact_person = models.CharField(u'聯絡人', max_length=10)
    contact_mobile = models.CharField(u'聯絡人手機', max_length=32)
    contact_email = models.EmailField(u'聯絡人Email', max_length=128)
    packing_tickets = models.IntegerField(u'停車證數量', default=0, blank=True, null=True)
    PARKING_CHOICES = (
        ('ticket', u'當日索取紙本停車抵用券'),
        ('register', u'企業事先登記A車車牌號碼')
    )
    parking_type = models.CharField(u'停車方式', max_length=20, choices=PARKING_CHOICES, null=True, blank=True)
    parking_tickets = models.IntegerField(u'停車證數量', default=0, blank=True, null=True)
    job_number = models.SmallIntegerField(u'職缺人數', default=0)

    lunch_box = models.SmallIntegerField(u'餐盒數量', default=0, help_text="餐盒預設為蛋奶素", blank=True, null=True)
    meat_lunchbox = models.SmallIntegerField(u'葷食餐點數量', default=0, blank=True, null=True)
    vege_lunchbox = models.SmallIntegerField(u'素食餐點', default=0, blank=True, null=True)

    power_req = models.CharField(u'用電需求', max_length=128, blank=True, null=True)
    long_table = models.IntegerField(u'長桌', default=2, blank=True, null=True)
    chair = models.IntegerField(u'椅子', default=5, blank=True, null=True)
    doily = models.IntegerField(u'紅桌巾', default=1, blank=True, null=True)
    flag_pole_socket = models.IntegerField(u'旗桿座組', default=0, blank=True, null=True)
    searchlight = models.IntegerField(u'攤位頂部白光探照燈', default=0, blank=True, null=True)
    ps = models.CharField(u'備註', max_length=128, blank=True, null=True)

    class Meta:
        managed = True
        verbose_name = u'就博會資訊'
        verbose_name_plural = u'就博會資訊'


class JobfairParking(models.Model):
    id = models.AutoField(primary_key=True)
    license_plate_number = models.CharField(u'車牌號碼', max_length=8, validators=[validate_license_plate_number])
    info = models.ForeignKey(JobfairInfo, verbose_name=u'公司', on_delete=models.CASCADE)

    def __str__(self):
        return self.license_plate_number

    class Meta:
        verbose_name = u"就博會車牌號碼"
        verbose_name_plural = u"就博會車牌號碼"


class JobfairInfoTemp(models.Model):
    id = models.AutoField(primary_key=True)
    company = models.OneToOneField(RecruitSignup, verbose_name=u'公司', on_delete=models.CASCADE)
    video = models.CharField(u'影片', max_length=100, blank=True, null=True)
    content = RichTextUploadingField(u'招募內容')
    updated_time = models.DateTimeField(u'更新時間', auto_now=True)

    class Meta:
        managed = True
        verbose_name = u'就博會資訊(線上暫時)'
        verbose_name_plural = u'就博會資訊(線上暫時)'


class SeminarInfo(models.Model):
    id = models.AutoField(primary_key=True)
    company = models.OneToOneField(RecruitSignup, to_field='cid',
                                   verbose_name=u'公司',
                                   on_delete=models.CASCADE)
    topic = models.CharField(u'說明會主題', max_length=30)
    speaker = models.CharField(u'主講人', max_length=30)
    speaker_title = models.CharField(u'主講人稱謂', max_length=30)
    speaker_email = models.EmailField(u'主講人Email', max_length=254, null=True, blank=True)
    raffle_prize = models.CharField(u'抽獎獎品', max_length=254,
                                    null=True, blank=True)
    raffle_prize_amount = models.SmallIntegerField(u'抽獎獎品數量', default=0)
    qa_prize = models.CharField(u'QA獎獎品', max_length=254, null=True, blank=True)
    qa_prize_amount = models.SmallIntegerField(u'QA獎獎品數量', default=0)
    attend_prize = models.CharField(u'參加獎獎品', max_length=254,
                                    null=True, blank=True)
    attend_prize_amount = models.SmallIntegerField(u'參加獎獎品數量', default=0)
    contact = models.CharField(u'聯絡人', max_length=30)
    contact_mobile = models.CharField(u'聯絡人手機', max_length=16)
    contact_email = models.EmailField(u'聯絡人Email', max_length=254)
    job_number = models.SmallIntegerField(u'職缺人數', default=0)
    hr_food = models.CharField(u'人資餐點', max_length=30, null=True, blank=True,
                               help_text=" 提供免費2份餐點與飲水給企業人資或講者，如需素食或特殊飲食請於本欄備註說明")
    ps = models.TextField(u'其它需求', null=True, blank=True)
    updated = models.DateTimeField(u'更新時間', auto_now=True)

    class Meta:
        managed = True
        verbose_name = u"說明會資訊"
        verbose_name_plural = u"說明會資訊"

class SeminarParking(models.Model):
    id = models.AutoField(primary_key=True)
    license_plate_number = models.CharField(u'車牌號碼', max_length=8, validators=[validate_license_plate_number])
    info = models.ForeignKey(SeminarInfo, verbose_name=u'公司', on_delete=models.CASCADE)

    def __str__(self):
        return self.license_plate_number

    class Meta:
        verbose_name = u"說明會車牌號碼"
        verbose_name_plural = u"說明會車牌號碼"


class OnlineSeminarInfo(models.Model):
    id = models.AutoField(primary_key=True)
    company = models.OneToOneField(RecruitSignup, to_field='cid',
                                   verbose_name=u'公司',
                                   on_delete=models.CASCADE)
    topic = models.CharField(u'說明會主題', max_length=30)
    speaker = models.CharField(u'主講人', max_length=30)
    speaker_title = models.CharField(u'主講人稱謂', max_length=30)
    speaker_email = models.EmailField(u'主講人Email', max_length=254, null=True, blank=True)
    raffle_prize = models.CharField(u'抽獎獎品', max_length=254,
                                    null=True, blank=True)
    raffle_prize_amount = models.SmallIntegerField(u'抽獎獎品數量', default=0)
    qa_prize = models.CharField(u'QA獎獎品', max_length=254, null=True, blank=True)
    qa_prize_amount = models.SmallIntegerField(u'QA獎獎品數量', default=0)
    attend_prize = models.CharField(u'參加獎獎品', max_length=254,
                                    null=True, blank=True)
    attend_prize_amount = models.SmallIntegerField(u'參加獎獎品數量', default=0)
    contact = models.CharField(u'聯絡人', max_length=30)
    contact_mobile = models.CharField(u'聯絡人手機', max_length=16)
    contact_email = models.EmailField(u'聯絡人Email', max_length=254)
    job_number = models.SmallIntegerField(u'職缺人數', default=0)
    ps = models.TextField(u'其它需求', null=True, blank=True)
    updated = models.DateTimeField(u'更新時間', auto_now=True)

    class Meta:
        managed = True
        verbose_name = u"線上說明會資訊"
        verbose_name_plural = u"線上說明會資訊"


class SeminarInfoTemporary(models.Model):
    id = models.AutoField(primary_key=True)
    company = models.OneToOneField(RecruitSignup, to_field='cid',
                                   verbose_name=u'公司',
                                   on_delete=models.CASCADE)
    contact_mobile = models.CharField(u'聯絡電話', max_length=16, null=True, blank=True)
    contact_email = models.EmailField(u'聯絡Email', max_length=254, null=True, blank=True)
    updated = models.DateTimeField(u'更新時間', auto_now=True)

    live = models.BooleanField(u'直播', default=False)
    video = models.CharField(u'影片', max_length=100, null=True, blank=True,
                             help_text="請複製youtube影片網址")
    intro = models.TextField(u'說明會簡介', max_length=260)
    order = models.PositiveSmallIntegerField(u'順序', default=1, help_text='數字愈大放在愈前面')

    class Meta:
        managed = True
        ordering = ['-live', '-order']
        verbose_name = u"說明會資訊(線上暫時)"
        verbose_name_plural = u"說明會資訊(線上暫時)"


class SponsorItem(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(u'贊助品名稱', max_length=20, unique=True)
    description = models.CharField(u'贊助品說明', max_length=100)
    spec = models.CharField(u'規格', blank=True, null=True, max_length=100)
    ps = models.CharField(u'備註', blank=True, null=True, max_length=100)
    price = models.IntegerField(u'價格')
    number_limit = models.IntegerField(u'數量限制')
    pic = models.ImageField(u'贊助品預覽圖', upload_to='recruit_sponsor_item', null=True)
    sponsors = models.ManyToManyField(RecruitSignup, through='SponsorShip')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = u'7. 贊助品'
        verbose_name_plural = u'7. 贊助品'


class SponsorShip(models.Model):
    id = models.AutoField(primary_key=True)
    company = models.ForeignKey(RecruitSignup, to_field='cid', on_delete=models.CASCADE)
    sponsor_item = models.ForeignKey(SponsorItem, to_field='name', on_delete=models.CASCADE)
    updated = models.DateTimeField(u'更新時間', auto_now=True)

    class Meta:
        verbose_name = u'8. 贊助情況'
        verbose_name_plural = u'8. 贊助情況'
        unique_together = ('company', 'sponsor_item')


class CompanySurvey(models.Model):
    RATING = (
        (u'非常滿意', u'非常滿意'),
        (u'滿意', u'滿意'),
        (u'普通', u'普通'),
        (u'不滿意', u'不滿意'),
        (u'非常不滿意', u'非常不滿意'),
    )
    YES_NO_CHOICES = [
        ('yes', '是'),
        ('no', '否'),
    ]

    id = models.AutoField(primary_key=True)
    # basic info
    cid = models.CharField(u'公司統一編號', unique=True, max_length=8, null=False)
    company = models.CharField(u'企業名稱(中文)', max_length=50)
    company_eng = models.CharField(u'企業名稱(英文)(選填)', max_length=50, null=True, blank=True)
    submiter_name = models.CharField(u'填寫人姓名', max_length=20)
    submiter_phone = models.CharField(u'填寫人電話', max_length=20)
    submiter_email = models.CharField(u'填寫人Email', max_length=50)
    SIZE = (
        (u'1~100人', u'1~100人'),
        (u'101~500人', u'101~500人'),
        (u'500~1000人', u'500~1000人'),
        (u'1001~5000人', u'1001~5000人'),
        (u'5000~10000人', u'5000~10000人'),
        (u'10000~20000人', u'10000~20000人'),
        (u'30000人以上', u'30000人以上'),
    )
    company_size = models.CharField(u'貴企業規模', max_length=20, choices=SIZE)
    nycu_employees = models.IntegerField(u'本校校友人數', default=0)
    categories = models.ForeignKey('CompanyCategories', verbose_name=u'企業類別', on_delete=models.SET_NULL, null=True)

    # oversea recruit info
    os_serve = models.CharField(
        u'境外生參與活動',
        max_length=3,
        choices=YES_NO_CHOICES,
    )
    os_seminar = models.CharField(
        u'境外生說明會',
        max_length=3,
        choices=YES_NO_CHOICES,
    )
    os_for_ftime = models.IntegerField(u'外籍生(母語非中文)正職人數', default=0)
    os_osc_ftime = models.IntegerField(u'僑生正職人數', default=0)
    os_cn_ftime = models.IntegerField(u'陸生正職人數', default=0)
    os_for_intern = models.IntegerField(u'外籍生(母語非中文)實習人數', default=0)
    os_osc_intern = models.IntegerField(u'僑生實習人數', default=0)
    os_cn_intern = models.IntegerField(u'陸生實習人數', default=0)

    # application process
    APP_PROCESS_CHOICES = (
        ('literal','Hand over your CV to the HR personnel at the booth. (將協助引導學生至公司攤位)'),
        ('online', 'Upload your CV to the recruitment website. (請留下應徵網址)'),
        ('others', '其他')
    )
    os_app_process = models.CharField(u'應徵方式 ', max_length=50, choices=APP_PROCESS_CHOICES, null=True)
    os_app_cv_url = models.CharField(u'網址', max_length=64, blank=True, null=True, default='')
    os_app_other = models.CharField(u'其他', max_length=30, blank=True, null=True, help_text='說明限30字內，若無則免填')

    # major multiple choice field
    os_major_ee = models.BooleanField(u'電子電機', default=False)
    os_major_po = models.BooleanField(u'光電', default=False)
    os_major_cs = models.BooleanField(u'資工', default=False)
    os_major_me = models.BooleanField(u'機械', default=False)
    os_major_mse = models.BooleanField(u'材料', default=False)
    os_major_chem = models.BooleanField(u'化學', default=False)
    os_major_phys = models.BooleanField(u'物理', default=False)
    os_major_math = models.BooleanField(u'數學', default=False)
    os_major_bs = models.BooleanField(u'生科', default=False)
    os_major_ms = models.BooleanField(u'管理', default=False)
    os_major_hs = models.BooleanField(u'人社', default=False)
    os_major_law = models.BooleanField(u'法律', default=False)
    os_major_ohter = models.CharField(u'其他', max_length=50, blank=True, null=True)

    SKILL_RATING = (
        (u'native', u'native'),
        (u'good', u'good'),
        (u'fair', u'fair'),
        (u'poor', u'poor'),
        (u'inapplicable', u'inalpplicable'),
    )
    # chinese skill (optional)
    os_chinese_listen = models.CharField(u'Chinese Listening', max_length=12, choices=SKILL_RATING, null=True, blank=True)
    os_chinese_speak = models.CharField(u'Chinese Speaking', max_length=12, choices=SKILL_RATING, null=True, blank=True)
    os_chinese_read = models.CharField(u'Chinese Reading', max_length=12, choices=SKILL_RATING, null=True, blank=True)
    os_chinese_write = models.CharField(u'Chinese Writing', max_length=12, choices=SKILL_RATING, null=True, blank=True)

    # english skill (optional)
    os_eng_listen = models.CharField(u'English Listening', max_length=12, choices=SKILL_RATING, null=True, blank=True)
    os_eng_speak = models.CharField(u'English Speaking', max_length=12, choices=SKILL_RATING, null=True, blank=True)
    os_eng_read = models.CharField(u'English Reading', max_length=12, choices=SKILL_RATING, null=True, blank=True)
    os_eng_write = models.CharField(u'English Writing', max_length=12, choices=SKILL_RATING, null=True, blank=True)

    os_other_required = models.CharField(u'特殊徵才條件', blank=True, null=True, max_length=255)
    os_others = models.CharField(u'其他事項', blank=True, null=True, max_length=255)

    # intern
    intern_num = models.IntegerField(u'實習人數', default=0)
    intern_percent = models.CharField(u'實習生比例', max_length=10, default='0')
    intern_bachelor = models.BooleanField(u'大學生', default=False)
    intern_master = models.BooleanField(u'碩士生', default=False)
    intern_phd = models.BooleanField(u'博士生', default=False)
    intern_week = models.IntegerField(u'實習週數', default=0)
    intern_hour = models.IntegerField(u'實習時數', default=0)
    intern_pay = models.CharField(u'實習薪資', max_length=3, choices=YES_NO_CHOICES, null=True)
    intern_return = models.CharField(u'實習生轉正', max_length=3, choices=YES_NO_CHOICES, null=True)

    # satisfaction
    ee_bachelor = models.IntegerField(u'電機學院-大學人數', default=0)
    ee_master = models.IntegerField(u'電機學院-碩士人數', default=0)
    ee_phd = models.IntegerField(u'電機學院-博士人數', default=0)
    ee_satisfaction = models.CharField(u'電機學院 - 平均滿意度', max_length=10, choices=RATING,
                                       null=True, blank=True
                                       )
    cs_bachelor = models.IntegerField(u'資訊學院-大學人數', default=0)
    cs_master = models.IntegerField(u'資訊學院-碩士人數', default=0)
    cs_phd = models.IntegerField(u'資訊學院-博士人數', default=0)
    cs_satisfaction = models.CharField(u'資訊學院 - 平均滿意度', max_length=10, choices=RATING,
                                       null=True, blank=True)
    manage_bachelor = models.IntegerField(u'管理學院-大學人數', default=0)
    manage_master = models.IntegerField(u'管理學院-碩士人數', default=0)
    manage_phd = models.IntegerField(u'管理學院-博士人數', default=0)
    manage_satisfaction = models.CharField(u'管理學院 - 平均滿意度', max_length=10, choices=RATING,
                                           null=True, blank=True)
    ls_bachelor = models.IntegerField(u'生命科學院-大學人數', default=0)
    ls_master = models.IntegerField(u'生命科學院-碩士人數', default=0)
    ls_phd = models.IntegerField(u'生命科學院-博士人數', default=0)
    ls_satisfaction = models.CharField(u'生命科學院 - 平均滿意度', max_length=10, choices=RATING,
                                       null=True, blank=True)
    bio_bachelor = models.IntegerField(u'生物科技學院-大學人數', default=0)
    bio_master = models.IntegerField(u'生物科技學院-碩士人數', default=0)
    bio_phd = models.IntegerField(u'生物科技學院-博士人數', default=0)
    bio_satisfaction = models.CharField(u'生物科技學院 - 平均滿意度', max_length=10, choices=RATING,
                                        null=True, blank=True)
    bse_bachelor = models.IntegerField(u'生物醫學暨工程學院-大學人數', default=0)
    bse_master = models.IntegerField(u'生物醫學暨工程學院-碩士人數', default=0)
    bse_phd = models.IntegerField(u'生物醫學暨工程學院-博士人數', default=0)
    bse_satisfaction = models.CharField(u'生物醫學暨工程學院 - 平均滿意度', max_length=10, choices=RATING,
                                        null=True, blank=True)
    sci_bachelor = models.IntegerField(u'理學院-大學人數', default=0)
    sci_master = models.IntegerField(u'理學院-碩士人數', default=0)
    sci_phd = models.IntegerField(u'理學院-博士人數', default=0)
    sci_satisfaction = models.CharField(u'理學院 - 平均滿意度', max_length=10, choices=RATING,
                                        null=True, blank=True)
    eng_bachelor = models.IntegerField(u'工學院-大學人數', default=0)
    eng_master = models.IntegerField(u'工學院-碩士人數', default=0)
    eng_phd = models.IntegerField(u'工學院-博士人數', default=0)
    eng_satisfaction = models.CharField(u'工學院 - 平均滿意度', max_length=10, choices=RATING,
                                        null=True, blank=True)
    hs_bachelor = models.IntegerField(u'人文社會學院-大學人數', default=0)
    hs_master = models.IntegerField(u'人文社會學院-碩士人數', default=0)
    hs_phd = models.IntegerField(u'人文社會學院-博士人數', default=0)
    hs_satisfaction = models.CharField(u'人文社會學院 - 平均滿意度', max_length=10, choices=RATING,
                                       null=True, blank=True)
    hss_bachelor = models.IntegerField(u'人文與社會科學院-大學人數', default=0)
    hss_master = models.IntegerField(u'人文與社會科學院-碩士人數', default=0)
    hss_phd = models.IntegerField(u'人文與社會科學院-博士人數', default=0)
    hss_satisfaction = models.CharField(u'人文與社會科學院 - 平均滿意度', max_length=10, choices=RATING,
                                        null=True, blank=True)
    haka_bachelor = models.IntegerField(u'客家學院-大學人數', default=0)
    haka_master = models.IntegerField(u'客家學院-碩士人數', default=0)
    haka_phd = models.IntegerField(u'客家學院-博士人數', default=0)
    haka_satisfaction = models.CharField(u'客家學院 - 平均滿意度', max_length=10, choices=RATING,
                                         null=True, blank=True)
    den_bachelor = models.IntegerField(u'牙醫學院-大學人數', default=0)
    den_master = models.IntegerField(u'牙醫學院-碩士人數', default=0)
    den_phd = models.IntegerField(u'牙醫學院-博士人數', default=0)
    den_satisfaction = models.CharField(u'牙醫學院 - 平均滿意度', max_length=10, choices=RATING,
                                        null=True, blank=True)
    pho_bachelor = models.IntegerField(u'光電學院-大學人數', default=0)
    pho_master = models.IntegerField(u'光電學院-碩士人數', default=0)
    pho_phd = models.IntegerField(u'光電學院-博士人數', default=0)
    pho_satisfaction = models.CharField(u'光電學院 - 平均滿意度', max_length=10, choices=RATING,
                                        null=True, blank=True)
    law_bachelor = models.IntegerField(u'科技法律學院-大學人數', default=0)
    law_master = models.IntegerField(u'科技法律學院-碩士人數', default=0)
    law_phd = models.IntegerField(u'科技法律學院-博士人數', default=0)
    law_satisfaction = models.CharField(u'科技法律學院 - 平均滿意度', max_length=10, choices=RATING,
                                        null=True, blank=True)
    fse_bachelor = models.IntegerField(u'前瞻系統工程教育院-大學人數', default=0)
    fse_master = models.IntegerField(u'前瞻系統工程教育院-碩士人數', default=0)
    fse_phd = models.IntegerField(u'前瞻系統工程教育院-博士人數', default=0)
    fse_satisfaction = models.CharField(u'前瞻系統工程教育院 - 平均滿意度', max_length=10, choices=RATING,
                                        null=True, blank=True)
    icst_bachelor = models.IntegerField(u'國際半導體學院-大學人數', default=0)
    icst_master = models.IntegerField(u'國際半導體學院-碩士人數', default=0)
    icst_phd = models.IntegerField(u'國際半導體學院-博士人數', default=0)
    icst_satisfaction = models.CharField(u'國際半導體學院 - 平均滿意度', max_length=10, choices=RATING,
                                         null=True, blank=True)
    ai_bachelor = models.IntegerField(u'智慧科技暨綠能學院-大學人數', default=0)
    ai_master = models.IntegerField(u'智慧科技暨綠能學院-碩士人數', default=0)
    ai_phd = models.IntegerField(u'智慧科技暨綠能學院-博士人數', default=0)
    ai_satisfaction = models.CharField(u'智慧科技暨綠能學院 - 平均滿意度', max_length=10, choices=RATING,
                                       null=True, blank=True)
    som_bachelor = models.IntegerField(u'醫學院-大學人數', default=0)
    som_master = models.IntegerField(u'醫學院-碩士人數', default=0)
    som_phd = models.IntegerField(u'醫學院-博士人數', default=0)
    som_satisfaction = models.CharField(u'醫學院 - 平均滿意度', max_length=10, choices=RATING,
                                        null=True, blank=True)
    ps_bachelor = models.IntegerField(u'藥物科學院-大學人數', default=0)
    ps_master = models.IntegerField(u'藥物科學院-碩士人數', default=0)
    ps_phd = models.IntegerField(u'藥物科學院-博士人數', default=0)
    ps_satisfaction = models.CharField(u'藥物科學院 - 平均滿意度', max_length=10, choices=RATING,
                                       null=True, blank=True)
    son_bachelor = models.IntegerField(u'護理學院-大學人數', default=0)
    son_master = models.IntegerField(u'護理學院-碩士人數', default=0)
    son_phd = models.IntegerField(u'護理學院-博士人數', default=0)
    son_satisfaction = models.CharField(u'護理學院 - 平均滿意度', max_length=10, choices=RATING,
                                        null=True, blank=True)
    overall_satisfaction = models.CharField(u'整體滿意度', max_length=10, choices=RATING, null=True, blank=True)

    # salary
    SALARY_MONTH = (
        (u'約30,000 元以下', u'約30,000 元以下'),
        (u'約30,001 元至40,000 元', u'約30,001 元至40,000 元'),
        (u'約40,001 元至50,000 元', u'約40,001 元至50,000 元'),
        (u'約50,001 元至60,000 元', u'約50,001 元至60,000 元'),
        (u'約60,001 元至70,000 元', u'約60,001 元至70,000 元'),
        (u'約70,001 元至80,000 元', u'約70,001 元至80,000 元'),
        (u'約80,001 元至90,000 元', u'約80,001 元至90,000 元'),
        (u'約90,001 元至100,000 元', u'約90,001 元至100,000 元'),
        (u'約100,001 元至110,000 元', u'約100,001 元至110,000 元'),
        (u'約110,001 元至120,000 元', u'約110,001 元至120,000 元'),
        (u'約120,001 元至130,000 元', u'約120,001 元至130,000 元'),
        (u'約130,001 元至140,000 元', u'約130,001 元至140,000 元'),
        (u'約140,001 元至150,000 元', u'約140,001 元至150,000 元'),
        (u'約150,001 元以上', u'約150,001 元以上'),
    )
    SALARY_YEAR = (
        (u'40萬元以下', u'40萬元以下'),
        (u'40~80萬元', u'40~80萬元'),
        (u'80~120萬元', u'80~120萬元'),
        (u'120~160萬元', u'120~160萬元'),
        (u'160~200萬元', u'160~200萬元'),
        (u'200萬元以上', u'200萬元以上'),
    )
    salary_avg_bachelor = models.CharField(u'大學平均月薪', max_length=20, choices=SALARY_MONTH)
    salary_avg_master = models.CharField(u'碩士平均月薪', max_length=20, choices=SALARY_MONTH)
    salary_avg_phd = models.CharField(u'博士平均月薪', max_length=20, choices=SALARY_MONTH)
    nctu_salary_avg_bachelor = models.CharField(u'大學平均年薪', max_length=20, choices=SALARY_YEAR)
    nctu_salary_avg_master = models.CharField(u'碩士平均年薪', max_length=20, choices=SALARY_YEAR)
    nctu_salary_avg_phd = models.CharField(u'博士平均年薪', max_length=20, choices=SALARY_YEAR)

    # ability
    no_nycu_employee = models.BooleanField(u'目前無本校畢業生在職', default=False)

    communication_rate = models.CharField(u'溝通表達', max_length=10, choices=RATING, null=True, blank=True)
    continuous_learning_rate = models.CharField(u'持續學習', max_length=10, choices=RATING, null=True, blank=True)
    interpersonal_rate = models.CharField(u'人際互動', max_length=10, choices=RATING, null=True, blank=True)
    collaboration_rate = models.CharField(u'團隊合作', max_length=10, choices=RATING, null=True, blank=True)
    problem_solving_rate = models.CharField(u'問題解決', max_length=10, choices=RATING, null=True, blank=True)
    innovation_rate = models.CharField(u'創新', max_length=10, choices=RATING, null=True, blank=True)
    responsibility_rate = models.CharField(u'工作責任及紀律', max_length=10, choices=RATING, null=True, blank=True)
    tech_applications_rate = models.CharField(u'資訊科技應用', max_length=10, choices=RATING, null=True, blank=True)
    
    # ability choice
    communication = models.BooleanField(u'溝通表達', default=False)
    continuous_learning = models.BooleanField(u'持續學習', default=False)
    interpersonal = models.BooleanField(u'人際互動', default=False)
    collaboration = models.BooleanField(u'團隊合作', default=False)
    problem_solving = models.BooleanField(u'問題解決', default=False)
    innovation = models.BooleanField(u'創新', default=False)
    responsibility = models.BooleanField(u'工作責任及紀律', default=False)
    tech_applications = models.BooleanField(u'資訊科技應用', default=False)
    other = models.CharField(u'其它', max_length=100, blank=True, null=True)

    # exp
    HELPFUL_RATE = (
        (u'無幫助', u'無幫助'),
        (u'略有幫助', u'略有幫助'),
        (u'有幫助', u'有幫助'),
        (u'頗有幫助', u'頗有幫助'),
        (u'極有幫助', u'極有幫助'),
    )

    major = models.CharField(u'主修科系', max_length=4, choices=HELPFUL_RATE)
    graduation_school = models.CharField(u'畢業學校', max_length=4, choices=HELPFUL_RATE)
    second_major = models.CharField(u'輔系、雙學位、學程', max_length=4, choices=HELPFUL_RATE)
    club = models.CharField(u'社團經驗', max_length=4, choices=HELPFUL_RATE)
    common_class = models.CharField(u'通識教育', max_length=4, choices=HELPFUL_RATE)
    national_exam = models.CharField(u'國家考試證書', max_length=4, choices=HELPFUL_RATE)
    cert = models.CharField(u'證照', max_length=4, choices=HELPFUL_RATE)
    work_exp = models.CharField(u'相關工作經驗（打工、實習）', max_length=4, choices=HELPFUL_RATE)
    travel_study = models.CharField(u'遊學（如交換學生、雙聯學位等）', max_length=4, choices=HELPFUL_RATE)

    # ways to recruit
    hr_bank = models.BooleanField(u'人力銀行')
    newspaper_ad = models.BooleanField(u'報章廣告')
    website = models.BooleanField(u'公司網頁')
    school = models.BooleanField(u'學校宣傳')
    teacher_recommend = models.BooleanField(u'老師推薦')
    campus_jobfair = models.BooleanField(u'校園徵才')
    contest = models.BooleanField(u'競賽活動')
    recruit_other = models.BooleanField(u'其他', default=False)

    # receive info
    receive_info = models.BooleanField(u'我希望定期接收校園徵才活動訊息')
    suggestions = models.CharField(u'其它建議', max_length=150, blank=True, null=True)

    updated = models.DateTimeField(u'更新時間', auto_now=True)

    class Meta:
        managed = True
        verbose_name = u"企業滿意度問卷"
        verbose_name_plural = u"企業滿意度問卷"

    def company_name(self):
        com = company.models.Company.objects.filter(cid=self.cid).first()
        return "資料庫不同步，請連絡資訊組" if com is None else com.shortname


class SlotColor(models.Model):
    id = models.AutoField(primary_key=True)
    place = models.CharField(u'場地', max_length=20, unique=True)
    css_color = models.CharField(u'文字顏色(css)', max_length=20, help_text=
    '''請輸入顏色英文，比如: red, green, blue, purple, black等'''
                                 )
    place_info = models.URLField(u'場地介紹網頁', max_length=256, default="http://")
    zone = models.ForeignKey('ZoneCategories', verbose_name=u'專區類別', on_delete=models.CASCADE, null=True, blank=True)


    class Meta:
        managed = True
        verbose_name = u"2. 場地顏色及資訊"
        verbose_name_plural = u"2. 場地顏色及資訊"

    def __str__(self):
        return self.place


class Student(models.Model):
    card_num = models.CharField(u'學生證卡號', max_length=20, primary_key=True)
    attendance = models.ManyToManyField(SeminarSlot, through='StuAttendance')
    student_id = models.CharField(u'學號', max_length=10, blank=True, null=True)
    
    phone = models.CharField(u'手機', max_length=15, blank=True, null=True, help_text='格式：0987654321')
    name = models.CharField(u'姓名', max_length=30, blank=True, null=True)
    department = models.CharField(u'系級', max_length=20, blank=True, null=True)
    email = models.EmailField(u'Email', max_length=64, blank=True)
    other = models.TextField(u'其他', max_length=64, blank=True, null=True)

    def get_redeem_points(self):
        redeem_records = ExchangePrize.objects.filter(student=self)
        redeem_points = sum([i.points for i in redeem_records])
        return redeem_points

    def get_points(self):
        points = sum([i.points for i in self.attendance.all()])
        redeem_records = ExchangePrize.objects.filter(student=self)
        redeem_points = sum([i.points for i in redeem_records])
        return points - redeem_points

    class Meta:
        verbose_name = u'說明會學生'
        verbose_name_plural = u'說明會學生'

    def __str__(self):
        return self.card_num if not self.student_id else self.student_id


class StuAttendance(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, to_field='card_num', verbose_name=u'學生證卡號', on_delete=models.CASCADE)
    seminar = models.ForeignKey(SeminarSlot, to_field='id', on_delete=models.CASCADE)
    updated = models.DateTimeField(u'更新時間', auto_now=True)
    
    def get_company(self):
        if self.seminar.company is None:
            return "None"
        return self.seminar.company.get_company_name()
    get_company.short_description = "說明會企業"

    def get_student_id(self):
        return self.student.student_id
    get_student_id.short_description = "學號"

    def get_student_name(self):
        return self.student.name
    get_student_name.short_description = "姓名"

    class Meta:
        unique_together = ('student', 'seminar')
        verbose_name = u"說明會參加記錄"
        verbose_name_plural = u"說明會參加記錄"


class ExchangePrize(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, to_field='card_num', verbose_name='學生證卡號', on_delete=models.CASCADE)
    points = models.IntegerField(u'所需點數', default=0, blank=True)
    prize = models.CharField(u'獎品', max_length=100, default='', blank=True)
    updated = models.DateTimeField(u'更新時間', auto_now=True)

    class Meta:
        verbose_name = u'兌獎紀錄'
        verbose_name_plural = u'兌獎紀錄'


class RecruitInfo(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(u'標題', default='', max_length=10)
    content = RichTextField(u'內容', default='', null=True, blank=True)
    updated = models.DateTimeField(u'更新時間', auto_now=True)

    def __str__(self):
        return "Recruit_Info"

    class Meta:
        managed = True
        verbose_name = u"6. 校徵活動資訊 (學生)"
        verbose_name_plural = u"6. 校徵活動資訊 (學生)"


class RecruitCompanyInfo(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(u'標題', default='', max_length=10)
    content = RichTextField(u'內容', default='', null=True, blank=True)
    updated = models.DateTimeField(u'更新時間', auto_now=True)

    def __str__(self):
        return "Recruit_Company_Info"

    class Meta:
        managed = True
        verbose_name = u"5. 校徵活動資訊 (企業)"
        verbose_name_plural = u"5. 校徵活動資訊 (企業)"


class RecruitSeminarInfo(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(u'標題', default='', max_length=10)
    content = RichTextField(u'內容', default='', null=True, blank=True)
    updated = models.DateTimeField(u'更新時間', auto_now=True)

    def __str__(self):
        return "Recruit_Seminar_Info"

    class Meta:
        managed = True
        verbose_name = u"說明會資訊編輯頁面 (學生)"
        verbose_name_plural = u"說明會資訊編輯頁面 (學生)"


class RecruitECESeminarInfo(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(u'標題', default='', max_length=10)
    content = RichTextField(u'內容', default='', null=True, blank=True)
    updated = models.DateTimeField(u'更新時間', auto_now=True)

    def __str__(self):
        return "Recruit_ECE_Seminar_Info"

    class Meta:
        managed = True
        verbose_name = u"ECE說明會資訊編輯頁面 (學生)"
        verbose_name_plural = u"ECE說明會資訊編輯頁面 (學生)"


class RecruitOnlineSeminarInfo(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(u'標題', default='', max_length=10)
    content = RichTextField(u'內容', default='', null=True, blank=True)
    updated = models.DateTimeField(u'更新時間', auto_now=True)

    def __str__(self):
        return "Recruit_Online_Seminar_Info"

    class Meta:
        managed = True
        verbose_name = u"線上說明會資訊編輯頁面 (學生)"
        verbose_name_plural = u"線上說明會資訊編輯頁面 (學生)"


class RecruitJobfairInfo(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(u'標題', default='', max_length=10)
    content = RichTextField(u'內容', default='', null=True, blank=True)
    updated = models.DateTimeField(u'更新時間', auto_now=True)

    def __str__(self):
        return "Recruit_Jobfair_Info"

    class Meta:
        managed = True
        verbose_name = u"就博會資訊編輯頁面 (學生)"
        verbose_name_plural = u"就博會資訊編輯頁面 (學生)"


class RecruitOnlineJobfairInfo(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(u'標題', default='', max_length=10)
    content = RichTextField(u'內容', default='', null=True, blank=True)
    updated = models.DateTimeField(u'更新時間', auto_now=True)

    def __str__(self):
        return "Recruit_Online_Jobfair_Info"

    class Meta:
        managed = True
        verbose_name = u"線上就博會資訊編輯頁面 (學生)"
        verbose_name_plural = u"線上就博會資訊編輯頁面 (學生)"


class RedeemDailyPrize(models.Model):
    """
    Record the student who listens to seminars and reach the
    threshold set in the config in a day.
    """
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, to_field='card_num', verbose_name=u'學生證卡號', on_delete=models.CASCADE)
    date = models.CharField(u'參加日期', max_length=30, default='')
    redeem = models.BooleanField(u'是否兌獎', default=False)
    updated = models.DateTimeField(u'更新時間', auto_now=True)

    class Meta:
        verbose_name = u"達成說明會參與次數紀錄&兌獎"
        verbose_name_plural = u"達成說明會參與次數紀錄&兌獎"
