from django.conf.urls import patterns, include, url
from django.views.static import * 
from django.conf import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^rateMyFriends/', include('rater.urls')),
	#url(r'^admin/', include(admin.site.urls)),
	url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),)
