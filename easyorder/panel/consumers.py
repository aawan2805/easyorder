import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from panel.models import Brand, Order

class OrderConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.brand_uuid = None
        self.room_group_name = None
        self.brand = None

    def connect(self):
        self.brand_uuid = self.scope['url_route']['kwargs']['brand_uuid']
        self.room_group_name = f'orders_{self.brand_uuid}'
        self.brand = Brand.objects.filter(uuid=self.brand_uuid)

        if self.brand:
            # connection has to be accepted
            self.accept()

            # join the room group
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name,
                self.channel_name,
            )

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name,
        )

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message', None)
        if message is not None:
            # Do stuff.
            pass

    def chat_message(self, event):
        self.send(text_data=json.dumps(event))

    def send_order_to_brand(self, order):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': "hola lol",
            }
        )


class CollectionCodeConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.collection_code = None
        self.room_group_name = None
        self.order = None

    def connect(self):
        self.collection_code = self.scope['url_route']['kwargs']['collection_code']
        self.room_group_name = f'{self.collection_code}'
        self.order = Order.objects.filter(order_collection_code=self.collection_code)

        if self.order:
            print("YES COLLECTION CODE")
            # connection has to be accepted
            self.accept()

            # join the room group
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name,
                self.channel_name,
            )

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name,
        )

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message', None)
        if message is not None:
            # Do stuff.
            pass

    def chat_message(self, event):
        self.send(text_data=json.dumps(event))

    def send_collection_notification(self, order=None, status=None):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': "",
            }
        )
