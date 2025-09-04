from django.db import models
from django.core.validators import RegexValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
import company.models
import datetime


def validate_mobile(string):
    RegexValidator(regex='^\d{4}-\d{6}$', message='手機格式為：0987-654321')(string)


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
    discount = models.IntegerField(u'專區優惠', default=0)
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

class RdssConfigs(models.Model):
    id = models.AutoField(primary_key=True)
    register_start = models.DateTimeField(u'廠商註冊開始時間')
    register_end = models.DateTimeField(u'廠商註冊結束時間')
    rdss_signup_start = models.DateTimeField(u'秋季招募報名開始時間')
    rdss_signup_end = models.DateTimeField(u'秋季招募報名結束時間')

    # 問卷
    survey_start = models.DateTimeField(u'滿意度問卷開始填答')
    survey_end = models.DateTimeField(u'滿意度問卷結束填答')

    # 說明會相關
    seminar_start_date = models.DateField(u'說明會開始日期')
    seminar_end_date = models.DateField(u'說明會結束日期')
    seminar_info_deadline = models.DateTimeField(u'說明會資訊截止填寫時間', default=timezone.now)
    seminar_btn_start = models.DateField(u'說明會按鈕開啟日期', null=True)
    seminar_btn_end = models.DateField(u'說明會按鈕關閉日期', null=True)
    seminar_btn_enable_time = models.TimeField(u'說明會按鈕每日開啟時間', default="8:00", help_text="按鈕將於每日此時間開啟")
    seminar_btn_disable_time = models.TimeField(u'說明會按鈕每日關閉時間', default="18:00", help_text="按鈕將於每日此時間關閉")
    ## 說明會參與達標現場領獎：當學生在一定天數範圍內（seminar_prize_day）參加說明會的
    ## 點數達標（seminar_prize_threshold）後，可於參加完說明會集點當下領獎，與集點抽獎為兩個不同機制
    seminar_prize_interval_days = models.IntegerField(
        u'說明會點數累積天數',
        default=1,
        help_text="累積幾天參加說明會的點數達標後可現場領獎"
    )
    seminar_prize_threshold = models.IntegerField(
        u'現場領獎門檻',
        default=10,
        help_text="期間內參與多少場說明會以上才可兌獎，與“期間內說明會全數參加者領獎”設定為或的關係"
    )
    ### 是否開放期間內說明會全數參加者領獎
    seminar_prize_all = models.BooleanField(
        u'期間內說明會全數參加者領獎',
        default=False,
        help_text="是否開放期間內說明會全數參加者領獎，與“每日參與領獎門檻”為或的關係"
    )

    # ECE說明會相關
    seminar_ece_start_date = models.DateField(u'實體ECE說明會開始日期', default=datetime.date.today)
    seminar_ece_end_date = models.DateField(u'實體ECE說明會結束日期', default=datetime.date.today)
    session_ece_fee = models.IntegerField(u'實體ECE說明會_費用', default=0)

    # 就博會相關
    jobfair_date = models.DateField(u'就博會日期')
    jobfair_start = models.TimeField(u'就博會開始時間')
    jobfair_end = models.TimeField(u'就博會結束時間')
    jobfair_booth_fee = models.IntegerField(u'就博會攤位費用(每攤)', default=0)
    jobfair_info_deadline = models.DateTimeField(u'就博會資訊截止填寫時間', default=timezone.now)
    JOBFAIR_FOOD_CHOICES = (
        ('lunch_box', u'餐盒(蛋奶素)'),
        ('bento', u'便當(葷素)')
    )
    jobfair_food = models.CharField(u'就業博覽會餐點', max_length=10, choices=JOBFAIR_FOOD_CHOICES, default='餐盒(蛋奶素)')
    jobfair_food_info = RichTextField(u'餐點注意事項', max_length=128, blank=True, null=True)
    jobfair_btn_start = models.DateField(u'就博會按鈕開啟日期', null=True)
    jobfair_btn_end = models.DateField(u'就博會按鈕關閉日期', null=True)
    jobfair_btn_enable_time = models.TimeField(u'就博會按鈕每日開啟時間', default="8:00", help_text="按鈕將於每日此時間開啟")
    jobfair_btn_disable_time = models.TimeField(u'就博會按鈕每日關閉時間', default="18:00", help_text="按鈕將於每日此時間關閉")

    class Meta:
        managed = True
        verbose_name = u"1. 秋季招募活動設定"
        verbose_name_plural = u"1. 秋季招募活動設定"

class ECESeminar(models.Model):
    id = models.AutoField(primary_key=True)
    seminar_name = models.CharField(u'實體ECE說明會名稱', max_length=50)
    ece_member_discount = models.BooleanField(u'電機資源產學聯盟優惠', default=False)

    def __str__(self):
        return u'{}'.format(self.seminar_name)

    class Meta:
        managed = True
        verbose_name = u'3. 實體ECE說明會設定'
        verbose_name_plural = u'3. 實體ECE說明會設定'


class Signup(models.Model):
    SEMINAR_CHOICES = (
        (u'none', u'不參加企業說明會'),
        (u'attend', u'參加說明會'),
    )
    id = models.AutoField(primary_key=True)
    cid = models.CharField(u'公司統一編號', unique=True, max_length=8, null=False)
    zone = models.ForeignKey('ZoneCategories', verbose_name=u'專區類別', on_delete=models.CASCADE, null=True)
    history = models.ManyToManyField('HistoryParticipation', verbose_name=u'歷史參加調查', blank=True)
    seminar = models.CharField(u'說明會場次', max_length=15,
                               choices=SEMINAR_CHOICES, default='none', blank=True)
    seminar_type = models.ForeignKey('ConfigSeminarChoice',
                                     verbose_name=u'說明會場次類型', on_delete=models.CASCADE,
                                     default=1, blank=True)
    jobfair = models.IntegerField(u'徵才展示會攤位數量', default=0, validators=[ MinValueValidator(0)])
    seminar_ece = models.ManyToManyField('ECESeminar', verbose_name=u'實體ECE說明會場次', blank=True)
    career_tutor = models.BooleanField(u'諮詢服務', default=False)
    visit = models.BooleanField(u'企業參訪', default=False)
    lecture = models.BooleanField(u'就業力講座', default=False)
    payment = models.BooleanField(u'完成付款', default=False)
    receipt_no = models.CharField(u'收據號碼', max_length=50, null=True, blank=True)
    ps = models.TextField(u'備註', null=True, blank=True)
    added = models.DateTimeField(u'報名時間', auto_now_add=True)
    updated = models.DateTimeField(u'更新時間', auto_now=True)

    class Meta:
        managed = True
        verbose_name = u"4. 活動報名情況"
        verbose_name_plural = u"4. 活動報名情況"

    def __str__(self):
        com = company.models.Company.objects.filter(cid=self.cid).first()
        return "資料庫不同步，請連絡資訊組" if com is None else com.shortname

    def get_company_name(self):
        com = company.models.Company.objects.filter(cid=self.cid).first()
        return "資料庫不同步，請連絡資訊組" if com is None else com.shortname

    def company_other_ps(self):
        com = company.models.Company.objects.filter(cid=self.cid).first()
        if com:
            return com.other_ps
        else:
            return None


class ConfigSeminarChoice(models.Model):
    id = models.AutoField(primary_key=True)
    config = models.ForeignKey(
        RdssConfigs, on_delete=models.CASCADE, related_name='config_seminar_choice'
    )
    name = models.CharField(u'說明會場次名稱', max_length=30, help_text="例如：上午場、下午場、晚場")
    session_fee = models.IntegerField(u'說明會場次_費用', default=0)

    class Meta:
        managed = True
        verbose_name = u"說明會場次類型＆費用設定"
        verbose_name_plural = u"說明會場次類型＆費用設定"

    def __str__(self):
        return self.name

    def get_session_fee(self):
        return self.session_fee


class ConfigSeminarSession(models.Model):
    id = models.AutoField(primary_key=True)
    config = models.ForeignKey(
        RdssConfigs, on_delete=models.CASCADE, related_name='config_seminar_session'
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

        if not datetime.time(6, 0, 0) <= self.session_start <= datetime.time(21, 0, 0):
            raise ValidationError("開始時間必須在 6:00 至 21:00 之間")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


# Proxy model for AdminSite company list item
class Company(Signup):
    class Meta:
        proxy = True
        verbose_name = u"2. 參加廠商"
        verbose_name_plural = u"2. 參加廠商"


class SeminarSlot(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateField(u'日期')
    session_from_config = models.ForeignKey(
        "ConfigSeminarSession",
        on_delete=models.CASCADE,
        verbose_name="時段(new)",
        related_name="seminar_slots",
        help_text="於活動設定中指定時段及對應價格",
        null=True,
        blank=True,
    )
    company = models.ForeignKey('Signup', to_field='cid',
                                   verbose_name=u'公司',
                                   on_delete=models.CASCADE, null=True, blank=True, unique=False)
    place = models.ForeignKey('SlotColor', verbose_name=u'場地', on_delete=models.CASCADE, default=1)
    points = models.SmallIntegerField(u'集點點數', default=1)
    updated = models.DateTimeField(u'更新時間', auto_now=True)

    class Meta:
        managed = True
        verbose_name = u"說明會場次"
        verbose_name_plural = u"說明會場次"

    def __str__(self):
        if self.company is None:
            return '{} {} {}'.format(self.date, self.session_from_config, "None")

        return '{} {} {}'.format(self.date, self.session_from_config , self.company.get_company_name())


class Student(models.Model):
    idcard_no = models.CharField(u'學生證卡號', max_length=20, primary_key=True)
    attendance = models.ManyToManyField(SeminarSlot, through='StuAttendance')
    student_id = models.CharField(u'學號', max_length=10, blank=True)
    phone = models.CharField(u'手機', max_length=20, blank=True,
                             help_text='格式：0987654321')
    name = models.CharField(u'姓名', max_length=64, blank=True)
    dep = models.CharField(u'系級', max_length=16, blank=True)
    email = models.EmailField(u'Email', max_length=64, blank=True)
    other = models.TextField(u'其他', max_length=64, blank=True, null=True)

    class Meta:
        verbose_name = u"說明會學生"
        verbose_name_plural = u"說明會學生"

    def __str__(self):
        return self.idcard_no if not self.student_id else self.student_id

    def get_points(self):
        points = sum([i.points for i in self.attendance.all()])
        redeem_records = RedeemPrize.objects.filter(student=self)
        redeemed = sum([i.points for i in redeem_records])
        return points - redeemed

    def get_redeemed(self):
        redeem_records = RedeemPrize.objects.filter(student=self)
        redeemed = sum([i.points for i in redeem_records])
        return redeemed


class StuAttendance(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, to_field='idcard_no',
                                verbose_name=u'學生證卡號',
                                on_delete=models.CASCADE, )

    seminar = models.ForeignKey(SeminarSlot,
                                on_delete=models.CASCADE, )

    updated = models.DateTimeField(u'時間', auto_now=True)

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
        unique_together = ("student", "seminar")
        verbose_name = u"說明會參加記錄"
        verbose_name_plural = u"說明會參加記錄"


class RedeemPrize(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, to_field='idcard_no',
                                verbose_name=u'學生證卡號',
                                on_delete=models.CASCADE, )
    prize = models.CharField(u'獎品', max_length=100, default='', blank=True)
    points = models.IntegerField(u'所需點數', default=0, blank=True)
    updated = models.DateTimeField(u'更新時間', auto_now=True)

    class Meta:
        verbose_name = u"兌獎紀錄"
        verbose_name_plural = u"兌獎紀錄"


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
        verbose_name = u"場地顏色及資訊"
        verbose_name_plural = u"場地顏色及資訊"

    def __str__(self):
        return self.place


class SeminarOrder(models.Model):
    id = models.AutoField(primary_key=True)
    time = models.DateTimeField(u'選位開始時間')
    company = models.OneToOneField('Signup', to_field='cid',
                                   verbose_name=u'公司',
                                   on_delete=models.CASCADE,
                                   limit_choices_to=~Q(seminar='')
                                   )
    updated = models.DateTimeField(u'更新時間', auto_now=True)

    class Meta:
        managed = True
        verbose_name = u"說明會選位順序"
        verbose_name_plural = u"說明會選位順序"


class SeminarInfo(models.Model):
    id = models.AutoField(primary_key=True)
    company = models.OneToOneField('Signup', to_field='cid',
                                   verbose_name=u'公司',
                                   on_delete=models.CASCADE)
    topic = models.CharField(u'說明會主題', max_length=30)
    speaker = models.CharField(u'主講人', max_length=30)
    speaker_title = models.CharField(u'主講人稱謂', max_length=30)
    speaker_email = models.EmailField(u'主講人Email', max_length=254)
    attendees = models.SmallIntegerField(u'人資餐點數量', default=0)
    raffle_prize = models.CharField(u'抽獎獎品', max_length=254,
                                    null=True, blank=True)
    raffle_prize_amount = models.SmallIntegerField(u'抽獎獎品數量', default=0)
    qa_prize = models.CharField(u'QA獎獎品', max_length=254, null=True, blank=True)
    qa_prize_amount = models.SmallIntegerField(u'QA獎獎品數量', default=0)
    attend_prize = models.CharField(u'參加獎獎品', max_length=254,
                                    null=True, blank=True)
    attend_prize_amount = models.SmallIntegerField(u'參加獎獎品數量', default=0)
    meal = models.CharField(u'餐點名稱', max_length=254,
                                    null=True, blank=True)
    meal_amount = models.SmallIntegerField(u'餐點數量', default=0)
    snack_box = models.SmallIntegerField(u'加碼餐盒數量', default=0)
    contact = models.CharField(u'聯絡人', max_length=30)
    contact_mobile = models.CharField(u'聯絡人手機', max_length=16,
                                      validators=[validate_mobile])
    contact_email = models.EmailField(u'聯絡人Email', max_length=254)
    ps = models.TextField(u'其它需求', null=True, blank=True)
    updated = models.DateTimeField(u'更新時間', auto_now=True)

    def __str__(self):
        return self.company.cid

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


# 以下為就博會


class JobfairSlot(models.Model):
    id = models.AutoField(primary_key=True)
    # TODO: investigate if we can use int for serial_no
    serial_no = models.CharField(u'攤位編號', max_length=10)
    zone = models.ForeignKey('ZoneCategories', verbose_name=u'專區類別', on_delete=models.CASCADE, null=True)
    company = models.ForeignKey('Signup', to_field='cid',
                                verbose_name=u'公司',
                                on_delete=models.CASCADE, blank=True, null=True)
    updated = models.DateTimeField(u'更新時間', auto_now=True)

    class Meta:
        managed = True
        verbose_name = u"就博會攤位"
        verbose_name_plural = u"就博會攤位"

    def __str__(self):
        return self.serial_no


class OnlineJobfairSlot(models.Model):
    id = models.AutoField(primary_key=True)
    serial_no = models.CharField(u'攤位編號', max_length=10)
    category = models.CharField(u'類別', max_length=37, choices=CATEGORYS)
    company = models.ForeignKey('Signup', to_field='cid',
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


class JobfairOrder(models.Model):
    id = models.AutoField(primary_key=True)
    time = models.DateTimeField(u'選位開始時間')
    company = models.OneToOneField('Signup', to_field='cid',
                                   verbose_name=u'公司',
                                   on_delete=models.CASCADE,
                                   limit_choices_to=~Q(jobfair=0)
                                   )
    updated = models.DateTimeField(u'更新時間', auto_now=True)

    class Meta:
        managed = True
        verbose_name = u"就博會選位順序"
        verbose_name_plural = u"就博會選位順序"


class JobfairInfo(models.Model):
    id = models.AutoField(primary_key=True)
    company = models.OneToOneField('Signup', to_field='cid',
                                   verbose_name=u'公司',
                                   on_delete=models.CASCADE)
    signname = models.CharField(u'攤位招牌名稱', max_length=20)
    sign_eng_name = models.CharField(u'攤位招牌英文名稱', max_length=10, help_text="請填寫英文名稱, 限制10字元內", default="")
    disable_proofread = models.BooleanField(u'無需校對', default=False)
    contact = models.CharField(u'聯絡人', max_length=30)
    contact_mobile = models.CharField(u'聯絡人手機', max_length=16,
                                      validators=[validate_mobile])
    contact_email = models.EmailField(u'聯絡人Email', max_length=254)
    
    parking_tickets = models.IntegerField(u'停車證數量', default=0, blank=True, null=True)
    lunch_box = models.SmallIntegerField(u'餐盒數量', default=0, help_text="餐盒預設為蛋奶素", blank=True, null=True)
    meat_lunchbox = models.SmallIntegerField(u'葷食餐點數量', default=0, blank=True, null=True)
    vege_lunchbox = models.SmallIntegerField(u'素食餐點', default=0, blank=True, null=True)

    power_req = models.CharField(u'用電需求', max_length=256,
                                 help_text="請填寫當天會使用的用電設備")
    ps = models.TextField(u'其它需求', blank=True)
    updated = models.DateTimeField(u'更新時間', auto_now=True)

    def __str__(self):
        return self.company.cid

    class Meta:
        managed = True
        verbose_name = u"就博會資訊"
        verbose_name_plural = u"就博會資訊"


class JobfairParking(models.Model):
    id = models.AutoField(primary_key=True)
    license_plate_number = models.CharField(u'車牌號碼', max_length=8, validators=[validate_license_plate_number])
    info = models.ForeignKey(JobfairInfo, verbose_name=u'公司', on_delete=models.CASCADE)

    def __str__(self):
        return self.license_plate_number

    class Meta:
        verbose_name = u"就博會車牌號碼"
        verbose_name_plural = u"就博會車牌號碼"


class SponsorItems(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(u'贊助品名稱', max_length=64, unique=True)
    description = models.CharField(u'贊助品說明', max_length=250)
    spec = models.CharField(u'規格', max_length=100, null=True, blank=True)
    ps = models.CharField(u'備註', max_length=100, null=True, blank=True)
    price = models.IntegerField(u'價格')
    limit = models.IntegerField(u'數量限制')
    sponsors = models.ManyToManyField(Signup, through='Sponsorship')
    pic = models.ImageField(u"贊助品預覽圖", upload_to='sponsor_items',
                            null=True,
                            help_text='''提供過去做的贊助品圖片，做為參考''')

    class Meta:
        managed = True
        verbose_name = u"5. 贊助品"
        verbose_name_plural = u"5. 贊助品"

    def __str__(self):
        return self.name


class Sponsorship(models.Model):
    id = models.AutoField(primary_key=True)
    company = models.ForeignKey(Signup, to_field='cid',
                                verbose_name=u'公司',
                                on_delete=models.CASCADE)
    item = models.ForeignKey(SponsorItems,
                             to_field='name', on_delete=models.CASCADE)
    updated = models.DateTimeField(u'更新時間', auto_now=True)

    class Meta:
        managed = True
        # unique_together = ("company",  "item")
        verbose_name = u"6. 贊助情況"
        verbose_name_plural = u"6. 贊助情況"


class Files(models.Model):
    FILE_CAT = (
        ('企畫書', '企畫書'),
        ('報名說明書', '報名說明書'),
        ('選位相關', '選位相關'),
        ('就博會攤位圖', '就博會攤位圖'),
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
        ('na', '不適用')
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
    categories = models.ForeignKey(
        'CompanyCategories',
        verbose_name=u'企業類別',
        on_delete=models.SET_NULL,
        null=True
    )

    # oversea recruit info
    # os = overseas, osc = overseas chinese, cn = china
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


class RdssInfo(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(u'標題', default='', max_length=10)
    content = RichTextUploadingField(u'內容', default='', null=True, blank=True)
    updated = models.DateTimeField(u'更新時間', auto_now=True)

    def __str__(self):
        return "Rdss_info"

    class Meta:
        managed = True
        verbose_name = u"秋季招募活動資訊"
        verbose_name_plural = u"秋季招募活動資訊"


class RdssCompanyInfo(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(u'標題', default='', max_length=10)
    content = RichTextUploadingField(u'內容', default='', null=True, blank=True)
    updated = models.DateTimeField(u'更新時間', auto_now=True)

    def __str__(self):
        return "Rdss_Company_info"

    class Meta:
        managed = True
        verbose_name = u"秋季招募活動資訊(公司)"
        verbose_name_plural = u"秋季招募活動資訊(公司)"


class RdssSeminarInfo(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(u'標題', default='', max_length=10)
    content = RichTextUploadingField(u'內容', default='', null=True, blank=True)
    updated = models.DateTimeField(u'更新時間', auto_now=True)

    def __str__(self):
        return "Rdss_Seminar_info"

    class Meta:
        managed = True
        verbose_name = u"說明會資訊編輯頁面"
        verbose_name_plural = u"說明會資訊編輯頁面"


class RdssJobfairInfo(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(u'標題', default='', max_length=10)
    content = RichTextUploadingField(u'內容', default='', null=True, blank=True)
    updated = models.DateTimeField(u'更新時間', auto_now=True)

    def __str__(self):
        return "Rdss_Jobfair_info"

    class Meta:
        managed = True
        verbose_name = u"就博會資訊編輯頁面"
        verbose_name_plural = u"就博會資訊編輯頁面"


class RdssOnlineJobfairInfo(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(u'標題', default='', max_length=10)
    content = RichTextField(u'內容', default='', null=True, blank=True)
    updated = models.DateTimeField(u'更新時間', auto_now=True)

    def __str__(self):
        return "Rdss_online_Jobfair_info"

    class Meta:
        managed = True
        verbose_name = u"線上就博會資訊編輯頁面"
        verbose_name_plural = u"線上就博會資訊編輯頁面"


class RedeemOnsitePrize(models.Model):
    """
    Record the student who attends to seminars and reach the
    threshold set in the config in an interval.
    """
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, to_field='idcard_no', verbose_name=u'學生證卡號', on_delete=models.CASCADE)
    date = models.CharField(u'參加日期', max_length=30, default='')
    redeem = models.BooleanField(u'是否兌獎', default=False)
    updated = models.DateTimeField(u'更新時間', auto_now=True)

    class Meta:
        verbose_name = u"說明會參與達標現場領獎"
        verbose_name_plural = u"說明會參與達標現場領獎"
