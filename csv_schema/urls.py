from django.urls import include, path
from django.views.generic import TemplateView

from . import api
from .views import ColumnDetail, FormRedirect, IndexView, PublishAll, TogglePreviewMode
from .views.data_element import DataElementDetail, DataElementList
from .views.database import DatabaseDetail, DatabaseList
from .views.grouping import GroupingDetail, GroupingList
from .views.table import TableAPI, TableDetail

urlpatterns = [
    path(
        "toggle-preview-mode", TogglePreviewMode.as_view(), name="toggle-preview-mode"
    ),
    # form urls
    path("form/", FormRedirect.as_view(), name="redirect"),
    path("form/publish_all/", PublishAll.as_view(), name="publish_all"),
    path("about/", TemplateView.as_view(template_name="about.html"), name="about_page"),
    path("database", DatabaseList.as_view(), name="database_list"),
    path("database/<str:db_name>/", DatabaseDetail.as_view(), name="database_detail"),
    path("database/<str:db_name>/<pk>/", TableDetail.as_view(), name="table_detail"),
    path("column/<int:pk>/", ColumnDetail.as_view(), name="column_detail"),
    path("data_element/", DataElementList.as_view(), name="data_element_list"),
    path(
        "data_element/<slug:slug>/",
        DataElementDetail.as_view(),
        name="data_element_detail",
    ),
    path("", IndexView.as_view(), name="index_view"),
    path("grouping/", GroupingList.as_view(), name="grouping_redirect"),
    path("grouping/<slug:slug>/", GroupingDetail.as_view(), name="grouping_detail"),
    path("api/tables/<database_pk>", TableAPI.as_view()),
    path("api/", include(api.router.urls)),
]
