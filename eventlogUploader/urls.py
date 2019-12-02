from django.urls import path
from django.conf.urls import include, url
from . import views

urlpatterns = [
	path('', views.index, name='index'),
        path('view/', views.handle_view_file, name='view'),
        path('upload/', views.handle_file_upload, name='upload'),
        url(r'^delete/(?P<token>\w+)/$', views.delete_file, name='delete_file'),
]
