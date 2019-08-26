from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json

class RoomConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'room_%s' % self.room_name
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
    
    # receivev data from the websocket
    def receive(self, text_data):
        data_json = json.loads(text_data)

        if 'ans' in data_json:
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'ans_message',
                    'player': data_json['player'],
                    'ans': data_json['ans']
                }
            )
        elif 'player' in data_json:
            player = data_json['player']
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'new_player',
                    'player': player
                }
            )

        elif 'delete_player' in data_json:
            delete_player = data_json['delete_player']
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'delete_player',
                    'delete_player': delete_player
                }
            )
        elif 'status' in data_json:
            status = data_json['status']
            if status == 'correct':
                guesser = data_json['guesser']
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'game_status',
                        'status': status,
                        'guesser': guesser,
                    }
                )
            elif status == 'pass':
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'game_status',
                        'status': status,
                    }
                )
            else:
                drawer = data_json['drawer']
                word = data_json['word']
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'game_status',
                        'status': status,
                        'drawer': drawer,
                        'word': word,
                    }
                )
        else:
        ## Send message to drawing group
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'drawing_stroke',
                    'x' : data_json['x'],
                    'y' : data_json['y'],
                    'draw_type': data_json['type']
                }
            )
    
    # add new player to the room
    def new_player(self, event):       
        data_json = event
        self.send(text_data=json.dumps({
            'player': data_json['player']
        }))

    # receive data from the drawing group
    def drawing_stroke(self, event):
        data_json = event
        self.send(text_data=json.dumps({
            'x' : data_json['x'],
            'y' : data_json['y'],
            'type': data_json['draw_type']
        }))

    def ans_message(self, event):
        answer = event['ans']
        player = event['player']
        # Send message to WebSocket (front end) --> js onmessage received
        self.send(text_data=json.dumps({
            'ans': answer,
            'player_id': player
        }))

    def delete_player(self, event):
        data_json = event
        self.send(text_data=json.dumps({
            'delete_player': data_json['delete_player']
        }))

    def game_status(self, event):
        data_json = event
        if data_json['status'] == 'correct':
            self.send(text_data=json.dumps({
                'status': data_json['status'],
                'guesser': data_json['guesser'],
            }))
        elif data_json['status'] == 'pass':
            self.send(text_data=json.dumps({
                'status': data_json['status'],
            }))
        else:
            self.send(text_data=json.dumps({
                'status': data_json['status'],
                'drawer': data_json['drawer'],
                'word': data_json['word']
            }))


class LobbyConsumer(WebsocketConsumer):
    def connect(self):
        self.lobby_group_name = "lobby"
        async_to_sync(self.channel_layer.group_add)(
            self.lobby_group_name,
            self.channel_name
        )
        self.accept()
        
    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.lobby_group_name,
            self.channel_name
        )
    def receive(self, text_data):
        data_json = json.loads(text_data)
        
        # user leave the room, decrease the number of players
        if 'leave_room' in data_json:
            room_name = data_json['leave_room']
            async_to_sync(self.channel_layer.group_send) (
                self.lobby_group_name,
                {
                    'type': 'leave_room',
                    'leave_room_name': room_name, 
                }
            )
        elif 'start_room' in data_json:
            room_name = data_json['start_room']
            async_to_sync(self.channel_layer.group_send) (
                self.lobby_group_name,
                {
                    'type': 'start_room',
                    'start_room': room_name, 
                }
            )
        elif 'curr_player_number' not in data_json:
            room_name = data_json['room_name']
            max_player_number = data_json['max_player_number']
            owner = data_json['owner']
            description = data_json['description']
            async_to_sync(self.channel_layer.group_send) (
                self.lobby_group_name, 
                {
                    'type': 'room_message',
                    'room_name': room_name,
                    'max_player_number': max_player_number,
                    'owner': owner,
                    'description': description,
                }

            )
        else:
            room_name = data_json['room_name']
            curr_player_number = data_json['curr_player_number']
            max_player_number = data_json['max_player_number']
            async_to_sync(self.channel_layer.group_send) (
                self.lobby_group_name, 
                {
                    'type': 'update_player_num',
                    'room_name': room_name,
                    'curr_player_number': curr_player_number,
                    'max_player_number': max_player_number
                }

            )

    def room_message(self, event):
        room_name = event['room_name']
        max_player_number = event['max_player_number']
        owner = event['owner']
        description = event['description']
        self.send(text_data=json.dumps({
            'room_name': room_name,
            'max_player_number': max_player_number,
            'owner': owner,
            'description': description,
        }))

    def update_player_num(self, event):
        room_name = event['room_name']
        curr_player_number = event['curr_player_number']
        max_player_number = event['max_player_number']
        self.send(text_data=json.dumps({
            'room_name': room_name,
            'curr_player_number': curr_player_number,
            'max_player_number': max_player_number
        }))
    
    def leave_room(self, event):
        room_name = event['leave_room_name']
        self.send(text_data=json.dumps({
            'leave_room_name': room_name,
        }))

    def start_room(self, event):
        room_name = event['start_room']
        self.send(text_data=json.dumps({
            'start_room': room_name,
        }))



