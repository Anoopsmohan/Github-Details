"""
    urls

    Handles urls of github application
"""
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$','views.index'),
    (r'^org_members/(?P<org_name>[\w-]+)$', 'views.org_details'),
    (
        r'^org_member/(?P<org_name>[\w-]+)/(?P<user_name>[\w-]+)$',\
            'views.org_details'
    ),
    (r'^topic_username/(?P<user_name>[\w-]+)$', 'views.details'),
    (r'^topic_search$', 'views.topic_search'),
    (r'^username_search$', 'views.username_search'),
    (r'^contact$', 'views.contact'),
    (r'^email_send', 'views.email_send'),
    (r'^user_resume', 'views.user_resume'),
)
