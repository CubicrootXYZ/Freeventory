from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, permission_required
from django.http import Http404


def error404(request, exception):
    context = {
        'exception': str(exception),
        'site_title': "404"
    }
    return render(request, '404.html', context, status=404)


