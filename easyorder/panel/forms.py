from django import forms
from panel.models import *
from django.forms import ModelForm
from django.conf import settings


class AddDish(ModelForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        # Displays the label isnted of id in the input.

        category_query_set = Category.objects.filter(brand=self.user.profile.brand)
        self.fields['category'] = forms.ModelChoiceField(queryset=category_query_set, empty_label=None, widget=forms.Select(attrs={'class': 'form-control','data-live-search': 'true', 'title':'Choose one of the following...'}), required=True)
        self.fields['category'].label_from_instance = lambda category: '{}'.format(category.name)
                
        self.fields['photo'].widget.attrs['class'] = 'custom-file-input'
        self.fields['photo'].widget.attrs['id'] = 'image'
    
    # image = forms.ImageField(required=True)
    ingredients = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'ingredients', 'data-role': 'tagsinput'}), required=False)
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
        new_dish.save()

        return new_dish


class EditDishForm(ModelForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.current_image = str(settings.MEDIA_URL) + str(self.instance.photo)

        category_query_set = Category.objects.filter(brand=self.user.profile.brand)
        self.fields['category'] = forms.ModelChoiceField(queryset=category_query_set, empty_label=None, widget=forms.Select(attrs={'class': 'form-control','data-live-search': 'true', 'title':'Choose one of the following...'}), required=True)
        self.fields['category'].label_from_instance = lambda category: '{}'.format(category.name)

        self.fields['current_photo'].initial = self.current_image

        self.fields['new_photo'].widget.attrs['class'] = 'custom-file-input'
        self.fields['new_photo'].widget.attrs['id'] = 'image'

        self.fields['ingredients'].initial = ",".join(self.instance.ingredients)

        self.fields['tags'].initial = ",".join(self.instance.tags)

    current_photo = forms.CharField(required=False)
    new_photo = forms.ImageField(required=False)

    class Meta:
        model = Dish
        fields = ['name', 'description', 'price', 'active', 'ingredients', 'tags', 'category', 'new_photo']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.TextInput(attrs={'class': 'form-control'}),
            'ingredients': forms.TextInput(attrs={'class': 'form-control', 'id': 'ingredients', 'data-role': 'tagsinput'}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 'id': 'tags', 'data-role': 'tagsinput'}),
        }

    def save(self, commit=False):
        self.cleaned_data.pop('current_photo')
        pic = self.cleaned_data.pop('new_photo')

        parent_dish = super().save(self)

        if pic:
            parent_dish.photo = pic

        parent_dish.save()

        return parent_dish
