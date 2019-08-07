from django.urls import path

from .views import About, Detail, Home, List, Search

urlpatterns = [
    path("", Home.as_view(), name="metrics-home"),
    path("about/", About.as_view(), name="metrics-about"),
    path("list/", List.as_view(), name="metrics-list"),
    path("search/", Search.as_view(), name="metrics-search"),
    path("<pk>/", Detail.as_view(), name="metrics-detail"),
]
