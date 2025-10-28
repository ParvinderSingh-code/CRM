from django.contrib import admin
from .models import *

class student(admin.ModelAdmin):
    list_display = ['name', 'street', 'street2', 'city', 'zip', 'state_id', 'nationality', 'country_id', 'passport_number', 'phone', 
                    'email', 'dob', 'gender', 'martial_status', 'profile', 'get_children']
    
    def get_children(self, obj):
        return ", ".join([child.name for child in obj.children.all()])
    get_children.short_description = "Child IDs"
    

class country(admin.ModelAdmin):
    list_display = ['name', 'country_code']


class state(admin.ModelAdmin):
    list_display = ['name', 'country_id']

class UniversityAdmin(admin.ModelAdmin):
    list_display = ['name', 'country_id']

class VisaTypeAdmin(admin.ModelAdmin):
    list_display = ['name']

class AcademicQualificationAdmin(admin.ModelAdmin):
    list_display = ['name']

class StudentStatusAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_completed']

class InterviewStatusAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_completed']

class PaymentStatusAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_completed']

class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['name']

class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date']

class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'symbol']

class UniversityApplicationAdmin(admin.ModelAdmin):
    list_display = ['name', 'student_id', 'passport_number', 'country_applied', 'university_id', 'course', 'course_type', 'intakes',
                    'intake_year', 'net_tuition', 'currency_id', 'student_status_id', 'payment_status_id', 'interview_status_id', 'agent_id',
                    'student', 'application', 'created_on']
    
class TravelAdmin(admin.ModelAdmin):
    list_display = ['date_from', 'country_id', 'date_to', 'visa_type', 'purpose', 'student_id']

class RefusalAdmin(admin.ModelAdmin):
    list_display = ['country_id', 'visa_type', 'date_refusal', 'reason', 'student_id']
    
class WorkExperienceAdmin(admin.ModelAdmin):
    list_display = ['company', 'date_from', 'date_to', 'period', 'designation', 'student_id']

class AcademicDetailsAdmin(admin.ModelAdmin):
    list_display = ['qualification', 'date_of_completion', 'university', 'percentage', 'student_id']

class UploadDocAdmin(admin.ModelAdmin):
    list_display = ['attach_file', 'student_id']

class PaymentAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'payment_date', 'contact_id', 'amount', 'currency_id', 'ref']

admin.site.register(ResStudent, student)
admin.site.register(ResCountry, country)
admin.site.register(ResState, state)
admin.site.register(University, UniversityAdmin)
admin.site.register(VisaType, VisaTypeAdmin)
admin.site.register(AcademicQualification, AcademicQualificationAdmin)
admin.site.register(StudentStatus, StudentStatusAdmin)
admin.site.register(InterviewStatus, InterviewStatusAdmin)
admin.site.register(PaymentStatus, PaymentStatusAdmin)
admin.site.register(PaymentMethod, PaymentMethodAdmin)
admin.site.register(AcademicYear, AcademicYearAdmin)
admin.site.register(Currency, CurrencyAdmin)
admin.site.register(UniversityApplication, UniversityApplicationAdmin)
admin.site.register(Travel, TravelAdmin)
admin.site.register(Refusal, RefusalAdmin)
admin.site.register(WorkExperience, WorkExperienceAdmin)
admin.site.register(AcademicDetails, AcademicDetailsAdmin)
admin.site.register(UploadDoc, UploadDocAdmin)
admin.site.register(Payment, PaymentAdmin)


