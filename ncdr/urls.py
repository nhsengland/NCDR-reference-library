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
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView

from .views import ColumnDetail, IndexView, TogglePreviewMode, api
from .views.data_element import DataElementDetail, DataElementList
from .views.database import DatabaseDetail, DatabaseList
from .views.forms import AddMany, Delete, Edit, FormRedirect, List
from .views.grouping import GroupingDetail, GroupingList
from .views.publishing import PublishAll, Unpublished
from .views.search import Search, SearchRedirect
from .views.table import TableAPI, TableDetail

urlpatterns = [
    path("", IndexView.as_view(), name="index_view"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("admin/", admin.site.urls),
    path("api/tables/<database_pk>", TableAPI.as_view()),
    path("api/", include(api.router.urls)),
    path("form/", FormRedirect.as_view(), name="redirect"),
    path("form/publish_all/", PublishAll.as_view(), name="publish_all"),
    path("form/<slug:model_name>/", never_cache(List.as_view()), name="edit_list"),
    path("form/<slug:model_name>/add/", AddMany.as_view(), name="add_many"),
    path("form/<slug:model_name>/edit/<int:pk>/", Edit.as_view(), name="edit"),
    path("form/<slug:model_name>/delete/<int:pk>/", Delete.as_view(), name="delete"),
    path(
        "form/<slug:model_name>/unpublished/",
        never_cache(Unpublished.as_view()),
        name="unpublished_list",
    ),
    path("about/", TemplateView.as_view(template_name="about.html"), name="about_page"),
    path("column/<int:pk>/", ColumnDetail.as_view(), name="column_detail"),
    path("database", DatabaseList.as_view(), name="database_list"),
    path("database/<str:db_name>/", DatabaseDetail.as_view(), name="database_detail"),
    path(
        "database/<str:db_name>/<int:pk>/", TableDetail.as_view(), name="table_detail"
    ),
    path("data_element/", DataElementList.as_view(), name="data_element_list"),
    path(
        "data_element/<slug:slug>/",
        DataElementDetail.as_view(),
        name="data_element_detail",
    ),
    path("grouping/", GroupingList.as_view(), name="grouping_redirect"),
    path("grouping/<slug:slug>/", GroupingDetail.as_view(), name="grouping_detail"),
    path("search/", SearchRedirect.as_view(), name="search_redirect"),
    path("search/<slug:model_name>/", Search.as_view(), name="search"),
    path(
        "toggle-preview-mode", TogglePreviewMode.as_view(), name="toggle-preview-mode"
    ),
    path("", include("metrics.urls")),
]


if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
