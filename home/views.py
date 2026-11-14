from django.shortcuts import render
from .models import Link


def home(request):
    if request.method == "GET":
        links = Link.objects.all().order_by('order')

        return render(request, "home.html", {"links": links})