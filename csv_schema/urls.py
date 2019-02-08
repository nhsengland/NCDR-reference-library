from django.urls import include, path
from django.views.generic import TemplateView

from . import api
from .views import ColumnDetail, FormRedirect, IndexView, PreviewModeSwitch, PublishAll
from .views.data_element import DataElementDetail, DataElementList
from .views.database import DatabaseDetail, DatabaseList
from .views.grouping import GroupingDetail, GroupingList
from .views.table import TableDetail

urlpatterns = [

    # form urls
    path('form/', FormRedirect.as_view(), name="redirect"),
    path('form/preview_mode/<int:preview_mode>', PreviewModeSwitch.as_view(), name="preview_mode"),
    path('form/publish_all/', PublishAll.as_view(), name="publish_all"),

    path('about/', TemplateView.as_view(template_name="about.html"), name="about_page"),

    path('database', DatabaseList.as_view(), name="database_list"),
    path('database/<str:db_name>/', DatabaseDetail.as_view(), name="database_detail"),
    path('database/<str:db_name>/<str:table_name>/', TableDetail.as_view(), name="table_detail"),

    path('column/<slug:slug>/', ColumnDetail.as_view(), name="column_detail"),

    path('data_element/', DataElementList.as_view(), name="data_element_list"),
    path('data_element/<slug:slug>/', DataElementDetail.as_view(), name="data_element_detail"),

    path('', IndexView.as_view(), name="index_view"),

    path('grouping/', GroupingList.as_view(), name="grouping_redirect"),
    path('grouping/<slug:slug>/', GroupingDetail.as_view(), name="grouping_detail"),
    path(r'api/', include(api.router.urls)),
]
