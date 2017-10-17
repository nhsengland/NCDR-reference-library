from django.conf.urls import url
from csv_schema import views

urlpatterns = [
    url(r'^', views.RowView.as_view(), name="csv_view"),
    url(r'about/', views.AboutView.as_view(), name="about_view"),
]
