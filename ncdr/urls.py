"""ncdr URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.views.decorators.cache import never_cache

from .views import AddMany, Delete, Edit, List, Search, SearchRedirect, Unpublished

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include("csv_schema.urls")),

    path('form/<slug:model_name>/unpublished/', never_cache(Unpublished.as_view()), name="unpublished_list"),
    path('form/<slug:model_name>/add/', AddMany.as_view(), name="add_many"),
    path('form/<slug:model_name>/edit/<int:pk>/', Edit.as_view(), name="edit"),
    path('form/<slug:model_name>/delete/<int:pk>/', Delete.as_view(), name="delete"),
    path('form/<slug:model_name>/', never_cache(List.as_view()), name="edit_list"),

    path('search/', SearchRedirect.as_view(), name="search_redirect"),
    path('search/<slug:model_name>/', Search.as_view(), name="search"),

    path('', include('metrics.urls')),

    path('accounts/', include('django.contrib.auth.urls')),
]
