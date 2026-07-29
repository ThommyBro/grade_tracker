from django.shortcuts import render

# Create your views here.
# Here starts my stuff

from django.http import HttpResponse


def home(request):
    return HttpResponse("Hello Grade Tracker!")