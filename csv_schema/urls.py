from django.conf.urls import url
from csv_schema import views

urlpatterns = [
    url(r'^about$', views.AboutView.as_view(), name="about_page"),
    url(
        r'^database/(?P<pk>\d+)$',
        views.DatabaseDetail.as_view(),
        name="database_detail"
    ),
    url(r'^database$', views.DatabaseList.as_view(), name="database_list"),
    url(
        r'^table/(?P<pk>\d+)$',
        views.TableDetail.as_view(),
        name="table_detail"
    ),
    url(r'^', views.RowView.as_view(), name="csv_page"),
]
