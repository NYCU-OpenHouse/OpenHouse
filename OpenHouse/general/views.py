from django.shortcuts import render, redirect
from django.http import  HttpResponseRedirect, JsonResponse,Http404, HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import datetime, json
from . import models

def Index(request):
    general_news_list = models.News.objects.filter(
        category="最新消息"
    ).exclude(
        perm="company_only"
    ).exclude(
        expiration_time__lt=datetime.datetime.now().date()
    ).order_by("-pinned", "-updated_time")[:5]

    recruit_news_list = models.News.objects.filter(
        category="徵才專區"
    ).exclude(
        perm="company_only"
    ).exclude(
        expiration_time__lt=datetime.datetime.now().date()
    ).order_by("-pinned", "-updated_time")[:5]


    photo_slide_list = models.PhotoSlide.objects.all().order_by('order')

    return render(request,'general/index.html',locals())


#TODO permission
def ReadNews(request,news_id):
    if not news_id.isnumeric():
        raise Http404("Not found")
    news = models.News.objects.filter(id = news_id).first()
    if not news:
        raise Http404("Not found")
    files = models.NewsFile.objects.filter(news_id=news_id)
    return render(request,'general/read_news.html',locals())

def GeneralNewsListing(request):
    general_news_list = models.News.objects.filter(
        category="最新消息"
    ).exclude(
        perm="company_only"
    ).exclude(
        expiration_time__lt=datetime.datetime.now().date()
    ).order_by(
        "-pinned", "-updated_time"
    )
    paginator = Paginator(general_news_list, 10) # Show 10 news per page

    page = request.GET.get('page')
    try:
        general_news_page = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        general_news_page = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        general_news_page = paginator.page(paginator.num_pages)

    return render(request, 'general/general_news_list.html', locals())

def RecruitNewsListing(request):
    recruit_news_list = models.News.objects.filter(
        category="徵才專區"
    ).exclude(
        perm="company_only"
    ).exclude(
        expiration_time__lt=datetime.datetime.now().date()
    ).order_by(
        "-pinned", "-updated_time"
    )
    paginator = Paginator(recruit_news_list, 10) # Show 10 news per page

    page = request.GET.get('page')
    try:
        recruit_news_page = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        recruit_news_page = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        recruit_news_page = paginator.page(paginator.num_pages)

    return render(request, 'general/recruit_news_list.html', locals())

#temporary deprecated
@login_required
def GetCompanyNewsList(request):
    news_list = models.News.objects.filter(Q(perm="both") | Q(perm="company_only"))

    ret_news_list = []
    for news in news_list:
        news_dict = {"title":news.title,"updated_time":news.updated_time,"url":"/news/"+news.id}
        ret_news_list.append(news_dict)

    return JsonResponse({'success':True,'data':ret_news_list})

def FAQ(request):
    try:
        FAQ = models.FAQ_new.objects.order_by('id').first()
    except models.FAQ_new.DoesNotExist:
        error_msg = '常見問題尚未建立，敬請等待!'
        return render(request, 'general/error.html', locals())
    return render(request, 'general/FAQ.html', locals())

def History(request):
    try:
        history_imgs = models.HistoryImg.objects.order_by('order')
        if not history_imgs:
            error_msg = '歷史沿革尚未建立，敬請等待!'
            return render(request, 'general/error.html', locals())
    except models.HistoryImg.DoesNotExist:
        error_msg = '歷史沿革尚未建立，敬請等待!'
        return render(request, 'general/error.html', locals())
    return render(request, 'general/history.html', locals())

def Member(request):
    try:
        members = models.Member.objects.order_by('start_term')
        if not members:
            error_msg = '各屆幹部尚未建立，敬請等待!'
            return render(request, 'general/error.html', locals())
    except models.Member.DoesNotExist:
        error_msg = '各屆幹部尚未建立，敬請等待!'
        return render(request, 'general/error.html', locals())

    # Group members by term
    members_by_term = {}
    for member in members:
        terms = member.get_all_terms()
        for term in terms:
            if term not in members_by_term:
                members_by_term[term] = []
            members_by_term[term].append(member)
    # Sort members in each term by title and name
    for term, members in members_by_term.items():
        members_by_term[term] = sorted(members, key=lambda x: (x.title, x.name))
    return render(request, 'general/member.html', locals())
