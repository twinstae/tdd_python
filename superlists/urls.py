from django.contrib import admin
from django.urls import path, include
from lists import views
from lists import urls as list_urls

urlpatterns = [
    path('', views.home_page, name='home'),
    path('lists/', include(list_urls)),
    path('admin/', admin.site.urls),
]
