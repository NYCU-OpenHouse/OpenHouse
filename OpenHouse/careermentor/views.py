from django.shortcuts import render, redirect
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import datetime
from . import forms
from . import models


def get_event_status(events):
    for event in events:
        event.full = False
        if event.signup_deadline < timezone.now().date():
            event.status = "報名時間截止 (Times Up)"
            event.full = True
        elif event.limit == 0:
            event.status = "Available"
        elif event.signup_num < event.limit:
            event.status = "Available：{}人".format(event.limit - event.signup_num)
        elif event.signup_num >= 2 * event.limit:
            event.status = "已額滿(Full)"
            event.full = True
        elif event.signup_num >= event.limit:
            event.status = "尚可候補：{}人".format(event.limit * 2 - event.signup_num)


# Create your views here.
def CareerMentorIndex(request):
    mentor_events = models.Mentor.objects.filter(category="職場導師") \
        .exclude(date__lt=datetime.now()).order_by('-date') \
        .annotate(signup_num=Count('signup'))
    career_events = models.Mentor.objects.filter(category="職涯教練").order_by('-date') \
        .exclude(date__lt=datetime.now()).order_by('-date') \
        .annotate(signup_num=Count('signup'))
    career_seminar = models.Mentor.objects.filter(category="職涯講座").order_by('-date') \
        .exclude(date__lt=datetime.now()).order_by('-date') \
        .annotate(signup_num=Count('signup'))

    get_event_status(mentor_events)
    get_event_status(career_events)
    get_event_status(career_seminar)

    return render(request, 'mentor/mentor_index.html', locals())


def CareerMentorSignup(request, event_id):
    try:
        event = models.Mentor.objects.filter(id=event_id).annotate(signup_num=Count('signup')).first()
        # redirect page if category doesn't match
        if event.category == '職涯講座':
            return redirect('/mentor/career_seminar_signup/' + str(event_id))
        # reach limit
        if event.limit != 0 and event.signup_num >= 2 * event.limit:
            return render(request, 'mentor/error.html')
        # time reach deadline
        if event.signup_deadline < timezone.now().date():
            return render(request, 'mentor/error.html')
    except:
        return render(request, 'mentor/error.html')

    init_data = {'mentor': event_id}
    form = forms.SignupForm(initial=init_data)
    if request.method == "POST":
        data = request.POST.copy()
        form = forms.SignupForm(data, request.FILES)
        if form.is_valid():
            form.save()
            return render(request, 'mentor/mentor_signup_success.html', locals())

        else:
            print(form.errors)

    return render(request, 'mentor/mentor_signup.html', locals())

# Customize form for Career Seminar
def CareerSeminarSignup(request, event_id):
    try:
        event = models.Mentor.objects.filter(id=event_id).annotate(signup_num=Count('signup')).first()
        # redirect page if category doesn't match
        if event.category != '職涯講座':
            return redirect('/mentor/signup/' + str(event_id))
        # reach limit
        if event.limit != 0 and event.signup_num >= 2 * event.limit:
            return render(request, 'mentor/error.html')
        # time reach deadline
        if event.signup_deadline < timezone.now().date():
            return render(request, 'mentor/error.html')
    except:
        return render(request, 'mentor/error.html')

    init_data = {'mentor': event_id}
    form = forms.CareerSeminarSignupForm(initial=init_data)
    if request.method == "POST":
        data = request.POST.copy()
        form = forms.CareerSeminarSignupForm(data)
        if form.is_valid():
            form.save()
            return render(request, 'mentor/mentor_signup_success.html', locals())

        else:
            print(form.errors)

    return render(request, 'mentor/mentor_signup.html', locals())

def event_info(request, event_id):
    try:
        event = models.Mentor.objects.get(id=event_id)
        if event.date < timezone.now().date():
            return render(request, 'mentor/error.html')
    except:
        return render(request, 'mentor/error.html')

    return render(request, 'mentor/mentor_info.html', locals())


def ListCareerMentor(request):

    mentor_events = models.Mentor.objects.all() \
        .order_by('-date') \
        .annotate(signup_num=Count('signup'))

    return render(request, 'admin/mentor_list.html', locals())

