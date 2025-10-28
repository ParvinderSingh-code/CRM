from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = "contact"

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.user_profile, name='profile'),
    # Students
    path('students/', views.students, name='student'),
    path('students_create/', views.students_create, name='students_create'),
    path("check_passport/", views.check_passport, name="check_passport"),
    path("students/<int:pk>/", views.student_edit, name="student_edit"),
    path("delete_student/<int:pk>/", views.delete_student, name="delete_student"),
    # child Contact
    path('child_contact_create/', views.child_contact_create, name='child_contact_create'),
    path('contact_delete/<int:pk>/', views.contact_delete, name='contact_delete'),
    # Tracvels
    path('travelcreate/', views.travelcreate, name='travelcreate'),
    path('travel/update/<int:pk>/', views.travel_update, name='travel_update'),
    path('travel_delete/<int:pk>/', views.travel_delete, name="travel_delete"),
    # Refusal
    path('refusalcreate/', views.refusalcreate, name='refusalcreate'),
    path("refusal/update/<int:pk>/", views.refusal_update, name="refusal_update"),
    path('refusal_delete/<int:pk>/', views.refusal_delete, name='refusal_delete'),
    # work experience
    path('workexpcreate/', views.workexpcreate, name='workexpcreate'),
    path('workexp/update/<int:pk>/', views.workexp_update, name='workexp_update'),
    path('work_exp_delete/<int:pk>/', views.work_exp_delete, name='work_exp_delete'),
    # Academic Details
    path('academic_detail_create/', views.academic_detail_create, name='academic_detail_create'),
    path("academic_details/update/<int:pk>/", views.academic_details_update, name="academic_details_update"),
    path('academic_detail_delete/<int:pk>/', views.academic_detail_delete, name='academic_detail_delete'),

    path('upload_doc_create/', views.upload_doc_create, name='upload_doc_create'),
    path('upload_doc_delete/<int:pk>/', views.upload_doc_delete, name='upload_doc_delete'),
    # PAyments
    path('payment_create/', views.payment_create, name='payment_create'),
    path("payment/update/<int:pk>/", views.payment_update, name="payment_update"),
    path('payment_delete/<int:pk>/', views.payment_delete, name='payment_delete'),

    #State
    path('state/', views.state, name='state'),
    path('state_create/', views.state_create, name="state_create"),
    path('state_update/<int:pk>/', views.state_update, name='state_update'),
    path('state_delete/<int:pk>/', views.state_delete, name='state_delete'),

    #Country
    path('country/', views.country, name="country"),
    path('country_create/', views.country_create, name="country_create"),
    path('country_update/<int:pk>/', views.country_update, name='country_update'),
    path('country_delete/<int:pk>/', views.country_delete, name='country_delete'),

    #Currency
    path('currency/', views.currency, name="currency"),
    path('currency_create/', views.currency_create, name="currency_create"),
    path('currency_update/<int:pk>/', views.currency_update, name='currency_update'),
    path('currency_delete/<int:pk>/', views.currency_delete, name='currency_delete'),

    #University
    path('university/', views.university, name="university"),
    path('university_create/', views.university_create, name="university_create"),
    path('university_update/<int:pk>/', views.university_update, name="university_update"),
    path('university_delete/<int:pk>/', views.university_delete, name="university_delete"),

    #university Application
    #Visa Type
    path('visa/', views.visa, name="visa"),
    path('visa_create/', views.visa_create, name="visa_create"),
    path('visa_update/<int:pk>/', views.visa_update, name="visa_update"),
    path('visa_delete/<int:pk>/', views.visa_delete, name="visa_delete"),

    # AcademicQualification
    path('academic/', views.academic, name='academic'),
    path('academic_create/', views.academic_create, name="academic_create"),
    path('academic_update/<int:pk>/', views.academic_update, name="academic_update"),
    path('academic_delete/<int:pk>/', views.academic_delete, name="academic_delete"),

    #StudentStatus
    path('studenstatus/', views.studenstatus, name='studenstatus'),
    path('studentstatus_create/', views.studentstatus_create, name="studentstatus_create"),
    path('studentstatus_update/<int:pk>/', views.studentstatus_update, name="studentstatus_update"),
    path('studentstatus_delete/<int:pk>/', views.studentstatus_delete, name="studentstatus_delete"),

    #InterviewStatus
    path('interviewstatus/', views.interviewstatus, name='interviewstatus'),
    path('interviewstatus_create/', views.interviewstatus_create, name="interviewstatus_create"),
    path('interviewstatus_update/<int:pk>/', views.interviewstatus_update, name="interviewstatus_update"),
    path('interviewstatus_delete/<int:pk>/', views.interviewstatus_delete, name="interviewstatus_delete"),

    # PaymentStatus
    path('paymentstatus/', views.paymentstatus, name='paymentstatus'),
    path('paymentstatus_create/', views.paymentstatus_create, name="paymentstatus_create"),
    path('paymentstatus_update/<int:pk>/', views.paymentstatus_update, name="paymentstatus_update"),
    path('paymentstatus_delete/<int:pk>/', views.paymentstatus_delete, name="paymentstatus_delete"),

    # PaymentMethod
    path('paymentmethod/', views.paymentmethod, name='paymentmethod'),
    path('paymentmethod_create/', views.paymentmethod_create, name="paymentmethod_create"),
    path('paymentmethod_update/<int:pk>/', views.paymentmethod_update, name="paymentmethod_update"),
    path('paymentmethod_delete/<int:pk>/', views.paymentmethod_delete, name="paymentmethod_delete"),

    # AcademicYear
    path('academicyear/', views.academicyear, name='academicyear'),
    path('academicyear_create/', views.academicyear_create, name="academicyear_create"),
    path('academicyear_update/<int:pk>/', views.academicyear_update, name="academicyear_update"),
    path('academicyear_delete/<int:pk>/', views.academicyear_delete, name="academicyear_delete"),

    # Agents
    path('agent/', views.agent_details, name='agent'),
    path('agent_create/', views.agent_create, name='agent_create'),
    path('agent_update/<int:pk>/', views.agent_update, name='agent_update'),
    path('agent_delete/<int:pk>/', views.agent_delete, name='agent_delete'),

    # Applied
    path('applied/', views.applied_details, name='applied'),
    path('applied_create/', views.applied_create, name='applied_create'),
    path('applied_update/<int:pk>/', views.applied_update, name='applied_update'),
    path('applied_delete/<int:pk>/', views.applied_delete, name='applied_delete'),

    # University Application
    path('university-application/', views.university_application, name='university-application'),
    path('university-application-create/', views.university_application_create, name='university-application-create'),
    path('university-application-update/<int:pk>/', views.university_application_update, name='university-application-update'),
    path('university-application-delete/<int:pk>/', views.university_application_delete, name='university-application-delete'),

    path('child_contact_create/', views.child_contact_create, name='child_contact_create'),

]

if settings.DEBUG:
    urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)