from django.conf.urls import url

from . import consumers

websocket_urlpatterns = [

    url('ws/room/(?P<room_name>[^/]+)', consumers.RoomConsumer),
    url('ws/lobby/', consumers.LobbyConsumer),
]
