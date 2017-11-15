from django.conf.urls import url
from csv_schema import views

urlpatterns = [
    url(r'^about$', views.AboutView.as_view(), name="about_page"),
    url(
        r'^database/(?P<db_name>[0-9a-zA-Z_\-]+)/(?P<table_name>[0-9a-zA-Z_\-]+)',
        views.TableDetail.as_view(),
        name="table_detail"
    ),
    url(
        r'^database/(?P<db_name>[0-9a-zA-Z_\-]+)',
        views.DatabaseDetail.as_view(),
        name="database_detail"
    ),
    url(r'^database$', views.DatabaseList.as_view(), name="database_list"),
    url(r'^$', views.IndexView.as_view(), name="index_view"),
]
