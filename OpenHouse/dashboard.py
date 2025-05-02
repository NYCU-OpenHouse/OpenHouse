from django.utils.translation import ugettext_lazy as _
from jet.dashboard import modules
from jet.dashboard.dashboard import Dashboard, AppIndexDashboard


class CustomDashboard(Dashboard):
    columns = 3

    def init_with_context(self, context):
        self.available_children.append(modules.LinkList)
        self.add_export_dashboard()

    def add_export_dashboard(self):
        self.children.append(modules.LinkList(
            _('網站監控'),
            children=[
                {
                    'title': _('網站流量監控(Nginx)'),
                    'url': '/grafana/d/Nz6kKgtGj/grafana-loki-dashboard-for-nginx-service-mesh?orgId=1',
                    'external': False,
                },
                {
                    'title': _('網站操作監控(Django)'),
                    'url': '/grafana/d/hchV4t2Iz/oh_django?orgId=1',
                    'external': False,
                },
            ],
            column=0,
            order=0
        ))
        self.children.append(modules.LinkList(
            _('企業列表'),
            children=[
                {
                    'title': _('已註冊中資公司'),
                    'url': '/admin/company/company/registered_chinese_funded_company/',
                    'external': False,
                },
            ],
            column=0,
            order=0
        ))
        self.children.append(modules.LinkList(
            _('其它匯出'),
            children=[
                {
                    'title': _('總廠商列表'),
                    'url': '/admin/company/company/export/',
                    'external': False,
                },
            ],
            column=0,
            order=0
        ))
        self.children.append(modules.LinkList(
            _('春徵匯出'),
            children=[
                {
                    'title': _('匯出全部資料'),
                    'url': '/admin/recruit/export_all/',
                    'external': False,
                },
                {
                    'title': _('匯出實體說明會資訊'),
                    'url': '/admin/recruit/export_seminar_info/',
                    'external': False,
                },
                {
                    'title': _('匯出線上說明會資訊'),
                    'url': '/admin/recruit/export_online_seminar_info/',
                    'external': False,
                },
                {
                    'title': _('匯出實體就博會資訊'),
                    'url': '/admin/recruit/export_jobfair_info/',
                    'external': False,
                },

                {
                    'title': _('廠商Logo和簡介(廣告用)'),
                    'url': '/admin/recruit/export_ad/',
                    'external': False,
                },
                {
                    'title': _('廠商滿意度問卷'),
                    'url': '/admin/recruit/companysurvey/export/',
                    'external': False,
                },
                {
                    'title': _('廠商職缺匯出'),
                    'url': '/admin/recruit/export_jobs/',
                    'external': False,
                },
            ],
            column=1,
            order=1
        ))
        self.children.append(modules.LinkList(
            _('企業參訪匯出'),
            children=[
                {
                    'title': _('匯出學生登記狀況'),
                    'url': '/admin/company_visit/student_signup_status/list',
                    'external': False,
                },
            ],
            column=0,
            order=1
        ))
        self.children.append(modules.LinkList(
            _('職場導師匯出'),
            children=[
                {
                    'title': _('匯出學生登記狀況'),
                    'url': '/admin/careermentor/student_signup_status/list',
                    'external': False,
                },
            ],
            column=0,
            order=1
        ))
        self.children.append(modules.LinkList(
            _('春徵集點'),
            children=[
                {
                    'title': _('春徵說明會集點'),
                    'url': '/admin/recruit/collect_points/',
                    'external': False,
                },
                {
                    'title': _('學生證註冊'),
                    'url': '/admin/recruit/reg_card/',
                    'external': False,
                },
                {
                    'title': _('批量操作學生卡號資訊'),
                    'url': '/admin/recruit/import_student_card_info/',
                    'external': False,
                },
                {
                    'title': _('兌換獎品'),
                    'url': '/admin/recruit/exchange_prize',
                    'external': False,
                },
                {
                    'title': _('兌獎-每日參與說明會獎品'),
                    'url': '/admin/recruit/show_student_with_daily_seminar_prize/',
                    'external': False,
                },
                {
                    'title': _('各場次學生登記總覽'),
                    'url': '/admin/recruit/seminar_attended_student/',
                    'external': False,
                },
                {
                    'title': _('匯出集點資料'),
                    'url': '/admin/recruit/export_points_info/',
                    'external': False,
                },
                {
                    'title': _('讀卡程式及驅動'),
                    'url': 'http://web.infothink.com.tw/tw/download',
                    'external': True,
                },
            ],
            column=1,
            order=1
        ))
        self.children.append(modules.LinkList(
            _('秋招匯出'),
            children=[
                {
                    'title': _('匯出全部資料'),
                    'url': '/admin/rdss/export_all/',
                    'external': False,
                },
                {
                    'title': _('廠商Logo和簡介(廣告用)'),
                    'url': '/admin/rdss/export_ad/',
                    'external': False,
                },
                {
                    'title': _('廠商贊助統整'),
                    'url': '/admin/rdss/sponsorship_situation',
                    'external': False,
                },
                {
                    'title': _('廠商滿意度問卷'),
                    'url': '/admin/rdss/companysurvey/export/',
                    'external': False,
                },
                {
                    'title': _('說明會資料匯出'),
                    'url': '/admin/rdss/export_seminar/',
                    'external': False,
                },
                {
                    'title': _('就博會資料匯出'),
                    'url': '/admin/rdss/export_jobfair/',
                    'external': False,
                },
                {
                    'title': _('廠商職缺匯出'),
                    'url': '/admin/rdss/export_jobs/',
                    'external': False,
                },
            ],
            column=2,
            order=1
        ))
        self.children.append(modules.LinkList(
            _('秋招集點'),
            children=[
                {
                    'title': _('秋招說明會集點'),
                    'url': '/admin/rdss/collect_points/',
                    'external': False,
                },
                {
                    'title': _('學生證註冊'),
                    'url': '/admin/rdss/reg_card/',
                    'external': False,
                },
                {
                    'title': _('批量操作學生卡號資訊'),
                    'url': '/admin/rdss/import_student_card_info/',
                    'external': False,
                },
                {
                    'title': _('兌獎'),
                    'url': '/admin/rdss/redeem/',
                    'external': False,
                },
                {
                    'title': _('兌獎-每日參與說明會獎品'),
                    'url': '/admin/rdss/show_student_with_daily_seminar_prize/',
                    'external': False,
                },
                {
                    'title': _('各場次學生登記總覽'),
                    'url': '/admin/rdss/seminar_attended_student/',
                    'external': False,
                },
                {
                    'title': _('匯出集點資料'),
                    'url': '/admin/rdss/export_points_info/',
                    'external': False,
                },
                {
                    'title': _('讀卡程式及驅動'),
                    'url': 'http://web.infothink.com.tw/tw/download',
                    'external': True,
                },
            ],
            column=2,
            order=1
        ))


class CustomAppDashboard(AppIndexDashboard):
    columns = 2

    def init_with_context(self, context):
        self.available_children.append(modules.LinkList)

        my_app_name = self.models()[0][:-2]
        my_app = None
        for app in context['available_apps']:
            if app['app_label'] == my_app_name:
                my_app = app
                break

        other, physical, online, student = [], [], [], []
        student_models = [
            'Student',
            'StuAttendance',
            # rdss
            'RedeemPrize',
            'redeem_prize_2024_3_points_per_day',
            # recruit
            'ExchangePrize',
            'RedeemDailyPrize',
            ]
        for m in my_app['models']:
            object_name = m['object_name']
            lower_object_name = object_name.lower()
            if 'temp' in lower_object_name:
                # Hide temporary models
                continue
            if 'online' in lower_object_name:
                online.append(my_app_name + '.' + object_name)
            elif ('seminar' in lower_object_name and 'ece' not in lower_object_name) or 'jobfair' in lower_object_name:
                physical.append(my_app_name + '.' + object_name)
            elif object_name in student_models:
                student.append(my_app_name + '.' + object_name)
            else:
                other.append(my_app_name + '.' + object_name)

        self.children.append(modules.ModelList(
            title=_('其他設定'),
            models=other,
            column=0,
            order=0
        ))

        self.children.append(modules.ModelList(
            title=_('實體'),
            models=physical,
            column=0,
            order=1
        ))
        self.children.append(modules.ModelList(
            title=_('說明會學生'),
            models=student,
            column=0,
            order=2
        ))
        self.children.append(modules.ModelList(
            title=_('線上'),
            models=online,
            column=0,
            order=3
        ))
        self.children.append(modules.RecentActions(
            include_list=self.get_app_content_types(),
            column=1,
            order=0
        ))
