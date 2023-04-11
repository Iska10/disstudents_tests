from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render


# Create your views here.
def index(request): #HttpRequest
    return HttpResponse("Index page")


def categories(request, category_slug):
    return HttpResponse(f"category {category_slug}")


def page_not_found(request, exception):
    return HttpResponseNotFound("404 Not Found")

