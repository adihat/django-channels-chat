import datetime
import json

from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer, JsonWebsocketConsumer

from mysite.settings import MONGO_CLIENT


@database_sync_to_async
def save_to_database(db, collection, chat_message):
    print('inside save_to_database====>', db, collection, chat_message)
    r = MONGO_CLIENT[db][collection].insert_one(chat_message)
    return True, r.inserted_id


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print('inside ChatConsumer connect()')
        print('scope =======>', self.scope)
        print('channel_layer ======>', self.channel_layer)
        print('channel_name ======>', self.channel_name)
        self.username = self.scope['session'].get('username', 'server')
        print('username =====>', self.username)
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        print('inside ChatConsumer disconnect()')
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        print('inside ChatConsumer receive()')
        if not self.username == 'server':
            username = self.scope['session']['username']
        else:
            username = 'server'
        text_data_json = json.loads(text_data)
        typing = text_data_json.get('typing') or False
        out_of_focus = text_data_json.get('outoffocus') or False
        timestamp = text_data_json.get('timestamp') or ''
        chat_data = {'type': 'chat_message', 'username': username, 'outoffocus': out_of_focus, 'typing': typing,
                     'timestamp': timestamp}
        message = text_data_json.get('message', '')
        if message:
            chat_data.update({'message': message})
        await self.channel_layer.group_send(self.room_group_name, chat_data)

    async def chat_message(self, event):
        print('inside ChatConsumer chat_message()', event)
        await self.send(text_data=json.dumps(event))

        # TODO link with celery later
        # save to database
        message = event.get('message') or ''
        if message:
            user_name = event['username']
            room_name = self.scope['url_route']['kwargs']['room_name']
            timestamp = datetime.datetime.utcnow()
            chat_data = {'user': user_name, 'chat_room': room_name, 'message': {'text': message},
                         'timestamp': timestamp}
            status, inserted_id = await save_to_database('chat_message', 'account_1', chat_data)
            if status:
                print('chat saved to db successfully ====>', inserted_id)
            else:
                print('saving to db failed')


class EventConsumer(JsonWebsocketConsumer):
    def connect(self):
        print('inside EventConsumer connect()')
        async_to_sync(self.channel_layer.group_add)(
            'events',
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        print('inside EventConsumer disconnect()')
        print("Closed websocket with code: ", close_code)
        async_to_sync(self.channel_layer.group_discard)(
            'events',
            self.channel_name
        )
        self.close()

    def receive_json(self, content, **kwargs):
        print('inside EventConsumer receive_json()')
        print("Received event: {}".format(content))
        self.send_json(content)

    def events_alarm(self, event):
        print('inside EventConsumer events_alarm()')
        self.send_json(
            {
                'type': 'events.alarm',
                'content': event['content']
            }
        )
