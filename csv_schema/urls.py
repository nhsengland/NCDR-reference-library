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
    url(r'table_admin/(?P<db_name>[0-9a-zA-Z_\-]+)/(?P<table_name>[0-9a-zA-Z_\-]+)$', views.AdminTablesVersionRedirect.as_view(), name="admin_redirect"),
    url(r'table_admin/(?P<db_name>[0-9a-zA-Z_\-]+)/(?P<table_name>[0-9a-zA-Z_\-]+)/(?P<version>\d+)$', views.AdminTablesVersions.as_view(), name="admin_versions"),
    url(r'table_admin/(?P<db_name>[0-9a-zA-Z_\-]+)/(?P<table_name>[0-9a-zA-Z_\-]+)/(?P<version>\d+)/edit$', views.AdminTablesEdit.as_view(), name="admin_tables_edit"),
    url(r'table_admin/(?P<db_name>[0-9a-zA-Z_\-]+)/(?P<table_name>[0-9a-zA-Z_\-]+)/(?P<version>\d+)/preview$', views.AdminTablesVersionPreview.as_view(), name="admin_tables_preview"),
    url(r'^$', views.IndexView.as_view(), name="index_view"),
]
