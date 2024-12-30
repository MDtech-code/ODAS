from channels.generic.websocket import AsyncWebsocketConsumer
import json

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_group_name = self.scope['url_route']['kwargs']['room_name']
        print(f"Connecting to room: {self.room_group_name}")
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print('Disconnected')

    async def receive(self, text_data):
        receive_dict = json.loads(text_data)
        action = receive_dict['action']

        if action == 'user-joined':  # New action for user join
            username = receive_dict['message']['username']
            # Broadcast the "user-joined" message to other participants
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'notify_user_joined',
                    'message': f'{username} has joined the call!'
                }
            )
            return
        
        if action == 'new-offer' or action == 'new-answer':
            receiver_channel_name = receive_dict['message']['receiver_channel_name']
            receive_dict['message']['receiver_channel_name'] = self.channel_name

            await self.channel_layer.send(
                receiver_channel_name,
                {
                    'type': 'send_sdp',
                    'receive_dict': receive_dict,
                }
            )
            return

        receive_dict['message']['receiver_channel_name'] = self.channel_name
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'send_sdp',
                'receive_dict': receive_dict,
            }
        )

    async def send_sdp(self, event):
        receive_dict = event['receive_dict']
        await self.send(text_data=json.dumps(receive_dict))

    async def notify_user_joined(self, event):
        # Notify the users that a new participant has joined
        message = event['message']
        await self.send(text_data=json.dumps({
            'action': 'user-joined-notification',
            'message': message
        }))
