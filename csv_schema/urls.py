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
    url(
        r'^column/(?P<slug>[0-9a-zA-Z_\-]+)',
        views.ColumnDetail.as_view(),
        name="column_detail"
    ),
    url(r'^ncdr_references$', views.NcdrReferenceRedirect.as_view(), name="ncdr_reference_redirect"),
    url(r'^ncdr_references/(?P<letter>[0-9A-Z_\-]+)$', views.NcdrReferenceList.as_view(), name="ncdr_reference_list"),
    url(r'^$', views.IndexView.as_view(), name="index_view"),
]
