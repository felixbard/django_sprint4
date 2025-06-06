# pages/views.py
from django.shortcuts import render
from django.views.generic import TemplateView


def about(request):
    template = 'pages/about.html'
    return render(request, template)


def rules(request):
    template = 'pages/rules.html'
    return render(request, template)


def page_not_found(request, exception):
    return render(request, 'pages/404.html', status=404)


def csrf_failure(request, reason=''):
    return render(request, 'pages/403csrf.html', status=403)


def server_error(request):
    return render(request, 'pages/500.html', status=500)


class AboutDetailView(TemplateView):
    template_name = 'pages/about.html'


class RulesDetailView(TemplateView):
    template_name = 'pages/rules.html'
