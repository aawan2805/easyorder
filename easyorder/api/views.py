import json
import channels.layers
from asgiref.sync import async_to_sync
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponseNotFound
from django.http import JsonResponse

from django.utils import timezone
from django.core import serializers as django_serializer
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView, CreateAPIView
from api.serializers import PlatosSerializer, ListCategoryByUuid, PostNewOrder
from panel.models import *
from rest_framework import status
from rest_framework.response import Response

from api.helper import ApiResponse
from panel.models import *
import uuid

from api.serializers import OrderSerializer, SummaryOrderStatusSerializer


class DishView(ListAPIView):
    http_method_names = ['get'] 
    serializer_class = PlatosSerializer
    model = Dish
    lookup_field = 'brand_uuid'

    def get_queryset(self):
        brand_uuid = self.kwargs.get('brand_uuid')
        category_uuid = self.kwargs.get('category_uuid')
        brand = get_object_or_404(Brand, uuid=brand_uuid)
        category = get_object_or_404(Category, uuid=category_uuid)

        return Dish.objects.filter(brand=brand, category=category, active=True, deleted=False)


    # def get(self, request, *args, **kwargs):
    #     response = super().get(self, request, *args, **kwargs)
    #     response['Access-Control-Allow-Credentials'] = 'true'
    #     return response


class CategoryView(ListAPIView):
    http_method_names = ['get'] 
    serializer_class = ListCategoryByUuid
    model = Category
    lookup_field = 'brand_uuid'
    brand = None

    def get_queryset(self):
        brand_uuid = self.kwargs.get('brand_uuid')
        brand = get_object_or_404(Brand, uuid=brand_uuid)

        categories = []
        for category in Category.objects.filter(brand=brand, active=True, deleted=False):
            categories.append({
                "key": category.uuid,
                "icon": "",
                "label": category.name 
            })

        return categories

    # def get(self, request, *args, **kwargs):
    #     response = super().get(self, request, *args, **kwargs)
    #     if 'brand' not in request.COOKIES:
    #         # Setting the cookie for 30 mins to store the brand uuid
    #         response.set_cookie('brand', self.brand or self.kwargs.get('brand_uuid'), max_age=30)
    #     else:
    #         print(request.COOKIES['brand'])

    #     response['Access-Control-Allow-Credentials'] = 'true'
    #     return response


class OrderView(CreateAPIView):
    serializer_class = PostNewOrder

    def create(self, request, *args, **kwargs):
        dd = json.loads(request.data.get('body'))
        print(json.dumps(dd, indent=4))
        # for dish in dd['dishes']:
        #     dish['dish_uuid'] = uuid.UUID(dish['dish_uuid'])
        # dd['brand_uuid'] = uuid.UUID(dd['brand_uuid'])

        serializer = PostNewOrder(data=dd)

        if serializer.is_valid():
            total_amount = 0.0
        
            all_dishes = [{"dish": dish["dish_uuid"], "exclude_ingredients": dish["exclude_ingredients"], "quantity": dish["quantity"]} for dish in serializer.data['dishes']]
            for dish in all_dishes:
                aux = get_object_or_404(Dish, uuid=uuid.UUID(dish["dish"]))
                total_amount += (dish["quantity"] * aux.price)
            new_order = Order(order_placed_at=timezone.now(),
                              order_delivered_at=None,
                              brand=Brand.objects.get(uuid=uuid.UUID(serializer.data['brand_uuid'])),
                              amount=total_amount)
            # Set ws code and collection code

            new_order.save()
            new_order.set_order_collection_code()
            # new_order.set_random_ws()
            # Add dishes to the intermediary table
            for obj in all_dishes:
                x = AdditionalOrder.objects.create(order=new_order,
                                               dish=Dish.objects.get(uuid=uuid.UUID(obj['dish'])),
                                               quantity=obj['quantity'],
                                               exclude_ingredients=[ing["name"] for ing in obj['exclude_ingredients'] if ing["exclude"] == True])
#                new_order.dishes.add(dish)
            new_order.save()

            headers = self.get_success_headers(serializer.data)
            rsp = ApiResponse(data={
                                    "msg": f'Order placed! Your tracking number is {new_order.order_collection_code}',
                                    "store": True,
                                    "delete_prev": True,
                                    "collection_code": new_order.order_collection_code
                                   },
                              status=status.HTTP_201_CREATED,
                              headers=headers
                             )

        
            order_json = {
                'id': new_order.id,
                'order_placed_at': new_order.order_placed_at,
                'order_delivered_at': new_order.order_delivered_at,
                'ws_code': new_order.ws_code,
                'status': new_order.status,
                'dishes': list(AdditionalOrder.objects.filter(order=new_order).select_related("dish").values("dish__name", "dish__price", "exclude_ingredients")),
                'brand_id': new_order.brand_id,
                'amount': new_order.amount,
                'collection_code': new_order.order_collection_code,
                'selected': False
            }

            try:
                channel_layer = channels.layers.get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f'orders_{new_order.brand.uuid}',
                    {
                        'type': 'chat_message',
                        'message': json.dumps(order_json, cls=DjangoJSONEncoder),
                    }
                )
            except:
                print("Couldn't send notification to restaurant.")

            return rsp.get_response()
    
        print("Errors", serializer.errors)
        return Response(data=None, status=status.HTTP_401_UNAUTHORIZED)

class OrderStatus(ListAPIView):
    http_method_names = ['get'] 
    serializer_class = None
    model = Order
    lookup_field = 'collection_code'

    def get(self, request, *args, **kwargs):
        collection_code = self.kwargs.get('collection_code', None)
        if collection_code:
            order = get_object_or_404(Order, order_collection_code=collection_code)
            if order.status == 4:
                return JsonResponse({'remove_token': True}, status=200)
            return JsonResponse({'remove_token': False}, status=200)

        return HttpResponseNotFound()


class QRStatus(ListAPIView):
    http_method_names = ['get'] 
    serializer_class = None
    model = Brand
    lookup_field = 'brand_uuid'

    def get(self, request, *args, **kwargs):
        brand_uuid = self.kwargs.get('brand_uuid', None)
        if brand_uuid:
            brand = get_object_or_404(Brand, uuid=brand_uuid)
            if brand.active:
                return JsonResponse({'qr_ok': True}, status=200)
            return JsonResponse({'qr_ok': False}, status=200)

        return HttpResponseNotFound()


class SummaryOrderStatus(ListAPIView):
    http_method_names = ['get'] 
    serializer_class = SummaryOrderStatusSerializer
    model = Order
    lookup_field = 'collection_code'

    def get(self, request, *args, **kwargs):
        try:
            collection_code = self.kwargs.get(self.lookup_field, None)
            order = Order.objects.get(order_collection_code=collection_code)
            dishes_ingredients = AdditionalOrder.objects.filter(order=order).select_related("dish").values("dish__name", "dish__price", "exclude_ingredients")
            order_status = order.status
            return Response(data={"dishes": dishes_ingredients, "order_status": order_status})
        except Order.DoesNotExist:
            print("Unknown object")
            return Response(data=None, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response(data=None, status=status.HTTP_404_NOT_FOUND)
