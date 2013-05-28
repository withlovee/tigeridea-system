from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'system.views.home', name='home'),
    # url(r'^system/', include('system.foo.urls')),
    #url(r'^admin/', include('smuggler.urls')),
    #url(r'^$', 'guides.views.index'), # root
    url(r'^add/', 'guides.views.add_person'), # add a person
    url(r'^view/', 'guides.views.view_person'), # view a person
    url(r'^list/', 'guides.views.list_person'), # list people
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
