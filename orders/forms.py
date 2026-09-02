import re

from django import forms


class CustomerNameForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        strip=True,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Enter your name',
                'autocomplete': 'name',
                'required': True,
            }
        ),
    )


class CheckoutForm(forms.Form):
    phone_number = forms.CharField(
        max_length=15,
        widget=forms.TelInput(
            attrs={
                'placeholder': '10-digit mobile number',
                'autocomplete': 'tel',
                'inputmode': 'numeric',
                'required': True,
            }
        ),
    )
    table_number = forms.ChoiceField(
        choices=[('', 'Select your table')] + [
            (str(number), f'Table {number}') for number in range(1, 21)
        ],
        widget=forms.Select(attrs={'required': True}),
    )

    def clean_phone_number(self):
        phone_number = re.sub(r'[\s-]', '', self.cleaned_data['phone_number'])
        if phone_number.startswith('+91'):
            phone_number = phone_number[3:]

        if not re.fullmatch(r'[6-9]\d{9}', phone_number):
            raise forms.ValidationError('Enter a valid 10-digit Indian mobile number.')
        return phone_number

    def clean_table_number(self):
        return int(self.cleaned_data['table_number'])
