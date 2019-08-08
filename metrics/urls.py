from django.urls import path

from .views import About, Detail, List, Search

urlpatterns = [
    path("about/", About.as_view(), name="metrics-about"),
    path("", List.as_view(), name="metrics-list"),
    path("search/", Search.as_view(), name="metrics-search"),
    path("<pk>/", Detail.as_view(), name="metrics-detail"),
]
