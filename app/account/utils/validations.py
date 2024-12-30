from datetime import date
from django.core.exceptions import ValidationError
from app.account.models import  Doctor
import re


def validate_min_experience(value):
     if value < 3: raise ValidationError(f'Years of experience must be at least 3 years. You entered {value}.')
