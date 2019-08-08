from django.urls import path
from . import views

urlpatterns = [
	path('', views.index, name='index'),
        path('view/', views.handle_view_file, name='view'),
        path('upload/', views.handle_file_upload, name='upload'),
]
