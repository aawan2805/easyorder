from django import forms
from panel.models import *
from django.forms import ModelForm


class AddDish(ModelForm):
    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        category_query_set = Category.objects.filter(brand=user.profile.branch)
        # Displays the label isnted of id in the input.

        self.fields['category'] = forms.ModelChoiceField(queryset=category_query_set, empty_label=None, widget=forms.Select(attrs={'class': 'form-control','data-live-search': 'true', 'title':'Choose one of the following...'}), required=True)
        self.fields['category'].label_from_instance = lambda category: '{}'.format(category.name)
        self.fields['tags'].initial = None
        self.fields['image'].widget.attrs['class'] = 'custom-file-input'
        self.fields['image'].widget.attrs['id'] = 'image'
    
    image = forms.ImageField(required=False)
    ingredients = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'ingredients', 'data-role': 'tagsinput'}), required=False)
    tags = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'tags', 'data-role': 'tagsinput'}), required=False)
 
    class Meta:
        model = Dish
        fields = ['name', 'description', 'price', 'active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.TextInput(attrs={'class': 'form-control'}),
        }

    # def save(self, branch, commit=False):
    #     self.cleaned_data.pop('image')
    #     new_dish = Dish(**self.cleaned_data)
    #     new_dish.branch = branch
    #     new_dish.ingredients = parse_ingredients(self.cleaned_data.pop('ingredients', False))
    #     new_dish.tags = parse_tags(self.cleaned_data.pop('tags', False))
    #     new_dish.save()

    #     return new_dish
