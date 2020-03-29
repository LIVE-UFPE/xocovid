from django.contrib import admin
from django.urls import include, path
from django.conf.urls import url,include
from App import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.index,name='index'),
    path('App/',include('App.urls')),
    path('logout/', views.user_logout, name='logout'),
]
