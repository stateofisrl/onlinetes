from django import forms
from .models import Order, SupportMessage, Investment


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['vehicle', 'name', 'email', 'phone', 'address']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Full delivery address'}),
        }


class PaymentProofForm(forms.Form):
    payment_proof = forms.CharField(
        max_length=500,
        label='Transaction Hash / Proof',
        widget=forms.TextInput(attrs={'placeholder': 'Enter transaction hash or payment reference'})
    )
    payment_proof_image = forms.URLField(
        required=False,
        label='Payment Screenshot URL (optional)',
        widget=forms.URLInput(attrs={'placeholder': 'https://example.com/screenshot.png'})
    )


class SupportForm(forms.ModelForm):
    class Meta:
        model = SupportMessage
        fields = ['name', 'email', 'message']


class TrackingLookupForm(forms.Form):
    tracking_id = forms.CharField(max_length=100, label='Tracking ID')


class InvestmentForm(forms.ModelForm):
    class Meta:
        model = Investment
        fields = ['full_name', 'email', 'phone', 'tier', 'capital', 'message']
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Full Name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email address'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Phone number (optional)'}),
            'tier': forms.Select(attrs={'required': 'required'}),
            'capital': forms.NumberInput(attrs={'placeholder': 'Investment amount (USD)', 'min': '100', 'max': '10000000', 'step': '1'}),
            'message': forms.Textarea(attrs={'placeholder': 'Additional information (optional)', 'rows': 5}),
        }

    def clean_capital(self):
        c = self.cleaned_data['capital']
        if c < 100:
            raise forms.ValidationError('Minimum investment is $100')
        if c > 10000000:
            raise forms.ValidationError('Maximum allowed is $10,000,000')
        return c
