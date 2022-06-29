from django.shortcuts import render
from django.utils import timezone
from .models import Participant,Vote, VoteInfo
from ipware.ip import get_ip
from django.db import IntegrityError
import datetime

def vote(request):
    start_time = datetime.datetime(2018, 11, 26, 0, 0, tzinfo=timezone.get_current_timezone())
    end_time = datetime.datetime(2018, 11, 30, 23, 59, 59, tzinfo=timezone.get_current_timezone())
    now = timezone.now()
    if request.POST:
        if start_time > now or now > end_time:
            error_msg = "投票尚未開始"
        else:
            ip = get_ip(request)
            if ip is not None:
                participant_id = request.POST['participant']
                participant = Participant.objects.get(id=participant_id)
                vote = Vote(participant=participant,ip=ip,date=datetime.date.today())
                try:
                    vote.save()
                except IntegrityError as e:
                    error_msg = "每人一天限投一票"
    participants = Participant.objects.all()
    return render(request,'vote.html',locals())
                
def index(request):
    vote_info = VoteInfo.objects.all()
    return render(request,'index.html',locals())
