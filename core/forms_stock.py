from django import forms
from .models import StockAdjustment


class StockAdjustmentForm(forms.ModelForm):
    class Meta:
        model = StockAdjustment
        fields = ["product", "quantity_change", "reason", "note"]
        widgets = {
            "quantity_change": forms.NumberInput(),
            "note": forms.TextInput(),
        }