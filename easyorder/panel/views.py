import json
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth import authenticate, get_user_model
from django.shortcuts import get_object_or_404

# Import the forms
from panel.forms import *


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


class Platos(LoginRequiredMixin, ListView):
    model = Dish
    template_name = 'platos.html'

    def get_queryset(self):
        qs = Dish.objects.filter(brand=self.request.user.profile.brand, active=True)
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
            self.object.active = False
            self.object.save()

            messages.success(request, f'Plato {dish_name} eliminado con éxito.')
        else:
            messages.success(request, f'No se pudo borrar el plato {dish_name}. Porfavor inténtelo más tarde.')

        return redirect(self.get_success_url())


class OrdersView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders.html'

    def get_queryset(self):
        qs = Order.objects.filter(brand=self.request.user.profile.brand).prefetch_related('dishes').order_by('-order_placed_at')

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
                'dishes': [dish.name for dish in order.dishes.all()],
                'brand_id': order.brand_id,
                'amount': order.amount,
                'collection_code': order.order_collection_code,
                'selected': False
            })

        return data

    def get_context_data(self, **kwargs):
        cd = super().get_context_data(**kwargs)
        cd.update({"object_list": json.dumps(cd.get('object_list'), cls=DjangoJSONEncoder)})
        return cd

class ChangeOrderStatus(LoginRequiredMixin, View):
    form_class = ChangeOrderStatus
    success_url = reverse_lazy('panel:orders')

    def get(self, request, *args, **kwargs):
        order = get_object_or_404(Order, id=kwargs.get('order', -1))
        form_data = self.form_class(data=request.GET, instance=order)

        if form_data.is_valid():
            form_data.save()
        
        return redirect(self.success_url)


class Categories(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'categories.html'

    def get_queryset(self):
        qs = Category.objects.filter(brand=self.request.user.profile.brand, active=True)
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
    """This class is to add a branch."""
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
                related_dishes.update(active=False)

            category_name = self.object.name
            self.object.active = False
            self.object.save()

            messages.success(request, f'Categoría {category_name} eliminada con éxito. Se han eliminado {len(related_dishes)} platos asociados a ésta cregoría.')
        else:
            messages.success(request, f'No se pudo borrar la categoría {category_name}. Porfavor inténtelo más tarde.')

        return redirect(self.get_success_url())
