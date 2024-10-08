from django import forms
from panel.models import *
from django.forms import ModelForm, Form
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
import qrcode
import os

class AddDish(ModelForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        # Displays the label isnted of id in the input.

        category_query_set = Category.objects.filter(brand=self.user.profile.brand, deleted=False)
        self.fields['category'] = forms.ModelChoiceField(queryset=category_query_set, empty_label=None, widget=forms.Select(attrs={'class': 'form-control','data-live-search': 'true', 'title':'Choose one of the following...'}), required=True)
        self.fields['category'].label_from_instance = lambda category: '{}'.format(category.name)
                
        self.fields['photo'].widget.attrs['class'] = 'custom-file-input'
        self.fields['photo'].widget.attrs['id'] = 'image'
    
    # image = forms.ImageField(required=True)
    ingredients = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'ingredients', 'data-role': 'tagsinput'}), required=True)
    tags = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'tags', 'data-role': 'tagsinput'}), required=False)
 
    class Meta: 
        model = Dish
        fields = ['name', 'description', 'price', 'active', 'category', 'photo']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def save(self, brand, commit=False):
        # self.cleaned_data.pop('image')
        new_dish = Dish(**self.cleaned_data)
        new_dish.brand = brand
        # new_dish.ingredients = parse_ingredients(self.cleaned_data.pop('ingredients', False))
        new_dish.ingredients = self.cleaned_data.pop('ingredients', '').split(',')
        # new_dish.tags = parse_tags(self.cleaned_data.pop('tags', False))
        new_dish.tags = self.cleaned_data.pop('tags', '').split(',')
        new_dish.active = self.cleaned_data.get('active')
        new_dish.save()

        # Mark brand as active.
        if not brand.active:
            brand.active = True
            brand.save()
            print("[INFO]: Brand is now active.")
        return new_dish


class EditDishForm(ModelForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.current_image = str(settings.MEDIA_URL) + str(self.instance.photo)

        category_query_set = Category.objects.filter(brand=self.user.profile.brand, deleted=False)
        self.fields['category'] = forms.ModelChoiceField(queryset=category_query_set, empty_label=None, widget=forms.Select(attrs={'class': 'form-control','data-live-search': 'true', 'title':'Choose one of the following...'}), required=True)
        self.fields['category'].label_from_instance = lambda category: '{}'.format(category.name)

        self.fields['current_photo'].initial = self.current_image

        self.fields['new_photo'].widget.attrs['class'] = 'custom-file-input'
        self.fields['new_photo'].widget.attrs['id'] = 'image'

        self.fields['ingredients2'].initial = ", ".join(self.instance.ingredients)

        self.fields['tags2'].initial = ", ".join(self.instance.tags)

    current_photo = forms.CharField(required=False)
    new_photo = forms.ImageField(required=False)
    ingredients2 = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'ingredients', 'data-role': 'tagsinput'}))
    tags2 = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'tags', 'data-role': 'tagsinput'}), required=False)

    class Meta:
        model = Dish
        fields = ['name', 'description', 'price', 'active', 'ingredients2', 'tags2', 'category', 'new_photo']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.TextInput(attrs={'class': 'form-control'}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 'id': 'tags', 'data-role': 'tagsinput'}),
        }

    def save(self, commit=False):
        self.cleaned_data.pop('current_photo')
        pic = self.cleaned_data.pop('new_photo')
        ingreds = self.cleaned_data.pop('ingredients2')
        tgs = self.cleaned_data.pop('tags2')

        parent_dish = super().save(self)
        if pic:
            parent_dish.photo = pic

        parent_dish.ingredients = ingreds.split(",")
        parent_dish.tags = tgs.split(",")
        parent_dish.active = self.cleaned_data.get('active', False)
        parent_dish.save()

        return parent_dish


class ChangeOrderStatusForm(ModelForm):
    class Meta:
        model = Order
        fields = ['status']


class EditCategoryForm(ModelForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    class Meta:
        model = Category
        fields = ['name', 'icon', 'default', 'active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'icon': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_default(self):
        if self.cleaned_data.get('default', False):
            data = Category.objects.filter(default=True, brand=self.user.profile.brand).exclude(uuid=self.instance.uuid)
            if data:
                raise forms.ValidationError('Ya existe una categoría por defecto.')
        
        return self.cleaned_data.get('default')


class AddCategoryFrom(ModelForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
 
    class Meta: 
        model = Category
        fields = ['name', 'icon', 'default', 'active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'icon': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_default(self):
        if self.cleaned_data.get('default', False):
            data = Category.objects.filter(default=True, brand=self.user.profile.brand)
            if data:
                raise forms.ValidationError('Ya existe una categoría por defecto.')
        
        return self.cleaned_data.get('default')

    def save(self, commit=False):
        new_category = Category(**self.cleaned_data)
        new_category.brand = self.user.profile.brand
        new_category.save()
        return new_category


class RegistrationForm(ModelForm):
    name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_name'}))
    phone_number = forms.CharField(max_length=9, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'phone_number'}))
    main_address = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'main_address'}))

    def save(self, commit=False, token=None):
        try:
            # Add the user
            # Add brand
            # Add profile
            # Associate all of them
            # Invalidate the token
            new_user = User.objects.create(username=self.cleaned_data.get('username'),
                            first_name=self.cleaned_data.get('first_name'),
                            last_name=self.cleaned_data.get('last_name'),
                            email=token.email)
            new_user.set_password(self.cleaned_data.get('password'))
            new_user.save()

            # Generate the QR code
            new_brand = Brand.objects.create(name=self.cleaned_data.get('name'),
                                phone_number=self.cleaned_data.get('phone_number'),
                                main_address=self.cleaned_data.get('main_address'),
                                email=token.email)
            new_brand.save()

            try:
                qr_image = qrcode.make(new_brand.uuid)
                path_to_save_qr = os.path.join(settings.MEDIA_ROOT, 'brands')
                qr_image.save(path_to_save_qr + f'/qr_{new_brand.uuid}.png')
            except:
                print("Could not save QR image.")

            Profile.objects.create(user=new_user, 
                                    brand=new_brand, 
                                    address=self.cleaned_data.get('address')).save()
            return True
        except:
            return False

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password'] 
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'id': 'inputUsername'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'id': 'inputfirstname'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'id': 'inputlastname'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'id': 'inputEmail'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control', 'id': 'inputPassword'}),
        }