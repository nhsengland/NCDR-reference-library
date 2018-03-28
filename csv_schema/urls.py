from django.urls import path, include
from csv_schema import views
from csv_schema import api
from django.views.decorators.cache import never_cache

urlpatterns = [

    # form urls
    path(
        'form/preview_mode/<int:preview_mode>',
        views.PreviewModeSwitch.as_view(),
        name="preview_mode"
    ),
    path(
        'form/publish_all/',
        views.PublishAll.as_view(),
        name="publish_all"
    ),
    path(
        'form/<slug:model_name>/unpublished/',
        never_cache(views.UnPublishedList.as_view()),
        name="unpublished_list"
    ),
    path(
        'form/',
        views.NCDRFormRedirect.as_view(),
        name="redirect"
    ),
    path(
        'form/<slug:model_name>/add/',
        views.NCDRAddManyView.as_view(),
        name="add_many"
    ),
    path(
        'form/<slug:model_name>/edit/<int:pk>/',
        views.NCDREditView.as_view(),
        name="edit"
    ),

    path(
        'form/<slug:model_name>/delete/<int:pk>/',
        views.NCDRDeleteView.as_view(),
        name="delete"
    ),
    path(
        'form/<slug:model_name>/',
        never_cache(views.NCDREditListView.as_view()),
        name="edit_list"
    ),

    # search urls
    path(
        'search/',
        views.NCDRSearchRedirect.as_view(),
        name="search_redirect"
    ),
    path(
        'search/<slug:model_name>/',
        views.NCDRSearch.as_view(),
        name="search"
    ),


    path('about/', views.AboutView.as_view(), name="about_page"),
    path(
        'database/<str:db_name>/<str:table_name>/',
        views.TableDetail.as_view(),
        name="table_detail"
    ),
    path(
        'database/<str:db_name>/',
        views.DatabaseDetail.as_view(),
        name="database_detail"
    ),
    path(
        'data_element/<slug:slug>/',
        views.DataElementDetail.as_view(),
        name="data_element_detail"
    ),
    path('database', views.DatabaseList.as_view(), name="database_list"),

    path(
        'column/<slug:slug>/',
        views.ColumnDetail.as_view(),
        name="column_detail"
    ),
    path(
        'data_element/',
        views.DataElementList.as_view(),
        name="data_element_list"
    ),
    path('', views.IndexView.as_view(), name="index_view"),

    path('grouping/', views.GroupingList.as_view(), name="grouping_redirect"),
    path(
        'grouping/<slug:slug>/',
        views.GroupingDetail.as_view(),
        name="grouping_detail"
    ),
    path(r'api/', include(api.router.urls)),
]
