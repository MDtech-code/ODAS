from django import forms
from django.core.exceptions import ValidationError
import phonenumbers
from phonenumbers import phonenumberutil
import datetime

class AgeValidationMixin:
    min_age = 18  # Default minimum age

    def clean_date_of_birth(self):
        dob = self.cleaned_data['date_of_birth']
        today = datetime.date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        if age < self.min_age:
            raise ValidationError(f"You must be at least {self.min_age} years old.")
        return dob

class PhoneNumberValidationMixin:
    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        try:
            parsed_number = phonenumbers.parse(phone_number)
            if not phonenumbers.is_valid_number(parsed_number):
                raise forms.ValidationError("Invalid phone number.")
            return phonenumberutil.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
        except phonenumbers.phonenumberutil.NumberParseException:
            raise forms.ValidationError("Invalid phone number format.")

