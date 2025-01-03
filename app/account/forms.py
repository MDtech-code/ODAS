from django import forms
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from app.account.models import Patient, User,Doctor,Speciality,Report,DoctorAvailability,PaymentMethod
from app.account.mixins.validation_mixins import AgeValidationMixin, PhoneNumberValidationMixin
from app.account.utils.validations import validate_min_experience


#! patient form
# class PatientRegistrationForm(UserCreationForm,AgeValidationMixin, PhoneNumberValidationMixin):
#     """
#     Form for registering a new patient. Extends the default UserCreationForm
#     and includes additional fields for the Patient model.
#     """
#     min_age = 18
#     email = forms.EmailField(required=True, help_text="Enter a valid email address.")
#     gender = forms.ChoiceField(choices=Patient.GENDER_CHOICES, required=True, widget=forms.RadioSelect)
#     date_of_birth = forms.DateField(
#         required=True,
#         widget=forms.DateInput(attrs={'type': 'date'}),
#         help_text="You must be at least 18 years old to register.",
#     )
#     phone_number = forms.CharField(
#         required=True,
#         help_text="Include your country code. Format: +923001234567",
#     )
    
#     class Meta:
#         model = User
#         fields = ['username', 'email', 'gender', 'date_of_birth', 'phone_number', 'password1', 'password2']

class PatientRegistrationForm(UserCreationForm):
    """
    Form for registering a new patient. Extends the default UserCreationForm
    and includes additional fields for the Patient model.
    """
    min_age = 18
    email = forms.EmailField(
        required=True, 
        help_text="Enter a valid email address.",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'})
    )
    gender = forms.ChoiceField(
        choices=Patient.GENDER_CHOICES, 
        required=True,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    date_of_birth = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        help_text="You must be at least 18 years old to register.",
    )
    phone_number = forms.CharField(
        required=True,
        help_text="Include your country code. Format: +92XXXXXXXXXX",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter a  number'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'gender', 'date_of_birth', 'phone_number', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your username'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control  password-input', 'placeholder': 'Enter your password'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control   password-input', 'placeholder': 'Confirm your password'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove help text for password fields
        self.fields['password1'].help_text = ""
class PatientProfileForm(forms.ModelForm, AgeValidationMixin, PhoneNumberValidationMixin):
    min_age = 18
    first_name= forms.CharField(
        label="First Name",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your first name'}),
        required=True
    )
    last_name = forms.CharField(
        label="Last Name",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your last name'}),
        required=True
    )
    phone_number = forms.CharField(
        required=True,
        help_text="Include your country code. Format: +923001234567",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter a  number'}),
    )
    date_of_birth = forms.DateField(
        label="Date of Birth",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=True,
    )
    medical_history = forms.CharField(
        label="Medical History",
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Brief medical history'}),
        required=False
    )
    address = forms.CharField(
        label="Address",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your address'}),
        required=False
    )
    medical_conditions = forms.CharField(
        label="Medical Conditions",
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Any existing medical conditions'}),
        required=False
    )

    class Meta:
        model = Patient
        fields = ['phone_number', 'date_of_birth', 'medical_history', 'address', 'medical_conditions']
    
    def save(self, commit=True):
        # Save the Patient model fields
        patient = super().save(commit=False)
        
        # Save the User model fields
        user = patient.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            patient.save()
        return patient




class DoctorRegistrationForm(UserCreationForm,AgeValidationMixin, PhoneNumberValidationMixin):
       
    min_age = 32
    phone_number = forms.CharField(
        required=True,
        help_text="Include your country code. Format: +92XXXXXXXXXX",
        widget=forms.EmailInput(attrs={'class': 'form-control',  'placeholder': 'Enter a phone number'})
        
    )
    speciality = forms.ModelChoiceField(
        label="Speciality",
        queryset=Speciality.objects.all(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}) 
    )
    gender = forms.ChoiceField(
        label="Gender",
        choices=[('Male', 'Male'), ('Female', 'Female')],
        widget=forms.Select(attrs={'class': 'form-control'}) 

        
    )
    email = forms.EmailField(required=True, help_text="Enter a valid email address.",
                             widget=forms.EmailInput(attrs={'class': 'form-control',  'placeholder': 'Enter email'})
    )
    date_of_birth = forms.DateField(
        label="Date of Birth",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        help_text="You must be at least 32 years old to register.",
        required=True,
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'date_of_birth', 'gender','speciality', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your username'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control  password-input', 'placeholder': 'Enter your password'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control   password-input', 'placeholder': 'Confirm your password'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Retrieve all specialities from the database and dynamically populate the choices
        specialties = Speciality.objects.all().values_list('id', 'name')
        self.fields['speciality'].choices = specialties
        self.fields['password1'].help_text = ""
    
       

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'doctor'  # Set user type to doctor
        if commit:
            user.save()
            Doctor.objects.create(
                user=user,
                phone_number=self.cleaned_data['phone_number'],
                gender=self.cleaned_data['gender'],
                speciality=self.cleaned_data['speciality'],
                date_of_birth=self.cleaned_data['date_of_birth'],
            )
        return user


class DoctorProfileForm(forms.ModelForm,AgeValidationMixin, PhoneNumberValidationMixin):
    min_age = 32
    phone_number = forms.CharField(
        required=True,
        help_text="Include your country code. Format: +92XXXXXXXXXX",
        widget=forms.EmailInput(attrs={'class': 'form-control',  'placeholder': 'Enter a phone number'})
        
    )
    date_of_birth = forms.DateField(
        label="Date of Birth",
        widget=forms.DateInput(attrs={'class': 'form-control','type': 'date'}),
        help_text="You must be at least 32 years old to register.",
        required=True,
    )
    bio = forms.CharField(
        label="Bio",
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write about yourself'}),
        required=False
    )
    years_of_experience = forms.IntegerField(
        label="Years of Experience",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Years of experience'}),
        required=False,
        validators=[validate_min_experience],
    )
    consultation_fee = forms.DecimalField(
        label="Consultation Fee",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Fee'}),
        required=False,
    )
    image = forms.ImageField(
        label="Profile Picture",
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        required=False
    )
    certificate = forms.FileField(
        label="Certificate",
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = Doctor
        fields = [
            'phone_number', 'date_of_birth', 'speciality', 'bio', 
            'years_of_experience', 'consultation_fee', 'image', 'certificate'
        ]
        widgets = {
            'speciality': forms.Select(attrs={'class': 'form-control'}),
        }




class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Username or Email",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter username or email'}),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'}),
    )





class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['name', 'file']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Report Name'}),
            'file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf, .jpg, .jpeg, .png'})
        }
        labels = {
            'name': 'Report Name',
            'file': 'Upload Report (PDF/Image)'
        }

        # Optional: Specify required fields or custom validation if needed


'''
class DoctorProfileForm(forms.ModelForm,AgeValidationMixin, PhoneNumberValidationMixin):
    min_age = 38
    phone_number = forms.CharField(
        required=True,
        help_text="Include your country code. Format: +923001234567",
        
    )
    date_of_birth = forms.DateField(
        label="Date of Birth",
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text="You must be at least 38 years old to register.",
        required=True,
    )
    bio = forms.CharField(
        label="Bio",
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write about yourself'}),
        required=False
    )
    years_of_experience = forms.IntegerField(
        label="Years of Experience",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Years of experience'}),
        required=False,
    )
    consultation_fee = forms.DecimalField(
        label="Consultation Fee",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Fee'}),
        required=False,
    )
    image = forms.ImageField(
        label="Profile Picture",
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        required=False
    )
    certificate = forms.FileField(
        label="Certificate",
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = Doctor
        fields = [
            'phone_number', 'date_of_birth', 'speciality', 'bio', 
            'years_of_experience', 'consultation_fee', 'image', 'certificate'
        ]





class DoctorAvailabilityForm(forms.ModelForm):
    class Meta:
        model = DoctorAvailability
        fields = ['day_of_week', 'start_time', 'end_time']
    
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time >= end_time:
            raise forms.ValidationError("Start time must be earlier than end time.")
        
        return cleaned_data
    

class PaymentMethodForm(forms.ModelForm):
    class Meta:
        model = PaymentMethod
        fields = ['payment_type', 'account_number', 'iban', 'bank_name', 'card_number', 'card_expiry', 'card_holder_name']

'''




#  def clean_gender(self):
#         gender = self.cleaned_data['gender']
#         if gender not in [Doctor.MALE, Doctor.FEMALE]:
#             raise forms.ValidationError("Doctors can only be Male or Female.")
#         return gender
# def clean_phone_number(self):
#         phone_number = self.cleaned_data['phone_number']
#         try:
#             parsed_number = phonenumbers.parse(phone_number)
#             if not phonenumbers.is_valid_number(parsed_number):
#                 raise forms.ValidationError("Invalid phone number.")
#             return phonenumberutil.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
#         except phonenumbers.phonenumberutil.NumberParseException:
#             raise forms.ValidationError("Invalid phone number format.")