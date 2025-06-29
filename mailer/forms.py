from django.forms import ModelForm, BooleanField, forms
from .models import Mailing


class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field, BooleanField):
                field.widget.attrs["class"] = "form-check-input"
            else:
                field.widget.attrs["class"] = "form-control"


class MailingForm(StyleFormMixin, ModelForm):
    class Meta:
        model = Mailing
        fields = ["message", "recipient", "start_datetime", "end_datetime"]

    def clean(self):
        cleaned_data = super().clean()
        start_date_time = cleaned_data.get("start_datetime")
        end_date_time = cleaned_data.get("end_datetime")

        if start_date_time and end_date_time and start_date_time >= end_date_time:
            raise forms.ValidationError("Дата начала должна быть раньше даты окончания")
        return cleaned_data
