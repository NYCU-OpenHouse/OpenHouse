from __future__ import unicode_literals
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractBaseUser, UserManager
from django.core.validators import RegexValidator, MinLengthValidator, validate_email
from django.utils import timezone
from datetime import datetime


def validate_all_num(string):
    if not string.isdigit():
        raise ValidationError('必需都是數字')


def validate_mobile(string):
    RegexValidator(regex='^\d{4}-\d{6}$', message='手機格式為：0987-654321')(string)


def validate_phone(string):
    RegexValidator(regex='^\d+-\d+(#\d+)?$', message='電話/傳真格式為：區碼-號碼#分機')(string)


class Company(AbstractBaseUser):
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
        (u'政府/國防/財團法人研究單位', u'政府/國防/財團法人研究單位'),
        (u'住宿/餐飲業', u'住宿/餐飲業'),
        (u'批發及零售/運輸及倉儲業', u'批發及零售/運輸及倉儲業'),
        (u'電力及燃氣供應業', u'電力及燃氣供應業'),
    )

    id = models.AutoField(primary_key=True)
    cid = models.CharField(u'公司統一編號', unique=True, max_length=8)
    name = models.CharField(u'公司名稱', max_length=64)
    english_name = models.CharField(u'公司英文完整名稱', max_length=100, default='None')
    shortname = models.CharField(u'公司簡稱', max_length=20)
    category = models.CharField(u'類別', max_length=37, choices=CATEGORYS, help_text='公司主要事業類別')
    phone = models.CharField(u'公司電話', max_length=32, help_text='格式: 區碼-號碼#分機')
    postal_code = models.CharField(u'郵遞區號(3+3)', max_length=6,help_text='ex:300123', validators=[validate_all_num])
    address = models.CharField(u'公司地址', max_length=128)
    website = models.CharField(u'公司網站', max_length=64)
    brief = models.CharField(u'公司簡介', max_length=200, help_text='為了印刷效果，限200字內')
    recruit_info = models.CharField(u'職缺內容', max_length=260, help_text='為了印刷效果，限260字內')
    recruit_url = models.CharField(u'應徵方式', max_length=260, help_text='報名網站或詳細職缺說明, 限260字內', blank=True)
    business_project = models.CharField(u'營業項目', max_length=100, default="", blank=True)
    relation_business = models.CharField(u'關係企業', max_length=64, help_text='若無, 可免填', blank=True, default="")
    subsidiary = models.CharField(u'分公司', max_length=64, help_text='若無, 可免填', blank=True, default="")
    hr_name = models.CharField(u'人資姓名', max_length=32)
    hr_phone = models.CharField(u'人資電話', max_length=32, help_text='格式: 區碼-號碼#分機')
    hr_fax = models.CharField(u'人資傳真', max_length=32, help_text='格式: 區碼-號碼#分機')
    hr_mobile = models.CharField(u'人資手機', max_length=32, help_text='格式: 0912-345678')
    hr_email = models.CharField(u'人資Email', max_length=64, validators=[validate_email])
    # hr spare
    hr2_name = models.CharField(u'第二位人資姓名', max_length=32, default="", blank=True)
    hr2_phone = models.CharField(u'第二位人資電話', max_length=32, default="", blank=True, help_text='格式: 區碼-號碼#分機')
    hr2_fax = models.CharField(u'第二位人資傳真', max_length=32, default="", blank=True, help_text='格式: 區碼-號碼#分機')
    hr2_mobile = models.CharField(u'第二位人資手機', max_length=32, default="", blank=True,
                                  help_text='格式: 0912-345678')
    hr2_email = models.CharField(u'第二位人資Email', max_length=64, default="", blank=True, validators=[validate_email])
    hr_ps = models.TextField(u'人員相關備註', default="", blank=True)
    logo = models.ImageField(u"公司LOGO", upload_to='company_logos', null=True,
                             help_text='''網站展示、筆記本內頁公司介紹使用，僅接受 jpg, png, gif 格式。建議解析度為 300 dpi以上，以達到最佳效果。''')

    payment_ps = models.TextField(u'款項備註', default="", blank=True)
    other_ps = models.TextField(u'其他備註', default="", blank=True)

    # discount for special member
    ece_member = models.BooleanField(u'電機資源產學聯盟', default=False)
    gloria_normal = models.BooleanField(u'國際產學聯盟總中心_一般會員', default=False)
    gloria_startup = models.BooleanField(u'國際產學聯盟總中心_國際新創會員', default=False)

    # receipt information
    receipt_title = models.CharField(u'公司收據抬頭', max_length=80, default="")
    receipt_postal_code = models.CharField(u'收據寄送郵遞區號(3+3)',help_text='ex:300123', max_length=6, default="",  validators=[validate_all_num])
    receipt_postal_address = models.CharField(u'收據寄送地址', max_length=128, default="", help_text="另註公司名尤佳")
    receipt_contact_name =  models.CharField(u'收據聯絡人姓名', max_length=10, default="")
    receipt_contact_phone = models.CharField(u'收據聯絡人公司電話', max_length=32, default="", help_text='格式: 區碼-號碼#分機')
    
    
    last_update = models.DateTimeField(u'更新時間', auto_now=True, null=True)
    date_join = models.DateTimeField(u'date joined', auto_now_add=True, null=True)
    objects = UserManager()
    USERNAME_FIELD = 'cid'

    class Meta:
        managed = True
        db_table = 'company'

        verbose_name = u"總廠商列表"
        verbose_name_plural = u"總廠商列表"  # 上面的複數ZZZ

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        return u'{0} - {1}'.format(self.cid, self.shortname)

    def get_short_name(self):
        return self.shortname

    def get_cid(self):  # for get cid
        return self.cid

    @property
    def username(self):
        return self.cid

    @property
    def is_staff(self):
        return False

    @property
    def is_company(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_superuser(self):
        return False

    def has_module_perms(self, app_label):
        return False

    def has_perm(self, perm, obj=None):
        return False

class ChineseFundedCompany(models.Model):
    cid = models.CharField(u'公司統一編號', unique=True, max_length=8)
    name = models.CharField(u'公司名稱', max_length=100)
    updated_time = models.DateTimeField(u'更新時間', auto_now=True)
    
    class Meta:
        managed = True
        db_table = 'chinesefundedcompany'

        verbose_name = u"中資企業列表"
        verbose_name_plural = u"中資企業列表"