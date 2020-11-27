from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from lists import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_page, name='home'),
    path('lists/new', views.new_list, name='new_list'),
    path('lists/<int:list_id>', views.view_list, name='view_list'),
    path('lists/<int:list_id>/add_item', views.add_item, name='add_item'),
]
