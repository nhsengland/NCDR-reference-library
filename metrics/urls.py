from django.urls import path
from django.views.generic.base import RedirectView

from .views import About, AtoZList, MetricDetail, Search, TopicDetail, TopicList

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="topics-list")),
    path("about/", About.as_view(), name="metrics-about"),
    path("a-z", AtoZList.as_view(), name="metrics-list"),
    path("topic", TopicList.as_view(), name="topics-list"),
    path("topic/<slug:slug>/", TopicDetail.as_view(), name="topics-detail"),
    path("search/", Search.as_view(), name="metrics-search"),
    path("<pk>/", MetricDetail.as_view(), name="metrics-detail"),
]
