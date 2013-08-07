from django.conf.urls import patterns, include, url
from guides.views import EditPerson, DeletePerson, AddBannedPerson, UnbanPerson
from django.contrib import admin
import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'guides.views.home'), # home
    url(r'^add/', 'guides.views.add_person'), # add a person
    url(r'^gitshell/', 'guides.views.gitshell'), # pull git, restart apache
    url(r'^view/(?P<no>\d+)/$', 'guides.views.view_person', name='view_person'), # view a person
    url(r'^list/log/$', 'guides.views.list_log'), # view log
    url(r'^list/$', 'guides.views.list_person'), # list people
    url(r'^export/$', 'guides.views.export_person'), # export people
    url(r'^log/$', 'guides.views.import_log'), # import log
    url(r'^blacklist/$', 'guides.views.list_banned'), # list banned people
    url(r'^blacklist/export/$', 'guides.views.export_banned'), # list people
    url(r'^blacklist/add/$', AddBannedPerson.as_view(), name='add_banned_person'), # add a person
    url(r'^edit/(?P<pk>\d+)/$', EditPerson.as_view(), name='edit_person'),
    #url(r'^view/(?P<pk>\d+)/$', ViewPerson.as_view(), name='view_person'),
    url(r'^delete/(?P<pk>\d+)/$', DeletePerson.as_view(), name='delete_person'),
    url(r'^blacklist/remove/(?P<slug>\d+)/$', UnbanPerson.as_view(), name='unban_person'),
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^uploads/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True }),
                       
#     url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
#         {'document_root': settings.STATIC_ROOT, }),
)

# urlpatterns += staticfiles_urlpatterns()
