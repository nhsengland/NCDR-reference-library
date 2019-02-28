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
from django.views.generic import TemplateView

from .views import ColumnDetail, IndexView, Login
from .views.data_element import DataElementDetail, DataElementList
from .views.database import DatabaseDetail, DatabaseList
from .views.grouping import GroupingDetail, GroupingList
from .views.search import Search, SearchRedirect
from .views.table import TableDetail
from .views.version import (
    PublishVersion,
    SwitchToLatestVersion,
    SwitchToVersion,
    UnPublishVersion,
    VersionList,
)

urlpatterns = [
    path("", IndexView.as_view(), name="index_view"),
    path("accounts/login/", Login.as_view(), name="login"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("admin/", admin.site.urls),
    path("about/", TemplateView.as_view(template_name="about.html"), name="about_page"),
    path(
        "database/",
        include(
            [
                path("", DatabaseList.as_view(), name="database_list"),
                path(
                    "<str:db_name>/",
                    include(
                        [
                            path("", DatabaseDetail.as_view(), name="database_detail"),
                            path(
                                "table/<int:pk>/",
                                TableDetail.as_view(),
                                name="table_detail",
                            ),
                            path(
                                "column/<int:pk>/",
                                ColumnDetail.as_view(),
                                name="column_detail",
                            ),
                        ]
                    ),
                ),
            ]
        ),
    ),
    path("data_element/", DataElementList.as_view(), name="data_element_list"),
    path(
        "data_element/<slug:slug>/",
        DataElementDetail.as_view(),
        name="data_element_detail",
    ),
    path("grouping/", GroupingList.as_view(), name="grouping_redirect"),
    path("grouping/<slug:slug>/", GroupingDetail.as_view(), name="grouping_detail"),
    path("publish/<int:pk>/", PublishVersion.as_view(), name="publish_version"),
    path("search/", SearchRedirect.as_view(), name="search_redirect"),
    path("search/<slug:model_name>/", Search.as_view(), name="search"),
    path(
        "switch-to-latest-version",
        SwitchToLatestVersion.as_view(),
        name="switch-to-latest-version",
    ),
    path(
        "switch-to-version/<int:pk>/",
        SwitchToVersion.as_view(),
        name="switch-to-version",
    ),
    path("unpublish/<int:pk>/", UnPublishVersion.as_view(), name="unpublish_version"),
    path("versions/", VersionList.as_view(), name="version_list"),
    path("", include("metrics.urls")),
]


if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
