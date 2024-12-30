# from django import forms
# from app.account.models import Appointment

# class ReportUploadForm(forms.ModelForm):
#     class Meta:
#         model = Appointment
#         fields = ['report']
#         widgets = {
#             'report': forms.FileInput(attrs={
#                 'class': 'form-control',
#                 'accept': '.pdf, .jpg, .jpeg, .png'
#             })
#         }
#         labels = {
#             'report': 'Upload Report (PDF/Image)'
#         }





















# # class PaymentForm(forms.ModelForm):
# #     class Meta:
# #         model = Payment
# #         fields = '__all__'

# #     def clean_amount(self):
# #         amount = self.cleaned_data['amount']
# #         if amount <= 0:
# #             raise forms.ValidationError("Amount must be greater than zero.") # Form-level validation
# #         return amount


