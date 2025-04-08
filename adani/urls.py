"""
URL configuration for adani project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.http import HttpResponse
from django.conf.urls import handler404
from django.shortcuts import render

from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from myapp.views import employee_page

import os

BASE_DIR = settings.BASE_DIR

def robots_txt(request):
    content = "User-agent: *\nAllow: /\nSitemap: https://eligo.space/sitemap.xml"
    return HttpResponse(content, content_type="text/plain")


# Custom 404 view
def custom_404_view(request, exception):
    return render(request, "404.html", status=404)

# URL patterns
urlpatterns = [
    path("admin/", admin.site.urls),
    path('', include('myapp.urls')),
    path('member/', employee_page, name='employee_page'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Assign custom 404 handler
handler404 = custom_404_view

