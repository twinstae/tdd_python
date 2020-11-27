from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from lists import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_page, name='home'),
    path('lists/the-only-list-in-the-world', views.view_list, name='view_list'),
]
