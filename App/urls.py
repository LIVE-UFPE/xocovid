from django.urls import path
from django.conf.urls import url
from . import views

# SET THE NAMESPACE!
app_name = 'App'

urlpatterns = [
    path('register/',views.register,name='register'),
    path('user_login/',views.user_login,name='user_login'),
    path('tela_exemplo/<int:id>', views.tela_exemplo, name='tela_exemplo'),
    path('index', views.index, name="index"),
    path('home', views.home, name="home"),
    path('graphs/', views.graphs, name="graphs"),
    path('get/ajax/pins',views.get_pins, name="get_pins"),
    path('graphs/get_data',views.get_data, name="get_data"),
    path('send_email',views.send_email, name="send_email"),
]