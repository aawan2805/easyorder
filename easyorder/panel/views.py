from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views import View
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin

class LoginUser(LoginView):
    # authentication_form = LoginForm
    template_name = 'login.html'
    success_url = reverse_lazy('panel:home')
    redirect_authenticated_user = True


class Home(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'base.html')

