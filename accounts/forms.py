from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import CustomUser
import re

class CustomerRegistrationForm(UserCreationForm):
    full_name = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={'placeholder': 'Full Name'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'Address'}), required=True)
    phone = forms.CharField(max_length=15, required=True, widget=forms.TextInput(attrs={'placeholder': 'Phone Number'}))

    class Meta:
        model = CustomUser
        fields = ['email', 'full_name', 'address', 'phone', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None
        self.fields['email'].widget.attrs.update({'placeholder': 'Email Address'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm Password'})

    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name')
        if full_name and not re.match(r'^[a-zA-Z\s]+$', full_name):
            raise ValidationError("Full name can only contain letters and spaces.")
        if full_name and len(full_name.strip()) < 5:
            raise ValidationError("Full name must be at least 5 characters.")
        return full_name

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            if CustomUser.objects.filter(email=email).exists():
                raise ValidationError("This email is already registered.")
            if not re.match(r'^[a-zA-Z][a-zA-Z0-9._%+-]*@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                raise ValidationError("Enter a valid email address (cannot start with a number).")
        return email

    # ============================================================
    # FIXED: clean_phone is now properly INDENTED inside the class
    # ============================================================
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        
        if phone:
            # Remove spaces, hyphens, parentheses
            clean_phone = re.sub(r'[\s\-\(\)]', '', phone)
            
            # Check if only digits
            if not clean_phone.isdigit():
                raise ValidationError("Phone number can only contain digits.")
            
            # Check length
            if len(clean_phone) != 10:
                raise ValidationError("Phone number must be exactly 10 digits.")
            
            # Check Nepal prefix (96, 97, 98)
            if not clean_phone.startswith(('96', '97', '98')):
                raise ValidationError(
                    "Phone number must start with 96, 97, or 98 (Nepal mobile number)."
                )
            
            return clean_phone
        
        return phone

    def clean_address(self):
        address = self.cleaned_data.get('address')
        if not address:
            raise ValidationError("Address is required.")
        if address and not re.match(r'^[a-zA-Z0-9\s,.-]+$', address):
            raise ValidationError("Address can only contain letters, numbers, spaces, commas, dots, and hyphens.")
        if address and not re.search(r'[a-zA-Z]', address):
            raise ValidationError("Address must contain at least one letter.")
        return address

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if password:
            if len(password) < 5:
                raise ValidationError("Password must be at least 5 characters.")
            if not re.search(r'[A-Za-z]', password):
                raise ValidationError("Password must contain at least one letter.")
            if not re.search(r'\d', password):
                raise ValidationError("Password must contain at least one number.")
        return password

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'customer'
        if commit:
            user.save()
        return user
    



        # def clean_phone(self):
    #     phone = self.cleaned_data.get('phone')
    #     if phone:
    #         clean_phone = re.sub(r'[\s\-\(\)]', '', phone)
    #         if not clean_phone.isdigit():
    #             raise ValidationError("Phone number can only contain digits.")
    #         if len(clean_phone) != 10:
    #             raise ValidationError("Phone number must be exactly 10 digits.")
    #     return phone