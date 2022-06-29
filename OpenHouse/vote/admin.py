from django.contrib import admin
from . import models

@admin.register(models.Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display=('name',)
@admin.register(models.Vote)
class VoteAdmin(admin.ModelAdmin):
    pass
@admin.register(models.VoteInfo)
class VoteContentAdmin(admin.ModelAdmin):
    list_display=('title',)
    def has_add_permission(self, request):
        count = models.VoteInfo.objects.all().count()
        if count ==0:
            return True
        return False
