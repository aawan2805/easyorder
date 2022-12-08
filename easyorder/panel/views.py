import base64
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
from django.contrib import messages
# Import the forms
from panel.forms import *

class LoginUser(LoginView):
    # authentication_form = LoginForm
    template_name = 'login.html'
    success_url = reverse_lazy('panel:home')
    redirect_authenticated_user = True


class Home(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'platos.html')


class AddDishView(CreateView):
    """This class is to add a branch."""
    template_name = 'add-plato.html' 
    success_url = reverse_lazy('panel:home')
    form_class = AddDish
    model = Dish
    object = None
    http_method_names = ['get', 'post']
    failed_redirect = reverse_lazy('panel:home')

    def post(self, request, *args, **kwargs):
        # User is BRANCH admin.
        if self.request.user.profile.role.id not in (4,):
            if self.request.user.profile.role.id in (1, 2, 3,):
                return redirect(self.failed_redirect)

            messages.error(self.request, 'Your role does not permit you to perform this action.')
            return redirect(self.success_url)

        form = self.get_form_class()
        data_form = form(self.request.user, self.request.POST)
        image_uploaded = request.FILES.pop('image', False)

        if data_form.is_valid():
            created_dish = data_form.save(branch=self.request.user.profile.branch)
            messages.success(self.request, 'Dish created successfully.')

        if not data_form.is_valid():
            messages.error(self.request, 'Please correct the errors below:')
            return render(self.request, self.template_name, {'form': data_form})            

        self.success_url = reverse_lazy('users:admin_dishes')
        return redirect(self.success_url) 

    # def get_form_kwargs(self):
    #     kwargs = super(AdminAddBranchDishView, self).get_form_kwargs()
    #     kwargs.update({'user': self.request.user})
    #     return kwargs
