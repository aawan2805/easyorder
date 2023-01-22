import base64
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth import authenticate, get_user_model

# Import the forms
from panel.forms import *


class LoginUser(LoginView):
    template_name = 'registration/login.html'
    success_url = reverse_lazy('panel:platos')

    def get(self, request, *args, **kwargs):
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
        qs = Dish.objects.filter(brand=self.request.user.profile.brand)
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


class EditDish(UpdateView):
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


class DeleteDish(DeleteView):
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
            self.object.delete()

            messages.success(request, f'Plato {dish_name} eliminado con éxito.')
        else:
            messages.success(request, f'No se pudo borrar el plato {dish_name}. Porfavor inténtelo más tarde.')

        return redirect(self.get_success_url())


class OrdersView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders.html'

    def get_queryset(self):
        qs = Order.objects.filter(brand=self.request.user.profile.brand).prefetch_related('dishes')
        return qs

