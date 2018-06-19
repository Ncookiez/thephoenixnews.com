import datetime

from django.conf import settings
from django.shortcuts import render, redirect
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from dispatch.models import Article, Page, Section, Topic, Issue

def homepage(request):
    news =  Article.objects.filter(section__slug='news', is_published=True).order_by('-published_at')
    lifestyle = Article.objects.filter(section__slug='life', is_published=True).order_by('-published_at')
    features = Article.objects.filter(section__slug='features', is_published=True).order_by('-published_at')
    arts = Article.objects.filter(section__slug='arts', is_published=True).order_by('-published_at')
    sports = Article.objects.filter(section__slug='sports', is_published=True).order_by('-published_at')
    opinions = Article.objects.filter(section__slug='opinions', is_published=True).order_by('-published_at')

    context = {
        'title': 'The Phoenix - UBCO\'s student newspaper',
        'news': news,
        'lifestyle': lifestyle,
        'features': features,
        'arts': arts,
        'sports': sports,
        'opinions': opinions,
        'issue': Issue.objects.order_by('-date').first(),
        'footer': get_footer_context()
    }

    print context['lifestyle']

    return render(request, 'homepage.html', context)

def section_home(request, slug=None):
    return section(request, slug, None)

def section_topic(request, slug=None, topic=None):
    return section(request, slug, topic)

def section(request, section_slug=None, topic_slug=None):
    try:
        section = Section.objects.get(slug=section_slug)
    except Section.DoesNotExist:
        raise Http404("Section does not exist")

    articles = Article.objects.filter(is_published=True, section=section)

    topic = None

    if topic_slug:
        topic = Topic.objects.get(slug=topic_slug)
        articles = articles.filter(topic=topic)

    articles = articles.order_by('-published_at')

    paginator = Paginator(articles[4:], 12)
    page = request.GET.get('page')

    try:
        archive = paginator.page(page)
    except PageNotAnInteger:
        archive = paginator.page(1)
    except EmptyPage:
        archive = paginator.page(paginator.num_pages)

    context = {
        'title': '%s - The Phoenix' % section.name,
        'section': section,
        'topic': topic,
        'articles': {
            'primary': articles[0],
            'secondary': articles[1:4],
            'archive': archive
        }
    }

    return render(request, 'section.html', context)

def article(request, year=0, month=0, slug=None):
    year, month = int(year), int(month)

    try:
        article = Article.objects.get(slug=slug, is_published=True)
    except Article.DoesNotExist:
        raise Http404("Article does not exist")

    if article.published_at.year != year or article.published_at.month != month:
        raise Http404("Article does not exist")

    related = Article.objects \
        .filter(section=article.section, is_published=True) \
        .order_by('-published_at') \
        .exclude(id__in=[article.id])[:3]

    context = {
        'title': '%s - The Phoenix' % article.headline,
        'article': article,
        'related': related
    }

    return render(request, 'article.html', context)

def page(request, slug=None):
    try:
        page = Page.objects.get(slug=slug, is_published=True)
    except Page.DoesNotExist:
        raise Http404("Page does not exist")

    context = {
        'title': '%s - The Phoenix' % page.title,
        'page': page,
    }

    return render(request, 'page.html', context)

def issues(request):

    issues_qs = Issue.objects.order_by('-date')

    paginator = Paginator(issues_qs, 12)
    page = request.GET.get('page')

    try:
        issues = paginator.page(page)
    except PageNotAnInteger:
        issues = paginator.page(1)
    except EmptyPage:
        issues = paginator.page(paginator.num_pages)

    context = {
        'title': 'Issues - The Phoenix',
        'issues': issues
    }

    return render(request, 'issues.html', context)

def issue(request, year=None, month=None, day=None):
    # TODO: validate year/month/day
    year, month, day = int(year), int(month), int(day)

    date = datetime.date(year, month, day)

    try:
        issue = Issue.objects.get(
            date__year=date.year,
            date__month=date.month,
            date__day=date.day)
    except Issue.DoesNotExist:
        raise Http404("Issue does not exist")

    if not request.user_agent.is_pc:
        return redirect(issue.file.url)

    context = {
        'title': '%s - The Phoenix' % issue.title,
        'issue': issue
    }

    return render(request, 'issue.html', context)


def get_footer_context():
    sections = ['news', 'life', 'features', 'arts', 'sports', 'opinions']
    section_topics = {}

    for section in sections:
        topic_ids = Article.objects \
                        .filter(is_published=True, section__slug=section) \
                        .values('topic') \
                        .distinct()
        topic_ids = map(lambda t: t['topic'], topic_ids)
        topic_ids = filter(lambda t: t is not None, topic_ids)

        topics = Topic.objects.filter(id__in=topic_ids)

        section_topics[section] = topics
