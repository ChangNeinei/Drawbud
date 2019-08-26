"""webapps URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from drawbud.views import *

urlpatterns = [

    path('', lobby),
    path('lobby/', lobby, name='lobby'),
    path('login/', login_action, name='login'),
    path('logout/', logout_action, name='logout'),
    path('room/', room_action, name='room'),
    path('get_room/<str:room_name>', getroom_action, name='getroom'),
    path('register/', register_action, name='register'),
    path('tutorial/', tutorial, name='tutorial'),
    path('myprofile', myprofile_action, name='myprofile'),
    path('photo/<int:id>', getphoto_action, name='photo'),
    path('remove/<str:delete_user>', remove, name='remove'),
    path('leave_to_lobby/<str:delete_user>', leave_to_lobby, name='leave_to_lobby'),
    path('startroom/<str:room_name>', startRoom, name='startroom'),
    path('getvoc/<str:room_name>', getVoc, name='getvoc'),
    path('checkans/', checkAns, name='checkans'),
    path('uploadimage/', uploadImage, name='uploadimage'),
    path('drawing/<int:id>', getdrawing_action, name='drawing'),
]
