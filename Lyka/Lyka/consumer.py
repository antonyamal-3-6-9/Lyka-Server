import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

class NotificationPrivateConsumer(AsyncWebsocketConsumer):

    connected_users = {} 

    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']

        self.user_channel_name = f'user_{self.user_id}'

        await self.channel_layer.group_add(
            self.user_channel_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(
            self.user_channel_name,
            self.channel_name
        )

    async def send_order_update(self, event):
        message = event['message']
        time = event["time"]
        print("Consumers")
        await self.send(text_data=json.dumps({'message': message , 'time' : time}))

    async def send_greetings(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({"message" : message, "time" : "12 PM"}))

