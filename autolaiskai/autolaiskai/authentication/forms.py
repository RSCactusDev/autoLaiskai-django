from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate

from authentication.models import CustomUser


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        max_length=255, 
        help_text="Prašome įvesti galiojantį el. pašto adresą.",
        error_messages={'required': 'Prašome įvesti el. pašto adresą.'}
    )

    kv_nr = forms.CharField(error_messages={'required': 'Prašome įvesti kvalifikacijos pažymėjimo numerį.'})
    first_name = forms.CharField(error_messages={'required': 'Prašome įvesti Varda.'})
    last_name = forms.CharField(error_messages={'required': 'Prašome įvesti Pavarde.'})
    password1 = forms.CharField(error_messages={'required': 'Pašome įvesti slaptažodį.'})
    password2 = forms.CharField(error_messages={'required': 'Pašome įvesti slaptažodį.'})
    
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name','last_name','kv_nr','password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        try:
            customuser = CustomUser.objects.get(email=email)
        except:
            return email
        raise forms.ValidationError(f"El. paštas {email} jau naudojamas.")
 

    def clean_kv_nr(self):
        kv_nr = self.cleaned_data['kv_nr']
        try:
            customuser = CustomUser.objects.get(kv_nr=kv_nr)
        except:
            return kv_nr
        raise forms.ValidationError(f"Kvalifikacijos pažymėjimas: {kv_nr} jau naudojamas.")   

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Slaptažodiai nesutampa.")
        
        return password2
    
  

class LoginForm(forms.ModelForm):   
    password = forms.CharField(label="Password", widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ("email", "password")

    def clean(self):
        if self.is_valid():
            email = self.cleaned_data['email']
            password = self.cleaned_data['password']
            if not authenticate(email=email, password=password):
                raise forms.ValidationError("Neteisingai suvesti duomenys")