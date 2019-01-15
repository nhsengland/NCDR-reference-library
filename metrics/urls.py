from django.urls import path

from .views import MetricDetail, MetricsList

urlpatterns = [
    path("metrics/", MetricsList.as_view(), name="metrics-list"),
    path("metrics/<pk>/", MetricDetail.as_view(), name="metrics-detail"),
]
