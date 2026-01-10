from django import forms

class OrderForm(forms.Form):
    first_name = forms.CharField(max_length=50, label='Имя')
    last_name = forms.CharField(max_length=50, label='Фамилия')
    email = forms.EmailField(label='Email')
    phone = forms.CharField(max_length=20, label='Телефон')
    address = forms.CharField(widget=forms.Textarea, label='Адрес')
