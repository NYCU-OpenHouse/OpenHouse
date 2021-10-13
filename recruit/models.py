from django.db import models
from company.models import Company
from django.db.models import Q
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
import datetime


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
    (u'綜合', u'綜合'),
    (u'人力銀行', u'人力銀行'),
    (u'機構', u'機構'),
    (u'新創', u'新創'),
    (u'主辦保留', u'主辦保留'),
    (u'生科醫療', u'生科醫療')
)


class RecruitConfigs(models.Model):
    register_start = models.DateTimeField(u'廠商註冊開始時間')
    register_end = models.DateTimeField(u'廠商註冊結束時間')
    recruit_signup_start = models.DateTimeField(u'校徵報名開始時間')
    recruit_signup_end = models.DateTimeField(u'校徵報名結束時間')

    survey_start = models.DateTimeField(u'滿意度問卷開始填答')
    survey_end = models.DateTimeField(u'滿意度問卷結束填答')

    # 說明會相關
    seminar_start_date = models.DateField(u'說明會開始日期', default=datetime.date.today)
    seminar_end_date = models.DateField(u'說明會結束日期', default=datetime.date.today)
    session_1_start = models.TimeField(u'說明會場次1_開始時間', default='00:00')
    session_1_end = models.TimeField(u'說明會場次1_結束時間', default='00:00')
    session_2_start = models.TimeField(u'說明會場次2(中午)_開始時間', default='00:00')
    session_2_end = models.TimeField(u'說明會場次2(中午)_結束時間', default='00:00')
    session_3_start = models.TimeField(u'說明會場次3_開始時間', default='00:00')
    session_3_end = models.TimeField(u'說明會場次3_結束時間', default='00:00')
    session_4_start = models.TimeField(u'說明會場次4_開始時間', default='00:00')
    session_4_end = models.TimeField(u'說明會場次4_結束時間', default='00:00')
    session_5_start = models.TimeField(u'說明會場次5_開始時間', default='00:00')
    session_5_end = models.TimeField(u'說明會場次5_結束時間', default='00:00')
    session_6_start = models.TimeField(u'說明會場次6_開始時間', default='00:00')
    session_6_end = models.TimeField(u'說明會場次6_結束時間', default='00:00')
    seminar_online_start_date = models.DateField(u'線上說明會開始日期', default=datetime.date.today)
    seminar_online_end_date = models.DateField(u'線上說明會結束日期', default=datetime.date.today)
    # 費用
    session_fee = models.IntegerField(u'說明會場次_費用', default=0)
    session_online_fee = models.IntegerField(u'線上說明會_費用', default=0)

    # 就博會相關
    jobfair_date = models.DateField(u'就博會日期', default=datetime.date.today)
    jobfair_start = models.TimeField(u'就博會開始時間')
    jobfair_end = models.TimeField(u'就博會結束時間')
    jobfair_place = models.CharField(u'就博會地點', max_length=150, default="")
    jobfair_online_start = models.DateField(u'線上就博會開始日期', default=datetime.date.today)
    jobfair_online_end = models.DateField(u'線上就博會結束日期', default=datetime.date.today)
    # 費用
    jobfair_booth_fee = models.IntegerField(u'就博會攤位費用(每攤)', default=0)
    jobfair_online_fee = models.IntegerField(u'線上就博會費用', default=0)

    seminar_btn_start = models.DateField(u'說明會按鈕開啟日期', null=True)
    seminar_btn_end = models.DateField(u'說明會按鈕關閉日期', null=True)
    jobfair_btn_start = models.DateField(u'就博會按鈕開啟日期', null=True)
    jobfair_btn_end = models.DateField(u'就博會按鈕關閉日期', null=True)

    class Meta:
        managed = True
        verbose_name = u'校徵活動設定'
        verbose_name_plural = u'校徵活動設定'


class RecruitSignup(models.Model):
    SEMINAR_CHOICES = (
        (u'none', u'不參加說明會'),
        (u'noon', u'12:10場'),
        (u'other', u'其餘場'),
    )
    cid = models.CharField(u'公司統一編號', max_length=8, unique=True)
    seminar = models.CharField(u'說明會場次', choices=SEMINAR_CHOICES, max_length=15, default='none')
    seminar_online = models.BooleanField(u'線上說明會', default=False)
    jobfair = models.IntegerField(u'徵才展示會攤位數量', default=0)
    jobfair_online = models.BooleanField(u'線上就博會', default=False)
    career_tutor = models.BooleanField(u'企業職場導師')
    company_visit = models.BooleanField(u'企業參訪')
    lecture = models.BooleanField(u'就業力講座')
    payment = models.BooleanField(u'完成付款', default=False)
    receipt_no = models.CharField(u'收據號碼', blank=True, null=True, max_length=50)
    receipt_year = models.CharField(u'收據年份', max_length=4, default="", help_text="例如: 2020或109，須先完成繳費方可開立收據")
    ps = models.TextField(u'備註', blank=True, null=True)
    added = models.TimeField(u'報名時間', auto_now_add=True)
    updated = models.TimeField(u'更新時間', auto_now=True)

    def __str__(self):
        try:
            company = Company.objects.get(cid=self.cid)
        except:
            return "資料庫不同步，請連絡資訊組"
        return company.shortname

    def get_company_name(self):
        com = Company.objects.filter(cid=self.cid).first()
        return "資料庫不同步，請連絡資訊組" if com is None else com.shortname

    def get_company(self):
        com = Company.objects.filter(cid=self.cid).first()
        return "資料庫不同步，請連絡資訊組" if com is None else com

    class Meta:
        managed = True
        verbose_name = u'活動報名情況'
        verbose_name_plural = u'活動報名情況'


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
    category = models.CharField(u'類別', max_length=37, choices=CATEGORYS)
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
    # (value in db,display name)
    SESSIONS = (
        ("other1", "中午場1"),
        ("noon2", "中午場2"),
        ("other2", "中午場3"),
        ("other3", "晚場1"),
        ("other4", "晚場2"),
        ("other5", "晚場3"),
        ("extra", "加(補)場"),
        ("jobfair", "就博會"),  # 因為集點需要，公司留空
    )
    id = models.AutoField(primary_key=True)
    date = models.DateField(u'日期')
    session = models.CharField(u'時段', max_length=10, choices=SESSIONS)
    company = models.OneToOneField('RecruitSignup', to_field='cid',
                                   verbose_name=u'公司',
                                   on_delete=models.CASCADE, null=True, blank=True)
    place = models.ForeignKey('SlotColor', null=True, blank=True,
                              verbose_name=u'場地',
                              )
    points = models.SmallIntegerField(u'集點點數', default=1)
    updated = models.DateTimeField(u'更新時間', auto_now=True)

    class Meta:
        managed = True
        verbose_name = u"說明會場次"
        verbose_name_plural = u"說明會場次"

    def __str__(self):
        return '{} {}'.format(self.date, self.session)


class OnlineSeminarSlot(models.Model):
    # (value in db,display name)
    SESSIONS = (
        ("other1", "中午場1"),
        ("noon2", "中午場2"),
        ("other2", "中午場3"),
        ("other3", "晚場1"),
        ("other4", "晚場2"),
        ("other5", "晚場3"),
        ("extra", "加(補)場"),
        ("jobfair", "就博會"),  # 因為集點需要，公司留空
    )
    id = models.AutoField(primary_key=True)
    date = models.DateField(u'日期')
    session = models.CharField(u'時段', max_length=10, choices=SESSIONS)
    company = models.OneToOneField('RecruitSignup', to_field='cid',
                                   verbose_name=u'公司',
                                   limit_choices_to={'seminar_online': True},
                                   on_delete=models.CASCADE, null=True, blank=True)
    place = models.ForeignKey('SlotColor', null=True, blank=True,
                              verbose_name=u'場地',
                              )
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
                                   on_delete=models.CASCADE,
                                   limit_choices_to=~Q(seminar='')
                                   )
    updated = models.DateTimeField(u'更新時間', auto_now=True)

    class Meta:
        managed = True
        verbose_name = u"說明會選位順序"
        verbose_name_plural = u"說明會選位順序"


class JobfairOrder(models.Model):
    id = models.AutoField(primary_key=True)
    time = models.DateTimeField(u'選位開始時間')
    company = models.OneToOneField(RecruitSignup, to_field='cid',
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
    company = models.OneToOneField(RecruitSignup, verbose_name=u'公司')
    sign_name = models.CharField(u'攤位招牌名稱', max_length=20)
    contact_person = models.CharField(u'聯絡人', max_length=10)
    contact_mobile = models.CharField(u'聯絡人手機', max_length=32)
    contact_email = models.EmailField(u'聯絡人Email', max_length=128)
    packing_tickets = models.IntegerField(u'停車證數量')
    job_number = models.SmallIntegerField(u'職缺人數', default=0)
    general_lunch_box = models.SmallIntegerField(u'葷食便當數量', default=0)
    veget_lunch_box = models.IntegerField(u'素食便當')
    power_req = models.CharField(u'用電需求', max_length=128, blank=True, null=True)
    long_table = models.IntegerField(u'長桌', default=2)
    chair = models.IntegerField(u'椅子', default=5)
    doily = models.IntegerField(u'紅桌巾', default=1)
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
    company = models.OneToOneField(RecruitSignup, verbose_name=u'公司')
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
    speaker_email = models.EmailField(u'主講人Email', max_length=254)
    raffle_prize = models.CharField(u'抽獎獎品', max_length=254,
                                    null=True, blank=True)
    raffle_prize_amount = models.SmallIntegerField(u'抽獎獎品數量', default=0)
    qa_prize = models.CharField(u'QA獎獎品', max_length=254, null=True, blank=True)
    qa_prize_amount = models.SmallIntegerField(u'QA獎獎品數量', default=0)
    attend_prize = models.CharField(u'參加獎獎品', max_length=254,
                                    null=True, blank=True)
    attend_prize_amount = models.SmallIntegerField(u'參加獎獎品數量', default=0)
    snack_box = models.SmallIntegerField(u'加碼餐盒數量', default=0)
    contact = models.CharField(u'聯絡人', max_length=30)
    contact_mobile = models.CharField(u'聯絡人手機', max_length=16)
    contact_email = models.EmailField(u'聯絡人Email', max_length=254)
    parking_cards = models.SmallIntegerField(u'汽車停車卡數量', default=0)
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
        verbose_name = u'贊助品'
        verbose_name_plural = u'贊助品'


class SponsorShip(models.Model):
    company = models.ForeignKey(RecruitSignup, to_field='cid', on_delete=models.CASCADE)
    sponsor_item = models.ForeignKey(SponsorItem, to_field='name', on_delete=models.CASCADE)
    updated = models.DateTimeField(u'更新時間', auto_now=True)

    class Meta:
        verbose_name = u'贊助情況'
        verbose_name_plural = u'贊助情況'
        unique_together = ('company', 'sponsor_item')


class CompanySurvey(models.Model):
    RATING = (
        (u'優', u'優'),
        (u'佳', u'佳'),
        (u'普通', u'普通'),
        (u'差', u'差'),
        (u'劣', u'劣'),
    )

    english_name = models.CharField(u'公司英文名稱', blank=True, null=True, max_length=255)
    # os = overseas, osc = overseas chinese, cn = china
    os_serve = models.BooleanField(u'境外生參與活動', default=False)
    os_for_ftime = models.BooleanField(u'外籍生正職', default=False)
    os_osc_ftime = models.BooleanField(u'僑生正職', default=False)
    os_cn_ftime = models.BooleanField(u'陸生正職', default=False)
    os_for_intern = models.BooleanField(u'外籍生實習', default=False)
    os_osc_intern = models.BooleanField(u'僑生實習', default=False)
    os_cn_intern = models.BooleanField(u'陸生實習', default=False)
    os_other_required = models.CharField(u'境外生能力要求', blank=True, null=True, max_length=255)
    os_seminar = models.BooleanField(u'外籍生說明會', default=False)

    ee_bachelor = models.IntegerField(u'電機學院-大學人數', default=0)
    ee_master = models.IntegerField(u'電機學院-碩士人數', default=0)
    ee_phd = models.IntegerField(u'電機學院-博士人數', default=0)
    ee_satisfaction = models.CharField(u'電機學院 - 平均滿意度', max_length=2, choices=RATING,
                                       null=True, blank=True
                                       )
    cs_bachelor = models.IntegerField(u'資訊學院-大學人數', default=0)
    cs_master = models.IntegerField(u'資訊學院-碩士人數', default=0)
    cs_phd = models.IntegerField(u'資訊學院-博士人數', default=0)
    cs_satisfaction = models.CharField(u'資訊學院 - 平均滿意度', max_length=2, choices=RATING,
                                       null=True, blank=True)
    manage_bachelor = models.IntegerField(u'管理學院-大學人數', default=0)
    manage_master = models.IntegerField(u'管理學院-碩士人數', default=0)
    manage_phd = models.IntegerField(u'管理學院-博士人數', default=0)
    manage_satisfaction = models.CharField(u'管理學院 - 平均滿意度', max_length=2, choices=RATING,
                                           null=True, blank=True)
    ls_bachelor = models.IntegerField(u'生命科學院-大學人數', default=0)
    ls_master = models.IntegerField(u'生命科學院-碩士人數', default=0)
    ls_phd = models.IntegerField(u'生命科學院-博士人數', default=0)
    ls_satisfaction = models.CharField(u'生命科學院 - 平均滿意度', max_length=2, choices=RATING,
                                       null=True, blank=True)
    bio_bachelor = models.IntegerField(u'生物科技學院-大學人數', default=0)
    bio_master = models.IntegerField(u'生物科技學院-碩士人數', default=0)
    bio_phd = models.IntegerField(u'生物科技學院-博士人數', default=0)
    bio_satisfaction = models.CharField(u'生物科技學院 - 平均滿意度', max_length=2, choices=RATING,
                                        null=True, blank=True)
    bse_bachelor = models.IntegerField(u'生物醫學暨工程學院-大學人數', default=0)
    bse_master = models.IntegerField(u'生物醫學暨工程學院-碩士人數', default=0)
    bse_phd = models.IntegerField(u'生物醫學暨工程學院-博士人數', default=0)
    bse_satisfaction = models.CharField(u'生物醫學暨工程學院 - 平均滿意度', max_length=2, choices=RATING,
                                        null=True, blank=True)
    sci_bachelor = models.IntegerField(u'理學院-大學人數', default=0)
    sci_master = models.IntegerField(u'理學院-碩士人數', default=0)
    sci_phd = models.IntegerField(u'理學院-博士人數', default=0)
    sci_satisfaction = models.CharField(u'理學院 - 平均滿意度', max_length=2, choices=RATING,
                                        null=True, blank=True)
    eng_bachelor = models.IntegerField(u'工學院-大學人數', default=0)
    eng_master = models.IntegerField(u'工學院-碩士人數', default=0)
    eng_phd = models.IntegerField(u'工學院-博士人數', default=0)
    eng_satisfaction = models.CharField(u'工學院 - 平均滿意度', max_length=2, choices=RATING,
                                        null=True, blank=True)
    hs_bachelor = models.IntegerField(u'人文社會學院-大學人數', default=0)
    hs_master = models.IntegerField(u'人文社會學院-碩士人數', default=0)
    hs_phd = models.IntegerField(u'人文社會學院-博士人數', default=0)
    hs_satisfaction = models.CharField(u'人文社會學院 - 平均滿意度', max_length=2, choices=RATING,
                                       null=True, blank=True)
    hss_bachelor = models.IntegerField(u'人文與社會科學院-大學人數', default=0)
    hss_master = models.IntegerField(u'人文與社會科學院-碩士人數', default=0)
    hss_phd = models.IntegerField(u'人文與社會科學院-博士人數', default=0)
    hss_satisfaction = models.CharField(u'人文與社會科學院 - 平均滿意度', max_length=2, choices=RATING,
                                        null=True, blank=True)
    haka_bachelor = models.IntegerField(u'客家學院-大學人數', default=0)
    haka_master = models.IntegerField(u'客家學院-碩士人數', default=0)
    haka_phd = models.IntegerField(u'客家學院-博士人數', default=0)
    haka_satisfaction = models.CharField(u'客家學院 - 平均滿意度', max_length=2, choices=RATING,
                                         null=True, blank=True)
    den_bachelor = models.IntegerField(u'牙醫學院-大學人數', default=0)
    den_master = models.IntegerField(u'牙醫學院-碩士人數', default=0)
    den_phd = models.IntegerField(u'牙醫學院-博士人數', default=0)
    den_satisfaction = models.CharField(u'牙醫學院 - 平均滿意度', max_length=2, choices=RATING,
                                        null=True, blank=True)
    pho_bachelor = models.IntegerField(u'光電學院-大學人數', default=0)
    pho_master = models.IntegerField(u'光電學院-碩士人數', default=0)
    pho_phd = models.IntegerField(u'光電學院-博士人數', default=0)
    pho_satisfaction = models.CharField(u'光電學院 - 平均滿意度', max_length=2, choices=RATING,
                                        null=True, blank=True)
    law_bachelor = models.IntegerField(u'科技法律學院-大學人數', default=0)
    law_master = models.IntegerField(u'科技法律學院-碩士人數', default=0)
    law_phd = models.IntegerField(u'科技法律學院-博士人數', default=0)
    law_satisfaction = models.CharField(u'科技法律學院 - 平均滿意度', max_length=2, choices=RATING,
                                        null=True, blank=True)
    fse_bachelor = models.IntegerField(u'前瞻系統工程教育院-大學人數', default=0)
    fse_master = models.IntegerField(u'前瞻系統工程教育院-碩士人數', default=0)
    fse_phd = models.IntegerField(u'前瞻系統工程教育院-博士人數', default=0)
    fse_satisfaction = models.CharField(u'前瞻系統工程教育院 - 平均滿意度', max_length=2, choices=RATING,
                                        null=True, blank=True)
    icst_bachelor = models.IntegerField(u'國際半導體學院-大學人數', default=0)
    icst_master = models.IntegerField(u'國際半導體學院-碩士人數', default=0)
    icst_phd = models.IntegerField(u'國際半導體學院-博士人數', default=0)
    icst_satisfaction = models.CharField(u'國際半導體學院 - 平均滿意度', max_length=2, choices=RATING,
                                         null=True, blank=True)
    ai_bachelor = models.IntegerField(u'智慧科技暨綠能學院-大學人數', default=0)
    ai_master = models.IntegerField(u'智慧科技暨綠能學院-碩士人數', default=0)
    ai_phd = models.IntegerField(u'智慧科技暨綠能學院-博士人數', default=0)
    ai_satisfaction = models.CharField(u'智慧科技暨綠能學院 - 平均滿意度', max_length=2, choices=RATING,
                                       null=True, blank=True)
    som_bachelor = models.IntegerField(u'醫學院-大學人數', default=0)
    som_master = models.IntegerField(u'醫學院-碩士人數', default=0)
    som_phd = models.IntegerField(u'醫學院-博士人數', default=0)
    som_satisfaction = models.CharField(u'醫學院 - 平均滿意度', max_length=2, choices=RATING,
                                        null=True, blank=True)
    ps_bachelor = models.IntegerField(u'藥物科學院-大學人數', default=0)
    ps_master = models.IntegerField(u'藥物科學院-碩士人數', default=0)
    ps_phd = models.IntegerField(u'藥物科學院-博士人數', default=0)
    ps_satisfaction = models.CharField(u'藥物科學院 - 平均滿意度', max_length=2, choices=RATING,
                                       null=True, blank=True)
    son_bachelor = models.IntegerField(u'護理學院-大學人數', default=0)
    son_master = models.IntegerField(u'護理學院-碩士人數', default=0)
    son_phd = models.IntegerField(u'護理學院-博士人數', default=0)
    son_satisfaction = models.CharField(u'護理學院 - 平均滿意度', max_length=2, choices=RATING,
                                        null=True, blank=True)
    overall_satisfaction = models.CharField(u'整體滿意度', max_length=2, choices=RATING, null=True, blank=True)

    # salary
    SALARY_MONTH = (
        (u'4萬以下', u'4萬以下'),
        (u'4~5萬', u'4~5萬'),
        (u'5~6萬', u'5~6萬'),
        (u'6萬以上', u'6萬以上'),
    )
    SALARY_YEAR = (
        (u'50萬以下', u'50萬以下'),
        (u'50~70萬', u'50~70萬'),
        (u'70~100萬', u'70~100萬'),
        (u'100萬以上', u'100萬以上'),
    )
    salary_avg_bachelor = models.CharField(u'大學平均月薪', max_length=8, choices=SALARY_MONTH)
    salary_avg_master = models.CharField(u'碩士平均月薪', max_length=8, choices=SALARY_MONTH)
    salary_avg_phd = models.CharField(u'博士平均月薪', max_length=8, choices=SALARY_MONTH)
    nctu_salary_avg_bachelor = models.CharField(u'大學平均年薪', max_length=8, choices=SALARY_YEAR)
    nctu_salary_avg_master = models.CharField(u'碩士平均年薪', max_length=8, choices=SALARY_YEAR)
    nctu_salary_avg_phd = models.CharField(u'博士平均年薪', max_length=8, choices=SALARY_YEAR)

    # ability
    no_nctu_employee = models.BooleanField(u'目前無交大畢業生在職')
    professional_skill_rate = models.CharField(u'專業知能', max_length=4, choices=RATING, null=True, blank=True)
    foreign_lang_rate = models.CharField(u'外語能力', max_length=4, choices=RATING, null=True, blank=True)
    document_process_rate = models.CharField(u'文書處理', max_length=4, choices=RATING, null=True, blank=True)
    info_literacy_rate = models.CharField(u'資訊素養', max_length=4, choices=RATING, null=True, blank=True)
    problem_solving_rate = models.CharField(u'發現及解決問題', max_length=4, choices=RATING, null=True, blank=True)
    attitude_rate = models.CharField(u'工作態度', max_length=4, choices=RATING, null=True, blank=True)
    civic_duty_rate = models.CharField(u'公民責任', max_length=4, choices=RATING, null=True, blank=True)
    pro_moral_rate = models.CharField(u'專業倫理', max_length=4, choices=RATING, null=True, blank=True)
    humanities_rate = models.CharField(u'人文及在地關懷', max_length=4, choices=RATING, null=True, blank=True)
    cultural_rate = models.CharField(u'人文藝術陶冶', max_length=4, choices=RATING, null=True, blank=True)
    international_view_rate = models.CharField(u'國際視野', max_length=4, choices=RATING, null=True, blank=True)
    diverse_thinking_rate = models.CharField(u'跨界多元思考', max_length=4, choices=RATING, null=True, blank=True)
    group_cognitive_rate = models.CharField(u'群己平衡認知', max_length=4, choices=RATING, null=True, blank=True)

    # ability choice
    professional_skill = models.BooleanField(u'專業知能')
    foreign_lang = models.BooleanField(u'外語能力')
    document_process = models.BooleanField(u'文書處理')
    info_literacy = models.BooleanField(u'資訊素養')
    problem_solving = models.BooleanField(u'發現及解決問題')
    attitude = models.BooleanField(u'工作態度')
    civic_duty = models.BooleanField(u'公民責任')
    pro_moral = models.BooleanField(u'專業倫理')
    humanities = models.BooleanField(u'人文及在地關懷')
    cultural = models.BooleanField(u'人文藝術陶冶')
    international_view = models.BooleanField(u'國際視野')
    diverse_thinking = models.BooleanField(u'跨界多元思考')
    group_cognitive = models.BooleanField(u'群己平衡認知')
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
    work_exp = models.CharField(u'相關工作經驗（打工、習實）', max_length=4, choices=HELPFUL_RATE)
    travel_study = models.CharField(u'遊學（如交換學生）', max_length=4, choices=HELPFUL_RATE)

    # ways to recruit
    hr_bank = models.BooleanField(u'人力銀行')
    newspaper_ad = models.BooleanField(u'報章廣告')
    website = models.BooleanField(u'公司網頁')
    school = models.BooleanField(u'學校宣傳')
    teacher_recommend = models.BooleanField(u'老師推薦')
    campus_jobfair = models.BooleanField(u'校園徵才')
    contest = models.BooleanField(u'競賽活動')

    # receive info
    receive_info = models.BooleanField(u'我希望定期接收校園徵才活動訊息')
    suggestions = models.CharField(u'其它建議', max_length=150, blank=True, null=True)

    # basic info
    cid = models.CharField(u'公司統一編號', unique=True, max_length=8, null=False)
    company = models.CharField(u'企業名稱', max_length=50)
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
    # plan_to_recruit     = models.IntegerField(u'2017年預計招募職缺數', help_text="此數據不會對外公開，僅供主辦單位內部作業統計用途。")
    nctu_employees = models.IntegerField(u'交大校友人數')
    category = models.CharField(u'企業類別', max_length=10, choices=CATEGORYS)
    updated = models.DateTimeField(u'更新時間', auto_now=True)

    class Meta:
        managed = True
        verbose_name = u"企業滿意度問卷"
        verbose_name_plural = u"企業滿意度問卷"


class SlotColor(models.Model):
    id = models.AutoField(primary_key=True)
    place = models.CharField(u'場地', max_length=20, unique=True)
    css_color = models.CharField(u'文字顏色(css)', max_length=20, help_text=
    '''請輸入顏色英文，比如: red, green, blue, purple, black等'''
                                 )
    place_info = models.URLField(u'場地介紹網頁', max_length=256, default="http://")

    class Meta:
        managed = True
        verbose_name = u"場地顏色及資訊"
        verbose_name_plural = u"場地顏色及資訊"

    def __str__(self):
        return self.place


class Student(models.Model):
    card_num = models.CharField(u'學生證卡號', max_length=20, primary_key=True)
    student_id = models.CharField(u'學號', max_length=10, blank=True, null=True)
    phone = models.CharField(u'手機', max_length=15, blank=True, null=True)
    name = models.CharField(u'姓名', max_length=30, blank=True, null=True)
    department = models.CharField(u'系級', max_length=20, blank=True, null=True)
    attendance = models.ManyToManyField(SeminarSlot, through='StuAttendance')

    def get_redeem_points(self):
        redeem_records = ExchangePrize.objects.filter(student=self)
        redeem_points = sum([i.points for i in redeem_records])
        return redeem_points

    def get_points(self):
        points = sum([i.points for i in self.attendance.all()])
        redeem_records = ExchangePrize.objects.filter(student=self)
        redeem_points = sum([i.points for i in redeem_records])
        return points - redeem_points

    def redeem_points(self):
        redeem_records = ExchangePrize.objects.filter(student=self)
        redeem_points = sum([i.points for i in redeem_records])
        return redeem_points

    class Meta:
        verbose_name = u'說明會學生'
        verbose_name_plural = u'說明會學生'

    def __str__(self):
        return self.card_num


class StuAttendance(models.Model):
    student = models.ForeignKey(Student, to_field='card_num')
    seminar = models.ForeignKey(SeminarSlot, to_field='id')

    class Meta:
        unique_together = ('student', 'seminar')


class ExchangePrize(models.Model):
    student = models.ForeignKey(Student, to_field='card_num', verbose_name='u學生證卡號')
    points = models.IntegerField(u'所需點數')
    prize = models.CharField(u'獎品', max_length=100)

    class Meta:
        verbose_name = u'兌獎紀錄'
        verbose_name_plural = u'兌獎紀錄'


class RecruitInfo(models.Model):
    title = models.CharField(u'標題', default='', max_length=10)
    content = RichTextField(u'內容', default='', null=True, blank=True)
    updated = models.DateTimeField(u'更新時間', auto_now=True)

    def __str__(self):
        return "Recruit_Info"

    class Meta:
        managed = True
        verbose_name = u"校徵活動資訊"
        verbose_name_plural = u"校徵活動資訊"


class RecruitCompanyInfo(models.Model):
    title = models.CharField(u'標題', default='', max_length=10)
    content = RichTextField(u'內容', default='', null=True, blank=True)
    updated = models.DateTimeField(u'更新時間', auto_now=True)

    def __str__(self):
        return "Recruit_Company_Info"

    class Meta:
        managed = True
        verbose_name = u"校徵活動資訊(公司)"
        verbose_name_plural = u"校徵活動資訊(公司)"


class RecruitSeminarInfo(models.Model):
    title = models.CharField(u'標題', default='', max_length=10)
    content = RichTextField(u'內容', default='', null=True, blank=True)
    updated = models.DateTimeField(u'更新時間', auto_now=True)

    def __str__(self):
        return "Recruit_Seminar_Info"

    class Meta:
        managed = True
        verbose_name = u"說明會資訊編輯頁面"
        verbose_name_plural = u"說明會資訊編輯頁面"


class RecruitOnlineSeminarInfo(models.Model):
    title = models.CharField(u'標題', default='', max_length=10)
    content = RichTextField(u'內容', default='', null=True, blank=True)
    updated = models.DateTimeField(u'更新時間', auto_now=True)

    def __str__(self):
        return "Recruit_Online_Seminar_Info"

    class Meta:
        managed = True
        verbose_name = u"線上說明會資訊編輯頁面"
        verbose_name_plural = u"線上說明會資訊編輯頁面"


class RecruitJobfairInfo(models.Model):
    title = models.CharField(u'標題', default='', max_length=10)
    content = RichTextField(u'內容', default='', null=True, blank=True)
    updated = models.DateTimeField(u'更新時間', auto_now=True)

    def __str__(self):
        return "Recruit_Jobfair_Info"

    class Meta:
        managed = True
        verbose_name = u"就博會資訊編輯頁面"
        verbose_name_plural = u"就博會資訊編輯頁面"


class RecruitOnlineJobfairInfo(models.Model):
    title = models.CharField(u'標題', default='', max_length=10)
    content = RichTextField(u'內容', default='', null=True, blank=True)
    updated = models.DateTimeField(u'更新時間', auto_now=True)

    def __str__(self):
        return "Recruit_Online_Jobfair_Info"

    class Meta:
        managed = True
        verbose_name = u"線上就博會資訊編輯頁面"
        verbose_name_plural = u"線上就博會資訊編輯頁面"
