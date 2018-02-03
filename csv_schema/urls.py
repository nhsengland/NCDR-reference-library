from django.urls import path, include
from csv_schema import views, api

urlpatterns = [
    path(
        'form/<slug:model_name>/edit', views.EditView.as_view(), name="edit"
    ),
    path('form/<slug:model_name>/add', views.AddView.as_view(), name="add"),
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
    path('api/', include(api.router.urls)),
]
