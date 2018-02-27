from django.urls import path
from csv_schema import views

urlpatterns = [
    path(
        'form/preview_mode/<int:preview_mode>',
        views.PreviewModeSwitch.as_view(),
        name="preview_mode"
    ),
    path(
        'form/preview/unpublished',
        views.PreviewList.as_view(),
        name="preview_list"
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
        views.NCDREditListView.as_view(),
        name="edit_list"
    ),
    path('about', views.AboutView.as_view(), name="about_page"),
    path(
        'database/<str:db_name>/<str:table_name>',
        views.TableDetail.as_view(),
        name="table_detail"
    ),
    path(
        'database/<str:db_name>',
        views.DatabaseDetail.as_view(),
        name="database_detail"
    ),
    path('database', views.DatabaseList.as_view(), name="database_list"),

    path(
        'column/<slug:slug>',
        views.ColumnDetail.as_view(),
        name="column_detail"
    ),
    path('ncdr_references', views.NcdrReferenceRedirect.as_view(), name="ncdr_reference_redirect"),
    path('ncdr_references/<str:letter>', views.NcdrReferenceList.as_view(), name="ncdr_reference_list"),
    path('', views.IndexView.as_view(), name="index_view"),

    path('grouping', views.GroupingRedirect.as_view(), name="grouping_redirect"),
    path(
        'grouping/<slug:slug>',
        views.GroupingDetail.as_view(),
        name="grouping_detail"
    ),
]
