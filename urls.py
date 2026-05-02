"""URL routes for the Github Details application."""
from django.urls import path

import views

urlpatterns = [
    path("", views.index, name="index"),
    path("org_members/<slug:org_name>", views.org_details, name="org_details"),
    path(
        "org_member/<slug:org_name>/<slug:user_name>",
        views.org_details,
        name="org_member_details",
    ),
    path("topic_username/<slug:user_name>", views.details, name="details"),
    path("topic_search", views.topic_search, name="topic_search"),
    path("username_search", views.username_search, name="username_search"),
    path("user_resume", views.user_resume, name="user_resume"),
]
