import json, os
import channels.layers
from asgiref.sync import async_to_sync
from typing import Any
from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.views import LoginView
from django.db import models
from django.urls import reverse_lazy
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth import authenticate, get_user_model
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.views.generic import TemplateView
from django.db.models import Sum, Q
# Import the forms
from panel.forms import *
from panel.constants import ORDER_DELIVERED, ORDER_PREPARED


class LoginUser(LoginView):
    template_name = 'registration/login.html'
    success_url = reverse_lazy('panel:platos')

    def get(self, request, *args, **kwargs):
        print("OK")
        return super().get(self, request, *args, **kwargs)
 
    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        usr = request.POST.get('username')
        passw = request.POST.get('password')
        auth = authenticate(request, username=usr, password=passw)
        print(auth)


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print("UUID",self.request.user.profile.brand.uuid)
        data = AdditionalOrder.objects.raw("""
            SELECT po.order_placed_at::timestamp::date as id, COUNT(*) AS cnt FROM panel_order po
            JOIN brand b ON b.uuid=po.brand_id
            WHERE b.uuid='{}'
            GROUP BY po.order_placed_at::timestamp::date;
        """.format(str(self.request.user.profile.brand.uuid)))
        context["qs"] = data

        total_amount = Order.objects.filter(brand=self.request.user.profile.brand).aggregate(Sum('amount'))
        context["total_amount"] = total_amount

        context["total_orders"] = Order.objects.filter(brand=self.request.user.profile.brand, status=ORDER_DELIVERED).count()

        context["total_unfinished_orders"] = Order.objects.filter(brand=self.request.user.profile.brand).filter(Q(status=ORDER_DELIVERED) | Q(status=ORDER_PREPARED)).count()

        context["has_orders"] = True if len(data) > 0 else False

        return context

class Platos(LoginRequiredMixin, ListView):
    model = Dish
    template_name = 'platos.html'
    brand_active = True
    chain_has_categories = True

    def render_to_response(self, context, **response_kwargs):
        context.update({"active": self.brand_active})
        context.update({"has_categories": True if self.chain_has_categories > 0 else False})

        response_kwargs.setdefault("content_type", self.content_type)

        return self.response_class(
            request=self.request,
            template=self.get_template_names(),
            context=context,
            using=self.template_engine,
            **response_kwargs,
        )

    def get_queryset(self):
        qs = Dish.objects.filter(brand=self.request.user.profile.brand, deleted=False)
        self.brand_active = self.request.user.profile.brand.active
        self.chain_has_categories = len(self.request.user.profile.brand.categories.filter(deleted=False, active=True))
        return qs


class AddDishView(LoginRequiredMixin, CreateView):
    """This class is to add a branch."""
    template_name = 'add-plato.html' 
    success_url = reverse_lazy('panel:home')
    form_class = AddDish
    model = Dish
    object = None
    http_method_names = ['get', 'post']
    failed_redirect = reverse_lazy('panel:home')

    def post(self, request, *args, **kwargs):
        form = self.get_form_class()
        data_form = form(self.request.user, self.request.POST, self.request.FILES)

        if data_form.is_valid():
            created_dish = data_form.save(brand=self.request.user.profile.brand)
            messages.success(self.request, f'Plato {data_form.cleaned_data.get("name")} creado.') 

        if not data_form.is_valid():
            print(data_form.errors.as_data())
            messages.error(self.request, 'Please correct the errors below:')
            return render(self.request, self.template_name, {'form': data_form})            

        self.success_url = reverse_lazy('panel:platos')
        return redirect(self.success_url) 

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs


class EditDishUpdate(View):
    pass


class EditDish(LoginRequiredMixin, UpdateView):
    form_class = EditDishForm
    model = Dish
    pk_url_kwarg = 'dish_id'
    template_name = 'edit-plato.html'
    success_url = reverse_lazy('panel:platos')

    def get(self, request, *args, **kwargs):
        if self.request.user.profile.brand != self.get_object().brand:
            return redirect(self.get_success_url())
        
        x = super().get(self, request, *args, **kwargs)
        return x

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def get_context_data(self, **kwargs):
        data =  super().get_context_data(**kwargs)
        data['uuid'] = self.get_object().uuid
        return data


class DeleteDish(LoginRequiredMixin, DeleteView):
    model = Dish
    pk_url_kwarg = 'dish_id'
    template_name = 'dish_confirm_delete.html'
    success_url = reverse_lazy('panel:platos')

    def delete(self, request, *args, **kwargs):
        """
        Call the delete() method on the fetched object and then redirect to the
        success URL.
        """
        self.object = self.get_object()

        # Check que el plato pertenece a éste dueño.
        if self.request.user.profile.brand == self.object.brand:
            dish_name = self.object.name
            self.object.deleted = True
            self.object.save()

            total_dishes_brand = len(self.object.brand.dishes.filter(deleted=True))
            if total_dishes_brand <= 0:
                br = self.object.brand
                br.active = False
                br.save()

            messages.success(request, f'Plato {dish_name} eliminado con éxito.')
        else:
            messages.success(request, f'No se pudo borrar el plato {dish_name}. Porfavor inténtelo más tarde.')

        return redirect(self.get_success_url())


class OrdersView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders.html'

    def get_queryset(self):
        qs = Order.objects.filter(brand=self.request.user.profile.brand).prefetch_related('dishes').order_by('-order_placed_at', 'status')

        data = {
            'orders': [],
            'brand_uuid': self.request.user.profile.brand.uuid
        }
        for order in qs:
            data['orders'].append({
                'id': order.id,
                'order_placed_at': order.order_placed_at,
                'order_delivered_at': order.order_delivered_at,
                'ws_code': order.ws_code,
                'status': order.status,
                'dishes': list(AdditionalOrder.objects.filter(order=order).select_related("dish").values("dish__name", "exclude_ingredients", "quantity")),
                'brand_id': order.brand_id,
                'amount': order.amount,
                'collection_code': order.order_collection_code,
                'selected': False,
                'error': False,
                'green': False,
            })

        return data

    def get_context_data(self, **kwargs):
        cd = super().get_context_data(**kwargs)
        cd.update({"object_list": json.dumps(cd.get('object_list'), cls=DjangoJSONEncoder)})
        return cd


class ChangeOrderStatus(LoginRequiredMixin, View):
    form_class = ChangeOrderStatusForm
    success_url = reverse_lazy('panel:orders')
    template_name = 'orders.html'
    allowed_methods = ["post"]

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form_data = self.form_class(data=request.POST)
        request_order = None
        if form_data.is_valid():
            try:
                new_status = form_data.cleaned_data.get('status')
                request_order = get_object_or_404(Order, id=self.kwargs.get('order_id'))
                request_order.status = new_status
                if new_status == ORDER_DELIVERED:
                    request_order.order_delivered_at = timezone.now()
                request_order.save()
            except:
                messages.error(request, 'An error occured changing status. Try again.')
                return redirect(self.success_url)

        qs = Order.objects.filter(brand=self.request.user.profile.brand).prefetch_related('dishes').order_by('-order_placed_at')
        data = {
            'orders': [],
            'brand_uuid': self.request.user.profile.brand.uuid
        }            
        for order in qs:
            order_dict = {
                'id': order.id,
                'order_placed_at': order.order_placed_at,
                'order_delivered_at': order.order_delivered_at,
                'ws_code': order.ws_code,
                'status': order.status,
                'dishes': list(AdditionalOrder.objects.filter(order=order).select_related("dish").values("dish__name", "exclude_ingredients", "quantity")),
                'brand_id': order.brand_id,
                'amount': order.amount,
                'collection_code': order.order_collection_code,
                'selected': False,
                'error': False,
                'green': False,
            }
            if request_order is not None:
                if order.id == request_order.id:
                    order_dict.update({'green': True})
                    try:
                        channel_layer = channels.layers.get_channel_layer()
                        async_to_sync(channel_layer.group_send)(
                            f'{request_order.order_collection_code}',
                            {
                                'type': 'chat_message',
                                'status': f'{request_order.status}',
                                'order_id': f'{request_order.id}'
                            }
                        )
                    except:
                        print("Failed to send notification to the client.")
            else:
                order_dict.update({'selected': True})

            data['orders'].append(order_dict)
        return render(request, self.template_name, {"object_list": json.dumps(data, cls=DjangoJSONEncoder)})

    # def get_contextt_data(self, **kwargs):
    #     cd = super().get_context_data(**kwargs)
    #     cd.update({"object_list": json.dumps(cd.get('object_list'), cls=DjangoJSONEncoder)})
    #     return cd



class Categories(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'categories.html'

    def get_queryset(self):
        qs = Category.objects.filter(brand=self.request.user.profile.brand, deleted=False)
        return qs


class EditCategory(LoginRequiredMixin, UpdateView):
    form_class = EditCategoryForm
    model = Category
    pk_url_kwarg = 'category_id'
    template_name = 'edit-category.html'
    success_url = reverse_lazy('panel:categorias')

    def get(self, request, *args, **kwargs):
        if self.request.user.profile.brand != self.get_object().brand:
            messages.error(request=request, message="Ha ocrrudo un error. Inténtalo de nuevo más tarde.")
            return redirect(self.get_success_url())
        
        x = super().get(self, request, *args, **kwargs)
        return x

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def get_context_data(self, **kwargs):
        data =  super().get_context_data(**kwargs)
        data['uuid'] = self.get_object().uuid
        return data


class AddCategoryView(LoginRequiredMixin, CreateView):
    """This class is to add a category."""
    template_name = 'add-category.html' 
    success_url = reverse_lazy('panel:categorias')
    form_class = AddCategoryFrom
    model = Category
    object = None
    http_method_names = ['get', 'post']
    failed_redirect = reverse_lazy('panel:home')

    def post(self, request, *args, **kwargs):
        form = self.get_form_class()
        data_form = form(self.request.user, self.request.POST)

        if data_form.is_valid():
            created_category = data_form.save()
            messages.success(self.request, f'Categoría {data_form.cleaned_data.get("name")} creada.') 

        if not data_form.is_valid():
            print(data_form.errors.as_data()) 
            messages.error(self.request, 'Por favor corrige los siguientes errores:')
            return render(self.request, self.template_name, {'form': data_form})            

        self.success_url = reverse_lazy('panel:categorias')
        return redirect(self.success_url) 

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs


class DeleteCategory(LoginRequiredMixin, DeleteView):
    model = Category
    pk_url_kwarg = 'category_id'
    template_name = 'category_confirm_delete.html'
    success_url = reverse_lazy('panel:categorias')

    def delete(self, request, *args, **kwargs):
        """
        Call the delete() method on the fetched object and then redirect to the
        success URL.
        """
        self.object = self.get_object()

        # Check que el plato pertenece a éste dueño.
        if self.request.user.profile.brand == self.object.brand:
            related_dishes = self.object.dishes.all()
            if related_dishes:
                related_dishes.update(deleted=True, active=False)

            category_name = self.object.name
            self.object.deleted = True
            self.object.save()

            messages.success(request, f'Categoría {category_name} eliminada con éxito. Se han eliminado {len(related_dishes)} platos asociados a ésta cregoría.')
        else:
            messages.success(request, f'No se pudo borrar la categoría {category_name}. Porfavor inténtelo más tarde.')

        return redirect(self.get_success_url())


class RegisterView(CreateView):
    """This class is to add a new branch."""
    template_name = 'registration/register.html' 
    success_url = reverse_lazy('panel:login')
    form_class = RegistrationForm
    model = Register
    object = None
    http_method_names = ['get', 'post']
    failed_redirect = reverse_lazy('panel:register-new-brand')
    pk_url_kwarg = 'register_token'

    def get(self, request, *args, **kwargs):
        form = self.form_class
        uuid = kwargs['register_token']
        return render(request, self.template_name, {'form': form, 'uuid': uuid})

    def post(self, request, *args, **kwargs):
        form = self.get_form_class()
        data_form = form(self.request.POST)
        if data_form.is_valid():
            # Verify if the token is valid.
            tk = Register.objects.filter(token=self.kwargs.get('register_token', None))
            if not tk or not tk[0].active or (tk[0].token != self.kwargs.get('register_token')):
                messages.warning(self.request, 'Brand or Token is already registered. Please log in.')
                return redirect(self.success_url)

            created_user = data_form.save(token=tk[0])
            uuid = self.kwargs['register_token']

            if created_user:
                tk[0].active = False
                tk[0].save()
                messages.success(self.request, f'Usuario {data_form.cleaned_data.get("username")} creado.') 
            else:
                messages.error(self.request, f'No se ha podido crear el usuario. Inténtalo más tarde.') 
                return render(self.request, self.template_name, {'form': data_form, 'uuid': self.kwargs['register_token']})

        if not data_form.is_valid():
            messages.error(self.request, 'Por favor corrige los errores.')
            return render(self.request, self.template_name, {'form': data_form, 'uuid': self.kwargs['register_token']})

        return redirect(self.success_url) 


class QRBrand(LoginRequiredMixin, View):
    allowed_methods = ["get"]
    template_name = 'qr.html'

    def get(self, request, *args, **kwargs):
        path_to_save_qr = os.path.join(settings.MEDIA_URL, 'brands')
        return render(request, self.template_name, {
            'img': path_to_save_qr + f'/qr_{request.user.profile.brand.uuid}.png'
        })


# Password reset methods
