from django.conf.urls import include, url
from django.contrib import admin

from chat.views import http_view, login, logged_in, send_data_from_server, alarm

urlpatterns = [
    url(r'^ws/chat/', include('chat.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^ws/hello/$', http_view),
    url(r'^login/$', login),
    url(r'^logged-in/$', logged_in),
    url(r'^server-send/$', send_data_from_server),
    url(r'^alarm/$', alarm, name='alarm'),
]
