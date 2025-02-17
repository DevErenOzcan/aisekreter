from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path(
        "meeting/",
        include(
            [
                path("start/", views.start_meeting, name="start_meeting"),
                path("start_segmentation/<int:id>/", views.start_segmentation, name="start_segmentation"),
                path("stop/<int:id>/", views.stop_meeting, name="stop_meeting"),
                path("results/<int:id>/", views.get_results, name="get_results"),
            ]
        ),
    ),
]
