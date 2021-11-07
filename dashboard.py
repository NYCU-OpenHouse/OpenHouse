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
            _('其它匯出'),
            children=[
                {
                    'title': _('總廠商列表'),
                    'url': '/admin/company/company/export/',
                    'external': False,
                },
            ],
            column=2,
            order=0
        ))
        self.children.append(modules.LinkList(
            _('校徵匯出'),
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
            ],
            column=2,
            order=1
        ))
        self.children.append(modules.LinkList(
            _('校徵集點'),
            children=[
                {
                    'title': _('校徵說明會集點'),
                    'url': '/admin/recruit/collect_points/',
                    'external': False,
                },
                {
                    'title': _('學生證註冊'),
                    'url': '/admin/recruit/reg_card/',
                    'external': False,
                },
                {
                    'title': _('兌換獎品'),
                    'url': '/admin/recruit/exchange_prize',
                    'external': False,
                },
            ],
            column=2,
            order=1
        ))
        self.children.append(modules.LinkList(
            _('研替匯出'),
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
            ],
            column=2,
            order=1
        ))
        self.children.append(modules.LinkList(
            _('研替集點'),
            children=[
                {
                    'title': _('研替說明會集點'),
                    'url': '/admin/rdss/collect_points/',
                    'external': False,
                },
                {
                    'title': _('學生證註冊'),
                    'url': '/admin/rdss/reg_card/',
                    'external': False,
                },
                {
                    'title': _('兌獎'),
                    'url': '/admin/rdss/redeem/',
                    'external': False,
                },
                {
                    'title': _('讀卡程式及驅動'),
                    'url': '/static/data/apps/card_reader.zip',
                    'external': False,
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

        other, physical, online = [], [], []
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
            title=_('線上'),
            models=online,
            column=0,
            order=2
        ))

        self.children.append(modules.RecentActions(
            include_list=self.get_app_content_types(),
            column=1,
            order=0
        ))
