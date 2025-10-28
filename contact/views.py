from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.contrib import messages
from datetime import datetime
from django.http import JsonResponse
from django.db.models import RestrictedError, ProtectedError, Count
from django.urls import reverse,NoReverseMatch
from django.db import IntegrityError, transaction
from django.core.exceptions import ObjectDoesNotExist
import calendar
from django.contrib.auth.decorators import login_required

def check_passport(request):
    passport = request.GET.get("passport", "").strip()
    if not passport:
        return JsonResponse({"exists": False, "skip": True})
    exists = ResStudent.objects.filter(passport_number=passport).exists()
    return JsonResponse({"exists": exists})

def students(request):
    student_qs = ResStudent.objects.filter(is_student=True,parent=None)
    state_id = ResState.objects.all()
    headers = ['Name', 'Passport','State', 'Nationality', 'Email']
    rows = []
    for row in student_qs:
        rows.append({
            'id': row.id,
            'edit_url': reverse('contact:student_edit', args=[row.id]),  
            'delete_url': reverse('contact:delete_student', args=[row.id]),
            'fields': [row.name, row.passport_number, row.state_id.name if row.state_id else "", row.nationality, row.email]
        })
    context = {'state': state_id, 'students':student_qs,'page_title': 'Student', 'student_header': headers,
               'students_rows': rows}
    return render(request, 'student_page.html', context)

def student_edit(request, pk):
    student = get_object_or_404(ResStudent, pk=pk)
    states = ResState.objects.all()
    countries = ResCountry.objects.all()
    all_students = ResStudent.objects.filter(is_student=True)
    children = student.children.all()
    academic_qualification = AcademicQualification.objects.all()
    travel = Travel.objects.filter(student_id=student)
    visa_type = VisaType.objects.all()
    refusals = Refusal.objects.filter(student_id=student)
    work_exp = WorkExperience.objects.filter(student_id=student)
    academic_details = AcademicDetails.objects.filter(student_id=student)
    upload_docs = UploadDoc.objects.filter(student_id=student)
    payments = Payment.objects.filter(student_id=student)
    currencies = Currency.objects.all()

    if request.method == "POST":
        student.name = request.POST.get("student_name", "").strip()
        student.street = request.POST.get("student_street", "").strip()
        student.street2 = request.POST.get("student_street2", "").strip()
        student.city = request.POST.get("student_city", "").strip()
        student.zip = request.POST.get("student_zip", "").strip()
        student.phone = request.POST.get("student_phone", "").strip()
        student.email = request.POST.get("student_email", "").strip()

        dob = request.POST.get("student_dob", "").strip()
        if dob:
            try:
                student.dob = datetime.strptime(dob, "%Y-%m-%d").date()
            except ValueError:
                messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
                return redirect("contact:student_edit", pk=student.pk)

        passport_number = request.POST.get("student_passport", "").strip()
        if passport_number:
            exists = ResStudent.objects.filter(passport_number=passport_number).exclude(pk=student.pk).exists()
            if exists:
                messages.error(request, "Passport number already exists for another student.")
                return redirect("contact:student_edit", pk=student.pk)
            student.passport_number = passport_number
        else:
            student.passport_number = None
        state = request.POST.get("student_state", '')
        if state:
            state_obj = ResState.objects.get(id=int(state))
            student.state_id = state_obj
            student.country_id = state_obj.country_id 
        nationality = request.POST.get("student_nationality")
        if nationality:
            student.nationality = ResCountry.objects.get(id=int(nationality))
        student.save()
        messages.info(request, f"Record '{student.name}' updated successfully.")
        return redirect("contact:student")

    context = {
        "student": student, "state": states, "countries": countries, "all_students": all_students,
        "children": children, "travel": travel, "refusals": refusals, "visa_type": visa_type,
        "work_experience": work_exp,"academic_details": academic_details,"upload_doc": upload_docs,"payments": payments,
        "currencies": currencies,"academic_qualification": academic_qualification,}
    return render(request, "student_create.html", context)

def students_create(request):
    state_id = ResState.objects.all()
    country_id = ResCountry.objects.all()
    all_students = ResStudent.objects.filter(is_student=True)

    if request.method == "POST":
        name = request.POST.get('student_name', '').strip()
        street = request.POST.get('student_street', '').strip()
        street2 = request.POST.get('student_street2', '').strip()
        city = request.POST.get('student_city', '').strip()
        zip_code = request.POST.get('student_zip', '').strip()
        state = request.POST.get('student_state', '')
        passport = request.POST.get('student_passport', '').strip()
        nationality = request.POST.get('student_nationality', '')
        phone = request.POST.get('student_phone', '').strip()
        email = request.POST.get('student_email', '').strip()
        dob = request.POST.get('student_dob', '')

        if not name:
            messages.error(request, "Student name is required.")
            return redirect('contact:students_create')
        states = None
        nation = None
        if state:
            states = get_object_or_404(ResState, id=int(state))
        if nationality:
            nation = get_object_or_404(ResCountry, id=int(nationality))

        dob_parsed = None
        if dob:
            try:
                dob_parsed = datetime.strptime(dob, "%Y-%m-%d").date()
            except ValueError:
                messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
                return redirect('contact:students_create')

        if passport and ResStudent.objects.filter(passport_number=passport).exists():
            messages.error(request, f"Passport Number {passport} already exists")
            return redirect('contact:students_create')

        ResStudent.objects.create(
            name=name, street=street, street2=street2, city=city, zip=zip_code, passport_number=passport,
            phone=phone, email=email, dob=dob_parsed, state_id=states, country_id=states.country_id if states else None,
            nationality=nation, is_student=True,)
        messages.success(request, "Record added successfully.")
        return redirect('contact:student')
    context = { 'state': state_id, 'countries': country_id,"all_students": all_students,}
    return render(request, 'student_create.html', context)

def delete_student(request, pk):
    student = get_object_or_404(ResStudent, pk=pk)
    if request.method == "POST":
        student.delete()
        messages.success(request, "Student deleted successfully!")
        return redirect("contact:student")
    return redirect("contact:student")

def child_contact_create(request):
    state_id = ResState.objects.all()
    country_id = ResCountry.objects.all()
    all_students = ResStudent.objects.filter(is_student=True)
    if request.method == "POST":
        parent_id = request.POST.get('parent_id')
        parent = None
        if parent_id:
            parent = get_object_or_404(ResStudent, id=int(parent_id))
        name = request.POST.get('student_name', '').strip()
        street = request.POST.get('student_street', '').strip()
        street2 = request.POST.get('student_street2', '').strip()
        city = request.POST.get('student_city', '').strip()
        zip_code = request.POST.get('student_zip', '').strip()
        state = request.POST.get('student_state', '')
        passport = request.POST.get('student_passport', '').strip()
        nationality = request.POST.get('student_nationality', '')
        phone = request.POST.get('student_phone', '').strip()
        email = request.POST.get('student_email', '').strip()
        dob = request.POST.get('student_dob', '').strip()
        if not name:
            messages.error(request, "Name is required.")
            if parent:
                return redirect("contact:student_edit", pk=parent.id)
            return redirect('contact:students_create')
        states = None
        nation = None
        if state:
            try:
                states = get_object_or_404(ResState, id=int(state))
            except (ValueError, TypeError):
                messages.error(request, "Invalid state selected.")
                return redirect("contact:student_edit", pk=parent.id)
        if nationality:
            try:
                nation = get_object_or_404(ResCountry, id=int(nationality))
            except (ValueError, TypeError):
                messages.error(request, "Invalid nationality selected.")
                return redirect("contact:student_edit", pk=parent.id)
        dob_parsed = None
        if dob:
            try:
                dob_parsed = datetime.strptime(dob, "%Y-%m-%d").date()
            except ValueError:
                messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
                return redirect("contact:student_edit", pk=parent.id)
        if passport and ResStudent.objects.filter(passport_number=passport).exists():
            messages.error(request, f"Passport Number {passport} already exists.")
            return redirect("contact:student_edit", pk=parent.id)
        ResStudent.objects.create(
            name=name, street=street, street2=street2, city=city, zip=zip_code, passport_number=passport, phone=phone,
            email=email, dob=dob_parsed, state_id=states, country_id=states.country_id if states else None,
            nationality=nation, is_student=True, parent=parent,)
        messages.success(request, "Record added successfully.")
        return redirect("contact:student_edit", pk=parent.id)
    context = {'state': state_id,'countries': country_id, "all_students": all_students, }
    return render(request, 'student_create.html', context)


def contact_delete(request, pk):
    student_dl = get_object_or_404(ResStudent, pk=pk)
    parent = student_dl.parent
    if request.method == "POST":
        student_dl.delete()
        messages.success(request, "Contact deleted successfully!")
        if parent:
            return redirect("contact:student_edit", pk=parent.pk)
        else:
            return redirect("contact:student")  
    return redirect("contact:student")

def travelcreate(request):
    if request.method == "POST":
        parent_id = request.POST.get('parent_id')
        date_from = request.POST.get('date_from', '').strip()
        date_to = request.POST.get('date_to', '').strip()
        country = request.POST.get('country_id', '')
        visa = request.POST.get('visa', '')
        purpose = request.POST.get('purpose', '').strip()
        if not parent_id:
            messages.error(request, "Parent ID is missing. Please refresh and try again.")
            return redirect('contact:student')
        try:
            parent = get_object_or_404(ResStudent, id=int(parent_id))
        except (ValueError, TypeError):
            messages.error(request, "Invalid parent ID.")
            return redirect('contact:student')
        country_obj = None
        visa_obj = None
        if country:
            try:
                country_obj = get_object_or_404(ResCountry, id=int(country))
            except (ValueError, TypeError):
                messages.error(request, "Invalid country selected.")
                return redirect("contact:student_edit", pk=parent.id)
        if visa:
            try:
                visa_obj = get_object_or_404(VisaType, id=int(visa))
            except (ValueError, TypeError):
                messages.error(request, "Invalid visa type selected.")
                return redirect("contact:student_edit", pk=parent.id)
        if not date_from or not date_to:
            messages.error(request, "Both From and To dates are required.")
            return redirect("contact:student_edit", pk=parent.id)
        try:
            date_from_parsed = datetime.strptime(date_from, "%Y-%m-%d").date()
            date_to_parsed = datetime.strptime(date_to, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
            return redirect("contact:student_edit", pk=parent.id)
        if date_to_parsed < date_from_parsed:
            messages.error(request, "End date cannot be before start date.")
            return redirect("contact:student_edit", pk=parent.id)
        Travel.objects.create(
            date_from=date_from_parsed, date_to=date_to_parsed, visa_type=visa_obj, country_id=country_obj, purpose=purpose,
            student_id=parent )
        messages.success(request, "Travel record created successfully!")
        return redirect("contact:student_edit", pk=parent.id)
    messages.error(request, "Invalid request method.")
    return redirect('contact:student')

def travel_update(request, pk):
    travel = get_object_or_404(Travel, pk=pk)

    if request.method == "POST":
        country_id = request.POST.get("country_id")
        visa_id = request.POST.get("visa_type")

        travel.country_id = get_object_or_404(ResCountry, pk=country_id)
        travel.visa_type = get_object_or_404(VisaType, pk=visa_id)
        travel.date_from = request.POST.get("date_from")
        travel.date_to = request.POST.get("date_to")
        travel.purpose = request.POST.get("purpose")

        travel.save()

        messages.success(request, "Travel record updated successfully!")
        return redirect("contact:student_edit", pk=travel.student_id.pk)
    return redirect("contact:student")

def travel_delete(request, pk):
    travel_dl = get_object_or_404(Travel, pk=pk)
    student = travel_dl.student_id
    if request.method == "POST":
        travel_dl.delete()
        messages.success(request, "Travel History deleted successfully!")
        if student:
            return redirect("contact:student_edit", pk=student.pk)
        else:
            return redirect("contact:student")  
    return redirect("contact:student")

def refusalcreate(request):
    if request.method == "POST":
        try:
            parent_id = request.POST.get('parent_id')
            if not parent_id:
                messages.error(request, "Missing student reference.")
                return redirect(request.META.get("HTTP_REFERER", "contact:student"))
            parent = get_object_or_404(ResStudent, id=int(parent_id))
            country_id = request.POST.get('country_id')
            visa_id = request.POST.get('visa')
            date_refusal = request.POST.get('date_of_completion')
            reason = request.POST.get('reason_refusal', "").strip()
            if not (country_id and visa_id and date_refusal):
                messages.error(request, "Please fill all required fields (Country, Visa Type, Date).")
                return redirect("contact:student_edit", pk=parent.id)
            try:
                country_obj = ResCountry.objects.get(id=int(country_id))
                visa_obj = VisaType.objects.get(id=int(visa_id))
            except ObjectDoesNotExist:
                messages.error(request, "Invalid country or visa type selected.")
                return redirect("contact:student_edit", pk=parent.id)
            with transaction.atomic():
                Refusal.objects.create(student_id=parent,country_id=country_obj,visa_type=visa_obj,date_refusal=date_refusal,reason=reason)
            messages.success(request, "Refusal record created successfully!")
            return redirect("contact:student_edit", pk=parent.id)

        except ValueError:
            messages.error(request, "Invalid data provided. Please check your inputs.")
            return redirect(request.META.get("HTTP_REFERER", "contact:student"))

        except IntegrityError:
            messages.error(request, "Database error occurred. Please try again.")
            return redirect("contact:student_edit", pk=parent.id)

        except Exception as e:
            messages.error(request, f"Unexpected error: {str(e)}")
            return redirect("contact:student_edit", pk=parent.id)
    messages.warning(request, "Invalid request method.")
    return redirect("contact:student")

def refusal_update(request, pk):
    refusal = get_object_or_404(Refusal, pk=pk)

    if request.method == "POST":
        country_id = request.POST.get("country_id")
        visa_id = request.POST.get("visa_type")  # may be "" if not selected
        date_refusal = request.POST.get("date_refusal")
        reason = request.POST.get("reason")

        if country_id:
            refusal.country_id = get_object_or_404(ResCountry, pk=country_id)

        # Only update visa_type if a valid ID is provided
        if visa_id:
            refusal.visa_type = VisaType.objects.filter(pk=visa_id).first()
        else:
            refusal.visa_type = None  # allow blank

        refusal.date_refusal = date_refusal
        refusal.reason = reason

        refusal.save()
        messages.success(request, "Refusal record updated successfully!")
        return redirect("contact:student_edit", pk=refusal.student_id.pk)

    return redirect("contact:student")

def refusal_update(request, pk):
    refusal = get_object_or_404(Refusal, pk=pk)

    if request.method == "POST":
        country_id = request.POST.get("country_id")
        visa_id = request.POST.get("visa_type")
        date_refusal = request.POST.get("date_refusal")
        reason = request.POST.get("reason")

        refusal.country_id = get_object_or_404(ResCountry, pk=country_id)
        refusal.visa_type = get_object_or_404(VisaType, pk=visa_id)
        refusal.date_refusal = date_refusal
        refusal.reason = reason

        refusal.save()

        messages.success(request, "Refusal record updated successfully!")
        return redirect("contact:student_edit", pk=refusal.student_id.id)
    return redirect("contact:student" )

def refusal_delete(request, pk):
    refusal_dl = get_object_or_404(Refusal, pk=pk)
    student = refusal_dl.student_id
    if request.method == "POST":
        refusal_dl.delete()
        messages.success(request, "Refusal deleted successfully!")
        if student:
            return redirect("contact:student_edit", pk=student.pk)
        else:
            return redirect("contact:student")  
    return redirect("contact:student")

def workexpcreate(request):
    if request.method == "POST":
        try:
            parent_id = request.POST.get('parent_id')
            if not parent_id:
                messages.error(request, "Missing student reference.")
                return redirect('contact:student')
            try:
                parent = get_object_or_404(ResStudent, id=int(parent_id))
            except (ValueError, TypeError):
                messages.error(request, "Invalid student selected.")
                return redirect('contact:student')
            company = request.POST.get('company', '').strip()
            designation = request.POST.get('designation', '').strip()
            date_from_str = request.POST.get('date_from', '').strip()
            date_to_str = request.POST.get('date_to', '').strip()
            if not company:
                messages.error(request, "Company name is required.")
                return redirect("contact:student_edit", pk=parent.id)
            if not date_from_str or not date_to_str:
                messages.error(request, "Both start and end dates are required.")
                return redirect("contact:student_edit", pk=parent.id)
            try:
                date_from = datetime.strptime(date_from_str, "%Y-%m-%d").date()
                date_to = datetime.strptime(date_to_str, "%Y-%m-%d").date()
            except ValueError:
                messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
                return redirect("contact:student_edit", pk=parent.id)
            if date_to < date_from:
                messages.error(request, "End date cannot be before start date.")
                return redirect("contact:student_edit", pk=parent.id)
            period_days = (date_to - date_from).days
            with transaction.atomic():
                WorkExperience.objects.create(
                    company=company,designation=designation,date_from=date_from,date_to=date_to,student_id=parent,period=period_days)
            messages.success(request, "Work Experience record created successfully!")
            return redirect("contact:student_edit", pk=parent.id)
        except Exception as e:
            messages.error(request, f"Unexpected error: {str(e)}")
            return redirect("contact:student_edit", pk=parent.id)
    messages.warning(request, "Invalid request method.")
    return redirect('contact:student')

def workexp_update(request, pk):
    workexp = get_object_or_404(WorkExperience, pk=pk)

    if request.method == "POST":
        workexp.company = request.POST.get("company")
        workexp.designation = request.POST.get("designation")

        date_from_str = request.POST.get("date_from")
        date_to_str = request.POST.get("date_to")

        if date_from_str:
            workexp.date_from = datetime.strptime(date_from_str, "%Y-%m-%d").date()
        if date_to_str:
            workexp.date_to = datetime.strptime(date_to_str, "%Y-%m-%d").date()

        if workexp.date_from and workexp.date_to:
            workexp.period = (workexp.date_to - workexp.date_from).days
        else:
            workexp.period = None

        workexp.save()
        messages.success(request, "Work experience updated successfully!")
        return redirect("contact:student_edit", pk=workexp.student_id.id)
    return redirect("contact:student")


def work_exp_delete(request, pk):
    workexp_dl = get_object_or_404(WorkExperience, pk=pk)
    student = workexp_dl.student_id
    if request.method == "POST":
        workexp_dl.delete()
        messages.success(request, "Work Experience deleted successfully!")
        if student:
            return redirect("contact:student_edit", pk=student.pk)
        else:
            return redirect("contact:student")  
    return redirect("contact:student")

def academic_detail_create(request):
    if request.method == 'POST':
        parent_id = request.POST.get('parent_id')
        qualification_id = request.POST.get('qualification')
        completion = request.POST.get('completion', '').strip()
        university_awarding = request.POST.get('university_awarding', '').strip()
        percentage_grade = request.POST.get('percentage_grade', '').strip()
        if not parent_id:
            messages.error(request, "Missing student reference.")
            return redirect('contact:student')
        try:
            parent = get_object_or_404(ResStudent, id=int(parent_id))
        except (ValueError, TypeError):
            messages.error(request, "Invalid student selected.")
            return redirect('contact:student')
        qualification = None
        if qualification_id:
            try:
                qualification = get_object_or_404(AcademicQualification, id=int(qualification_id))
            except (ValueError, TypeError):
                messages.error(request, "Invalid qualification selected.")
                return redirect("contact:student_edit", pk=parent.id)
        else:
            messages.error(request, "Qualification is required.")
            return redirect("contact:student_edit", pk=parent.id)

        # Optional: validate completion date
        # If you want to store as a proper date object:
        # try:
        #     completion_date = datetime.strptime(completion, "%Y-%m-%d").date() if completion else None
        # except ValueError:
        #     messages.error(request, "Invalid completion date format. Use YYYY-MM-DD.")
        #     return redirect("contact:student_edit", pk=parent.id)

        try:
            with transaction.atomic():
                AcademicDetails.objects.create(
                    student_id=parent,qualification=qualification,date_of_completion=completion,
                    university=university_awarding, percentage=percentage_grade,
                )
            messages.success(request, "Academic details created successfully!")
        except Exception as e:
            messages.error(request, f"Error creating academic details: {str(e)}")
        return redirect("contact:student_edit", pk=parent.id)
    messages.warning(request, "Invalid request method.")
    return redirect('contact:student')

def academic_details_update(request, pk):
    ad = get_object_or_404(AcademicDetails, pk=pk)
    if request.method == "POST":
        qualification_id = request.POST.get("qualification")
        if qualification_id:
            ad.qualification = get_object_or_404(AcademicQualification, pk=qualification_id)
        ad.university = request.POST.get("university")
        ad.percentage = request.POST.get("percentage")
        ad.date_of_completion = datetime.strptime(request.POST.get("date_of_completion"), "%Y-%m-%d").date()
        ad.save()

        messages.success(request, "Academic detail updated successfully!")
        return redirect("contact:student_edit", pk=ad.student_id.id)

def academic_detail_delete(request,pk):
    ad_dl = get_object_or_404(AcademicDetails, pk=pk)
    student = ad_dl.student_id
    if request.method == "POST":
        ad_dl.delete()
        messages.success(request, "AcademicDetails deleted successfully!")
        if student:
            return redirect("contact:student_edit", pk=student.pk)
        else:
            return redirect("contact:student")  
    return redirect("contact:student")

def upload_doc_create(request):
    if request.method == 'POST':
        parent_id = request.POST.get('parent_id')
        parent = None
        if parent_id:
            parent = get_object_or_404(ResStudent, id=int(parent_id))
        document = request.FILES.get('document')
        if document:
            UploadDoc.objects.create(attach_file=document,student_id=parent,created_by=request.user)
            messages.success(request, "UploadDoc created successfully!")
            return redirect("contact:student_edit", pk=parent.id)
    return render(request, 'student_create.html')

def upload_doc_delete(request, pk):
    upload_doc_qs = get_object_or_404(UploadDoc, pk=pk)
    student = upload_doc_qs.student_id
    if request.method == "POST":
        upload_doc_qs.delete()
        messages.success(request, "Docs deleted successfully!")
        if student:
            return redirect("contact:student_edit", pk=student.pk)
        else:
            return redirect("contact:student")  
    return redirect("contact:student")

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from datetime import datetime
from .models import ResStudent, Payment, Currency

def payment_create(request):
    if request.method == 'POST':
        parent_id = request.POST.get('parent_id')
        payment_date = request.POST.get('payment_date', '').strip()
        contact_id = request.POST.get('contact', '').strip()
        amount = request.POST.get('amount', '').strip()
        currency_id = request.POST.get('currency', '').strip()
        ref = request.POST.get('ref', '').strip()
        if not parent_id:
            messages.error(request, "Missing student reference.")
            return redirect('contact:student')
        try:
            parent = get_object_or_404(ResStudent, id=int(parent_id))
        except (ValueError, TypeError):
            messages.error(request, "Invalid student reference.")
            return redirect('contact:student')
        contact = None
        currency = None
        if contact_id:
            try:
                contact = get_object_or_404(ResStudent, id=int(contact_id))
            except (ValueError, TypeError):
                messages.error(request, "Invalid contact selected.")
                return redirect("contact:student_edit", pk=parent.id)
        if currency_id:
            try:
                currency = get_object_or_404(Currency, id=int(currency_id))
            except (ValueError, TypeError):
                messages.error(request, "Invalid currency selected.")
                return redirect("contact:student_edit", pk=parent.id)
        payment_date_parsed = None
        if payment_date:
            try:
                payment_date_parsed = datetime.strptime(payment_date, "%Y-%m-%d").date()
            except ValueError:
                messages.error(request, "Invalid payment date format. Use YYYY-MM-DD.")
                return redirect("contact:student_edit", pk=parent.id)
        try:
            amount_val = float(amount)
            if amount_val <= 0:
                messages.error(request, "Amount must be greater than zero.")
                return redirect("contact:student_edit", pk=parent.id)
        except (ValueError, TypeError):
            messages.error(request, "Invalid amount entered.")
            return redirect("contact:student_edit", pk=parent.id)
        try:
            with transaction.atomic():
                Payment.objects.create(
                    student_id=parent,payment_date=payment_date_parsed,contact_id=contact,amount=amount_val,currency_id=currency,ref=ref)
            messages.success(request, "Payment record created successfully!")
        except Exception as e:
            messages.error(request, f"Error creating payment record: {str(e)}")
        return redirect("contact:student_edit", pk=parent.id)
    messages.warning(request, "Invalid request method.")
    return redirect('contact:student')

def payment_update(request, pk):
    pay = get_object_or_404(Payment, pk=pk)
    if request.method == "POST":
        contact_id = request.POST.get("contact_id")
        currency_id = request.POST.get("currency_id")
        pay.contact_id = get_object_or_404(ResStudent, pk=contact_id)
        pay.amount = request.POST.get("amount")
        pay.currency_id = get_object_or_404(Currency, pk=currency_id)
        pay.ref = request.POST.get("ref")
        pay.payment_date = request.POST.get("payment_date")
        pay.save()

        messages.success(request, "Payment updated successfully!")
        return redirect("contact:student_edit", pk=pay.contact_id.id)


def payment_delete(request, pk):
    payment_dl = get_object_or_404(Payment, pk=pk)
    student = payment_dl.student_id
    if request.method == "POST":
        payment_dl.delete()
        messages.success(request, "AcademicDetails deleted successfully!")
        if student:
            return redirect("contact:student_edit", pk=student.pk)
        else:
            return redirect("contact:student")  
    return redirect("contact:student")

def state(request):
    state_qs = ResState.objects.all()
    country_qs = ResCountry.objects.all().prefetch_related("resstate_set") 
    context = {'state': state_qs, 'countries': country_qs, 'page_title': 'State',}
    return render(request, 'state_page.html',context)

def state_create(request):
    countries = ResCountry.objects.all()
    if request.method == "POST":
        name = request.POST.get('name')
        country_id = request.POST.get('country')
        if not name or not country_id:
            messages.error(request, "Please fill all details properly")
            return render(request, "state_page.html", {"countries": countries})
        try:
            country = get_object_or_404(ResCountry, id=int(country_id))
            ResState.objects.create(name=name, country_id=country)
            messages.success(request, "State Created Successfully")
            return redirect('contact:state')
        except ValueError:
            messages.error(request, "Invalid country ID.")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
    return render(request, "state_page.html", {"countries": countries})

def state_update(request, pk):
    state = get_object_or_404(ResState, pk=pk)
    countries = ResCountry.objects.all()
    if request.method == "POST":
        name = request.POST.get("name")
        country_id = request.POST.get("country")
        if not name or not country_id:
            messages.error(request, "Please fill all details properly")
            return render(request, "state_page.html", {"state": state,"countries": countries, })
        try:
            country = get_object_or_404(ResCountry, pk=int(country_id))
            state.name = name
            state.country_id = country
            state.save()
            messages.success(request, "State Details Updated Successfully")
            return redirect("contact:state")
        except ValueError:
            messages.error(request, "Invalid country ID.")
        except Exception as e:
            messages.error(request, f"Error updating state: {str(e)}")

    return render(request, "state_page.html", {"state": state,"countries": countries,})

def state_delete(request, pk):
    state = get_object_or_404(ResState, pk=pk)
    try:
        state.delete()
        messages.success(request, "State deleted successfully.")    
    except RestrictedError as e:
        messages.warning(request, f"Cannot delete state '{state.name}' because it is used in students.") 
    return redirect('contact:state')

def country(request):
    country_qs = ResCountry.objects.all()
    return render(request, 'country_page.html', {'countries': country_qs, 'page_title': 'Country',})

def country_create(request):
    if request.method == "POST":
        name = request.POST.get('country_name')
        country_code = request.POST.get('country_code')

        if not name or not country_code:
            messages.error(request, "Please fill all details properly.")
            return redirect('contact:country')

        if ResCountry.objects.filter(name__iexact=name).exists():
            messages.warning(request, f"The country '{name}' already exists.")
            return redirect('contact:country')

        if ResCountry.objects.filter(country_code__iexact=country_code).exists():
            messages.warning(request, f"The country code '{country_code}' is already in use.")
            return redirect('contact:country')
        ResCountry.objects.create(name=name.strip(), country_code=country_code.strip())
        messages.success(request, "Country created successfully!")
        return redirect('contact:country')
    return render(request, "country_page.html")

def country_update(request, pk):
    country = get_object_or_404(ResCountry, pk=pk)

    if request.method == "POST":
        name = request.POST.get("edit_country_name", "").strip()
        code = request.POST.get("edit_country_code", "").strip()

        if not name or not code:
            messages.error(request, "Please fill all details properly.")
            return redirect("contact:country")

        if ResCountry.objects.filter(name__iexact=name).exclude(pk=pk).exists():
            messages.warning(request, f"The country '{name}' already exists.")
            return redirect("contact:country")

        if ResCountry.objects.filter(country_code__iexact=code).exclude(pk=pk).exists():
            messages.warning(request, f"The country code '{code}' is already in use.")
            return redirect("contact:country")
        country.name = name
        country.country_code = code
        country.save()
        messages.success(request, "Country updated successfully!")
        return redirect("contact:country")
    return render(request, "country_page.html", {"country": country})


def country_delete(request, pk):
    countries = get_object_or_404(ResCountry, pk=pk)
    try:
        countries.delete()
        messages.success(request, "Country deleted successfully.")    
    except RestrictedError as e:
        messages.warning(request, f"Cannot delete Country '{countries.name.upper()}' because it is used in students.") 
    return redirect('contact:country')

def currency(request):
    currencies = Currency.objects.all()
    context = {'currencies': currencies,'page_title': 'Currency',}
    return render(request, 'currency_page.html', context)

def currency_create(request):
    if request.method == "POST":
        name = request.POST.get('currency_name', '').strip()
        code = request.POST.get('currency_code', '').strip()
        symbol = request.POST.get('currency_symbol', '').strip()

        if not name or not code or not symbol:
            messages.error(request, "Please fill all details properly.")
            return redirect('contact:currency')

        if Currency.objects.filter(code__iexact=code).exists():
            messages.warning(request, f"The currency code '{code}' is already in use.")
            return redirect('contact:currency')

        Currency.objects.create(name=name, code=code, symbol=symbol)
        messages.success(request, f"Currency '{name}' created successfully!")
        return redirect('contact:currency')
    return render(request, "currency_page.html")

def currency_update(request, pk):
    """Update an existing currency record."""
    currency = get_object_or_404(Currency, pk=pk)

    if request.method == "POST":
        name = request.POST.get("edit_currency_name", "").strip()
        code = request.POST.get("edit_currency_code", "").strip()
        symbol = request.POST.get("edit_currency_symbol", "").strip()

        if not name or not code or not symbol:
            messages.error(request, "Please fill all details properly.")
            return redirect('contact:currency')

        if Currency.objects.filter(code__iexact=code).exclude(pk=pk).exists():
            messages.warning(request, f"The currency code '{code}' is already used by another record.")
            return redirect('contact:currency')

        currency.name = name
        currency.code = code
        currency.symbol = symbol
        currency.save()
        messages.success(request, f"Currency '{name}' updated successfully!")
        return redirect("contact:currency")
    return render(request, "currency_page.html", {'currency': currency})

def currency_delete(request, pk):
    currency = get_object_or_404(Currency, pk=pk)
    try:
        currency.delete()
        messages.success(request, f"Currency '{currency.name}' deleted successfully.")
    except RestrictedError:
        messages.warning(request, f"Cannot delete Currency '{currency.name}' because it is in use.")
    except Exception as e:
        messages.error(request, f"An unexpected error occurred while deleting: {e}")
    return redirect('contact:currency')

def university(request):
    universities = University.objects.select_related("country_id").all()
    countries = ResCountry.objects.prefetch_related("resstate_set").all()
    context = { 'universities': universities, 'countries': countries, 'page_title': 'University',}
    return render(request, 'university.html', context)

def university_create(request):
    countries = ResCountry.objects.all()
    if request.method == "POST":
        name = request.POST.get('university_name', '').strip()
        country_id = request.POST.get('university_country', '').strip()

        if not name or not country_id:
            messages.error(request, "Please fill all details properly.")
            return redirect('contact:university')

        country = get_object_or_404(ResCountry, id=int(country_id))

        if University.objects.filter(name__iexact=name, country_id=country).exists():
            messages.warning(request, f"University '{name}' already exists in {country.name}.")
            return redirect('contact:university')

        University.objects.create(name=name, country_id=country)
        messages.success(request, f"University '{name}' created successfully!")
        return redirect('contact:university')
    return render(request, "university.html", {'countries': countries})

def university_update(request, pk):
    university_qs = get_object_or_404(University, pk=pk)

    if request.method == "POST":
        name = request.POST.get('edit_uni-name', '').strip()
        country_id = request.POST.get('edit_uni-country', '').strip()

        if not name or not country_id:
            messages.error(request, "Please fill all details properly.")
            return redirect('contact:university')

        country = get_object_or_404(ResCountry, pk=country_id)

        if University.objects.filter(name__iexact=name, country_id=country).exclude(pk=pk).exists():
            messages.warning(request, f"University '{name}' already exists in {country.name}.")
            return redirect('contact:university')

        university_qs.name = name
        university_qs.country_id = country
        university_qs.save()

        messages.success(request, f"University '{name}' updated successfully!")
        return redirect('contact:university')

    return render(request, "university.html", {'university': university_qs})

def university_delete(request, pk):
    university_dl = get_object_or_404(University, pk=pk)

    try:
        university_dl.delete()
        messages.success(request, f"University '{university_dl.name}' deleted successfully.")
    except RestrictedError:
        messages.warning(request, f"Cannot delete University '{university_dl.name}' because it is in use.")
    except Exception as e:
        messages.error(request, f"Unexpected error while deleting: {e}")

    return redirect('contact:university')
        
def visa(request):
    visa_qs = VisaType.objects.all().order_by('name')
    context = {'visa_type': visa_qs,'page_title': 'Visa Type'}
    return render(request, 'visa_page.html', context)

def visa_create(request):
    if request.method == "POST":
        name = request.POST.get('visa_name', '').strip()

        if not name:
            messages.error(request, "Please fill all details properly.")
            return redirect('contact:visa')

        if VisaType.objects.filter(name__iexact=name).exists():
            messages.warning(request, f"Visa Type '{name}' already exists.")
            return redirect('contact:visa')

        VisaType.objects.create(name=name)
        messages.success(request, f"Visa Type '{name}' created successfully!")
        return redirect('contact:visa')

    return render(request, "visa_page.html")

def visa_update(request, pk):
    visa_obj = get_object_or_404(VisaType, pk=pk)
    if request.method == "POST":
        name = request.POST.get('edit_visa_name', '').strip()

        if not name:
            messages.error(request, "Please provide a valid name.")
            return redirect('contact:visa')

        if VisaType.objects.filter(name__iexact=name).exclude(pk=pk).exists():
            messages.warning(request, f"Visa Type '{name}' already exists.")
            return redirect('contact:visa')

        visa_obj.name = name
        visa_obj.save()
        messages.success(request, f"Visa Type '{name}' updated successfully!")
        return redirect('contact:visa')

    return render(request, "visa_page.html", {'visa_obj': visa_obj})

def visa_delete(request, pk):
    visa_obj = get_object_or_404(VisaType, pk=pk)
    try:
        visa_obj.delete()
        messages.success(request, f"Visa Type '{visa_obj.name}' deleted successfully.")
    except RestrictedError:
        messages.warning(request, f"Cannot delete Visa Type '{visa_obj.name}' because it is in use.")
    except Exception as e:
        messages.error(request, f"Unexpected error while deleting: {e}")

    return redirect('contact:visa')

def academic(request):
    academic_qs = AcademicQualification.objects.all()
    return render(request, 'academic_page.html', {'academies': academic_qs, 'page_title': 'Academic Qualification'})

def academic_create(request):
    if request.method == "POST":
        name = request.POST.get('academic_name', '').strip()

        if not name:
            messages.error(request, "Please fill all details properly.")
            return redirect('contact:academic')

        AcademicQualification.objects.create(name=name)
        messages.success(request, "Academic Qualification created successfully.")
        return redirect('contact:academic')

    return render(request, "academic_page.html")

def academic_update(request, pk):
    academic_qs = get_object_or_404(AcademicQualification, pk=pk)

    if request.method == "POST":
        name = request.POST.get('edit_academic_name', '').strip()
        if not name:
            messages.error(request, "Name cannot be empty.")
            return redirect('contact:academic')

        academic_qs.name = name
        academic_qs.save()
        messages.success(request, "Academic Qualification updated successfully.")
        return redirect('contact:academic')

    return render(request, "academic_page.html", {'academic': academic_qs})

def academic_delete(request, pk):
    academic_qs = get_object_or_404(AcademicQualification, pk=pk)
    try:
        academic_qs.delete()
        messages.success(request, "Academic Qualification deleted successfully.")
    except RestrictedError:
        messages.warning(request,f"Cannot delete Academic Qualification '{academic_qs.name}' because it is in use.")

    return redirect('contact:academic')

def studenstatus(request):
    student_statuses = StudentStatus.objects.all().order_by('id')
    return render(request, 'studentstatus_page.html', {'student_status_name': student_statuses, 'page_title': 'Student Status'})

def studentstatus_create(request):
    if request.method == "POST":
        name = request.POST.get('student_status_name', '').strip()
        is_completed = request.POST.get('student_status_complete') == 'on'

        if not name:
            messages.error(request, "Please fill all details properly.")
            return redirect('contact:studenstatus')

        StudentStatus.objects.create(name=name, is_completed=is_completed)
        messages.success(request, "Student Status created successfully.")
        return redirect('contact:studenstatus')

    return render(request, "studentstatus_page.html")

def studentstatus_update(request, pk):
    ss_qs = get_object_or_404(StudentStatus, pk=pk)

    if request.method == "POST":
        name = request.POST.get('edit_ss_name', '').strip()
        is_completed = request.POST.get('edit_ss_status') == 'on'

        if not name:
            messages.error(request, "Name cannot be empty.")
            return redirect('contact:studenstatus')

        ss_qs.name = name
        ss_qs.is_completed = is_completed
        ss_qs.save()
        messages.success(request, "Student Status updated successfully.")
        return redirect('contact:studenstatus')

    return render(request, "studentstatus_page.html", {'student_status': ss_qs})

def studentstatus_delete(request, pk):
    ss_qs = get_object_or_404(StudentStatus, pk=pk)

    try:
        ss_qs.delete()
        messages.success(request, "Student Status deleted successfully.")
    except RestrictedError:
        messages.warning(request, f"Cannot delete Student Status '{ss_qs.name}' because it is in use.")

    return redirect('contact:studenstatus')

def interviewstatus(request):
    interview_statuses = InterviewStatus.objects.all().order_by('id')
    return render(request, 'interview_status_page.html', {'interview_status': interview_statuses, 'page_title': 'Interview Status'})

def interviewstatus_create(request):
    if request.method == "POST":
        name = request.POST.get('interview_status_name', '').strip()
        is_completed = request.POST.get('interview_status_complete') == 'on'

        if not name:
            messages.error(request, "Please fill all details properly.")
            return redirect('contact:interviewstatus')

        InterviewStatus.objects.create(name=name, is_completed=is_completed)
        messages.success(request, f"Interview Status '{name}' created successfully.")
        return redirect('contact:interviewstatus')

    return render(request, "interview_status_page.html")

def interviewstatus_update(request, pk):
    interview_status = get_object_or_404(InterviewStatus, pk=pk)

    if request.method == "POST":
        name = request.POST.get('edit_is_name', '').strip()
        is_completed = request.POST.get('edit_is_status') == 'on'

        if not name:
            messages.error(request, "Name cannot be empty.")
            return redirect('contact:interviewstatus')

        interview_status.name = name
        interview_status.is_completed = is_completed
        interview_status.save()
        messages.success(request, "Interview Status updated successfully.")
        return redirect('contact:interviewstatus')

    return render(request, "interview_status_page.html", {'interview_status': interview_status})

def interviewstatus_delete(request, pk):
    interview_status = get_object_or_404(InterviewStatus, pk=pk)
    try:
        interview_status.delete()
        messages.success(request, f"Interview Status '{interview_status.name}' deleted successfully.")
    except RestrictedError:
        messages.warning(request, f"Cannot delete Interview Status '{interview_status.name}' because it is in use.")
    return redirect('contact:interviewstatus')

def paymentstatus(request):
    payment_statuses = PaymentStatus.objects.all().order_by('id')
    return render(request, 'payment_status_page.html', {'payment_status': payment_statuses, 'page_title': 'Payment Status'})

def paymentstatus_create(request):
    if request.method == "POST":
        name = request.POST.get('payment_status_name', '').strip()
        is_completed = request.POST.get('payment_status_complete') == 'on'

        if not name:
            messages.error(request, "Please fill all details properly.")
            return redirect('contact:paymentstatus')

        PaymentStatus.objects.create(name=name, is_completed=is_completed)
        messages.success(request, f"Payment Status '{name}' created successfully.")
        return redirect('contact:paymentstatus')

    return render(request, "payment_status_page.html")

def paymentstatus_update(request, pk):
    payment_status = get_object_or_404(PaymentStatus, pk=pk)

    if request.method == "POST":
        name = request.POST.get('edit_ps_name', '').strip()
        is_completed = request.POST.get('edit_ps_status') == 'on'

        if not name:
            messages.error(request, "Name cannot be empty.")
            return redirect('contact:paymentstatus')

        payment_status.name = name
        payment_status.is_completed = is_completed
        payment_status.save()
        messages.success(request, "Payment Status updated successfully.")
        return redirect('contact:paymentstatus')

    return render(request, "payment_status_page.html", {'payment_status': payment_status})

def paymentstatus_delete(request, pk):
    payment_status = get_object_or_404(PaymentStatus, pk=pk)
    try:
        payment_status.delete()
        messages.success(request, f"Payment Status '{payment_status.name}' deleted successfully.")
    except RestrictedError:
        messages.warning(request, f"Cannot delete Payment Status '{payment_status.name}' because it is in use.")
    return redirect('contact:paymentstatus')

def paymentmethod(request):
    payment_methods = PaymentMethod.objects.all().order_by('id')
    return render(request, 'payment_method_page.html', {'payment_method': payment_methods, 'page_title': 'Payment Method'})

def paymentmethod_create(request):
    if request.method == "POST":
        name = request.POST.get('payment_method_name', '').strip()

        if not name:
            messages.error(request, "Please fill all details properly.")
            return redirect('contact:paymentmethod')

        PaymentMethod.objects.create(name=name)
        messages.success(request, f"Payment Method '{name}' created successfully.")
        return redirect('contact:paymentmethod')

    return render(request, "payment_method_page.html")

def paymentmethod_update(request, pk):
    payment_method = get_object_or_404(PaymentMethod, pk=pk)

    if request.method == "POST":
        name = request.POST.get('edit_pm_name', '').strip()

        if not name:
            messages.error(request, "Name cannot be empty.")
            return redirect('contact:paymentmethod')

        payment_method.name = name
        payment_method.save()
        messages.success(request, "Payment Method updated successfully.")
        return redirect('contact:paymentmethod')

    return render(request, "payment_method_page.html", {'payment_method': payment_method})

def paymentmethod_delete(request, pk):
    payment_method = get_object_or_404(PaymentMethod, pk=pk)

    try:
        payment_method.delete()
        messages.success(request, f"Payment Method '{payment_method.name}' deleted successfully.")
    except RestrictedError:
        messages.warning(request, f"Cannot delete Payment Method '{payment_method.name}' because it is in use.")

    return redirect('contact:paymentmethod')

def academicyear(request):
    academic_year_qs = AcademicYear.objects.all()
    headers = ['Name', 'Start date','End Date']
    rows = []
    for row in academic_year_qs:
        rows.append({
            'id': row.id,
            'edit_url': '#',  
            'delete_url': reverse('contact:academicyear_delete', args=[row.id]),
            'fields': [
                row.name,
                row.start_date,
                row.end_date,  
            ]
        })
    context = { "student_headers": headers,
                "student_rows": rows,
                'academic_year': academic_year_qs,
                'page_title': 'Academic Year'}
    return render(request, 'academic_year_page.html', context)

def academicyear_delete(request, pk):
    ay_qs = get_object_or_404(AcademicYear, pk=pk)
    if request.method == "POST":
        ay_qs.delete()
        messages.info(request, f"Academic Year {ay_qs.name} has been deleted")
        return redirect('contact:academicyear')


def academicyear_create(request):
    if request.method == "POST":
        name = request.POST.get('academic_year_name')
        start_date = request.POST.get('academic_year_start_date')
        end_date = request.POST.get('academic_year_end_date')
        if not name:
            messages.error(request, "Please fill all details properly")
        AcademicYear.objects.create(
            name = name,start_date=start_date,end_date=end_date
        )
        return redirect('contact:academicyear')
    return render(request, "academic_year_page.html")

def academicyear_update(request, pk):
    year = get_object_or_404(AcademicYear, pk=pk)

    if request.method == "POST":
        name = request.POST.get("edit_ay_name")
        start_date = request.POST.get("edit_ay_start_date")
        end_date = request.POST.get("edit_ay_end_date")

        if not name or not start_date or not end_date:
            messages.error(request, "All fields are required!")
            return redirect("contact:academicyear") 
        year.name = name
        year.start_date = start_date
        year.end_date = end_date
        year.save()

        messages.success(request, f"Academic Year '{year.name}' updated successfully!")
        return redirect("contact:academicyear")

    messages.warning(request, "Invalid request method.")
    return redirect("contact:academicyear")

def agent_details(request):
    agents = ResStudent.objects.filter(is_agent=True).order_by('id')
    headers = ['Name','State', 'Nationality', 'Email']
    rows = []
    for row in agents:
        rows.append({
            'id': row.id,
            'edit_url': reverse('contact:agent_update', args=[row.id]),  
            'delete_url': reverse('contact:agent_delete', args=[row.id]),
            'fields': [row.name, row.state_id.name if row.state_id else "", row.nationality, row.email]
        })
    context = {'agents': agents, 'agents_rows': rows, 'header': headers, 'page_title':'Agents'}
    return render(request, 'agent.html', context)

def agent_create(request):
    states_qs = ResState.objects.all()
    countries_qs = ResCountry.objects.all()

    if request.method == "POST":
        name = request.POST.get('student_name', '').strip()
        street = request.POST.get('student_street', '').strip()
        street2 = request.POST.get('student_street2', '').strip()
        city = request.POST.get('student_city', '').strip()
        zip_code = request.POST.get('student_zip', '').strip()
        state_id = request.POST.get('student_state')
        passport = request.POST.get('student_passport', '').strip()
        nationality_id = request.POST.get('student_nationality')
        phone = request.POST.get('student_phone', '').strip()
        email = request.POST.get('student_email', '').strip()
        dob_str = request.POST.get('student_dob', '').strip()

        if passport and ResStudent.objects.filter(passport_number=passport).exists():
            messages.error(request, f"Passport Number '{passport}' already exists.")
            return redirect('contact:agent_create')

        dob_parsed = None
        if dob_str:
            try:
                dob_parsed = datetime.strptime(dob_str, "%Y-%m-%d").date()
            except ValueError:
                messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
                return redirect('contact:agent_create')

        state_obj = get_object_or_404(ResState, id=int(state_id)) if state_id else None
        country_obj = get_object_or_404(ResCountry, id=int(nationality_id)) if nationality_id else None

        agent = ResStudent.objects.create(
            name=name,street=street, street2=street2, city=city, zip=zip_code, passport_number=passport,
            phone=phone,email=email,dob=dob_parsed,state_id=state_obj,nationality=country_obj,is_agent=True,)
        if state_obj:
            agent.country_id = state_obj.country_id
            agent.save()
        messages.success(request, f"Agent '{name}' created successfully!")
        return redirect('contact:agent')
    context = {'states': states_qs, 'countries': countries_qs,}
    return render(request, 'agent_create.html', context)

def agent_update(request, pk):
    agent = get_object_or_404(ResStudent, pk=pk)
    states_qs = ResState.objects.all()
    countries_qs = ResCountry.objects.all()

    if request.method == "POST":
        agent.name = request.POST.get("student_name", '').strip()
        agent.street = request.POST.get("student_street", '').strip()
        agent.street2 = request.POST.get("student_street2", '').strip()
        agent.city = request.POST.get("student_city", '').strip()
        agent.zip = request.POST.get("student_zip", '').strip()
        agent.phone = request.POST.get("student_phone", '').strip()
        agent.email = request.POST.get("student_email", '').strip()

        dob_str = request.POST.get("student_dob", '').strip()
        if dob_str:
            try:
                agent.dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
            except ValueError:
                messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
                return redirect("contact:agent_update", pk=agent.pk)

        passport_number = request.POST.get("student_passport", '').strip()
        if passport_number:
            exists = ResStudent.objects.filter(passport_number=passport_number).exclude(pk=agent.pk).exists()
            if exists:
                messages.error(request, "Passport number already exists for another agent.")
                return redirect("contact:agent_update", pk=agent.pk)
            agent.passport_number = passport_number

        state_id = request.POST.get("student_state")
        nationality_id = request.POST.get("student_nationality")
        if state_id:
            state_obj = get_object_or_404(ResState, id=int(state_id))
            agent.state_id = state_obj
            agent.country_id = state_obj.country_id
        if nationality_id:
            agent.nationality = get_object_or_404(ResCountry, id=int(nationality_id))

        agent.save()
        messages.success(request, f"Agent '{agent.name}' updated successfully!")
        return redirect("contact:agent")

    context = {"student": agent,"states": states_qs,"countries": countries_qs,}
    return render(request, "agent_create.html", context)

def agent_delete(request, pk):
    agent = get_object_or_404(ResStudent, pk=pk)
    try:
        agent.delete()
        messages.success(request, f"Agent '{agent.name}' deleted successfully.")
    except (ProtectedError, RestrictedError):
        messages.warning(request, f"Cannot delete Agent '{agent.name}' because it is in use.")
    return redirect('contact:agent')

def applied_details(request):
    applied_qs = ResStudent.objects.filter(is_applied=True).order_by('id')
    headers = ['Name','State', 'Nationality', 'Email']
    rows = []
    for row in applied_qs:
        rows.append({
            'id': row.id,
            'edit_url': reverse('contact:applied_update', args=[row.id]),  
            'delete_url': reverse('contact:applied_delete', args=[row.id]),
            'fields': [row.name, row.state_id.name if row.state_id else "", row.nationality, row.email]
        })
    context = {'applied': applied_qs, 'applied_rows': rows, 'header': headers, 'page_title': 'Applied Through'}
    return render(request, 'applied.html', context)

def applied_create(request):
    states_qs = ResState.objects.all()
    countries_qs = ResCountry.objects.all()

    if request.method == "POST":
        name = request.POST.get('student_name', '').strip()
        street = request.POST.get('student_street', '').strip()
        street2 = request.POST.get('student_street2', '').strip()
        city = request.POST.get('student_city', '').strip()
        zip_code = request.POST.get('student_zip', '').strip()
        state_id = request.POST.get('student_state')
        passport = request.POST.get('student_passport', '').strip()
        nationality_id = request.POST.get('student_nationality')
        phone = request.POST.get('student_phone', '').strip()
        email = request.POST.get('student_email', '').strip()
        dob_str = request.POST.get('student_dob', '').strip()

        if passport and ResStudent.objects.filter(passport_number=passport).exists():
            messages.error(request, f"Passport Number '{passport}' already exists.")
            return redirect('contact:applied_create')

        dob_parsed = None
        if dob_str:
            try:
                dob_parsed = datetime.strptime(dob_str, "%Y-%m-%d").date()
            except ValueError:
                messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
                return redirect('contact:applied_create')

        state_obj = get_object_or_404(ResState, id=int(state_id)) if state_id else None
        country_obj = get_object_or_404(ResCountry, id=int(nationality_id)) if nationality_id else None

        applied = ResStudent.objects.create(
            name=name,street=street, street2=street2, city=city, zip=zip_code, passport_number=passport,
            phone=phone,email=email,dob=dob_parsed,state_id=state_obj,nationality=country_obj,is_applied=True,)
        if state_obj:
            applied.country_id = state_obj.country_id
            applied.save()
        messages.success(request, f"Applied '{name}' created successfully!")
        return redirect('contact:applied')
    context = {'states': states_qs, 'countries': countries_qs,}
    return render(request, 'applied_create.html', context)

def applied_update(request, pk):
    applied = get_object_or_404(ResStudent, pk=pk)
    states_qs = ResState.objects.all()
    countries_qs = ResCountry.objects.all()

    if request.method == "POST":
        applied.name = request.POST.get("student_name", '').strip()
        applied.street = request.POST.get("student_street", '').strip()
        applied.street2 = request.POST.get("student_street2", '').strip()
        applied.city = request.POST.get("student_city", '').strip()
        applied.zip = request.POST.get("student_zip", '').strip()
        applied.phone = request.POST.get("student_phone", '').strip()
        applied.email = request.POST.get("student_email", '').strip()

        dob_str = request.POST.get("student_dob", '').strip()
        if dob_str:
            try:
                applied.dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
            except ValueError:
                messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
                return redirect("contact:applied_update", pk=applied.pk)

        passport_number = request.POST.get("student_passport", '').strip()
        if passport_number:
            exists = ResStudent.objects.filter(passport_number=passport_number).exclude(pk=applied.pk).exists()
            if exists:
                messages.error(request, "Passport number already exists for another Applied.")
                return redirect("contact:applied_update", pk=applied.pk)
            applied.passport_number = passport_number

        state_id = request.POST.get("student_state")
        nationality_id = request.POST.get("student_nationality")
        if state_id:
            state_obj = get_object_or_404(ResState, id=int(state_id))
            applied.state_id = state_obj
            applied.country_id = state_obj.country_id
        if nationality_id:
            applied.nationality = get_object_or_404(ResCountry, id=int(nationality_id))

        applied.save()
        messages.success(request, f"Applied '{applied.name}' updated successfully!")
        return redirect("contact:Applied")

    context = {"student": applied,"states": states_qs,"countries": countries_qs,}
    return render(request, "applied_create.html", context)

def applied_delete(request, pk):
    applied_qs = get_object_or_404(ResStudent, pk=pk)
    try:
        applied_qs.delete()
        messages.success(request, f"Applied '{applied_qs.name}' deleted successfully.")
    except (ProtectedError, RestrictedError):
        messages.warning(request, f"Cannot delete Applied '{applied_qs.name}' because it is in use.")
    return redirect('contact:applied')


def university_application(request):
    university_applications = UniversityApplication.objects.all().order_by('-id')
    headers = ['Name','Student', 'Agent', 'Country Applied', 'University', 'Student Status', ]
    rows = []
    for row in university_applications:
        rows.append({
            'id': row.id,
            'edit_url': reverse('contact:university-application-update', args=[row.id]),  
            'delete_url': reverse('contact:university-application-delete', args=[row.id]),
            'fields': [row.name, row.student_id.name if row.student_id else "", 
                       row.agent_id, row.country_applied, row.university_id.name, 
                       row.student_status_id if row.student_status_id else ""]
        })
    context = {'universities': university_applications,'page_title': 'University Applications', 'headers':headers, 'uni_app_row':rows}
    return render(request, 'university_app.html', context)

def university_application_create(request):
    countries = ResCountry.objects.all()
    student_statuses = StudentStatus.objects.all()
    payment_statuses = PaymentStatus.objects.all()
    interview_statuses = InterviewStatus.objects.all()
    universities = University.objects.all()
    currencies = Currency.objects.all()
    students = ResStudent.objects.filter(is_student=True)
    agents = ResStudent.objects.filter(is_agent=True)
    applied_id = ResStudent.objects.filter(is_applied=True)
    months = [
        ('jan', 'January'), ('feb', 'February'), ('mar', 'March'), ('apr', 'April'),
        ('may', 'May'), ('jun', 'June'), ('jul', 'July'), ('aug', 'August'),
        ('sep', 'September'), ('oct', 'October'), ('nov', 'November'), ('dec', 'December')
    ]

    if request.method == "POST":
        try:
            student = get_object_or_404(ResStudent, id=int(request.POST.get("student_name"))) if request.POST.get("student_name") else None
            student_status = get_object_or_404(StudentStatus, id=int(request.POST.get("student_status"))) if request.POST.get("student_status") else None
            country_applied = get_object_or_404(ResCountry, id=int(request.POST.get("country_applied"))) if request.POST.get("country_applied") else None
            payment_status = get_object_or_404(PaymentStatus, id=int(request.POST.get("payment_status"))) if request.POST.get("payment_status") else None
            interview_status = get_object_or_404(InterviewStatus, id=int(request.POST.get("interview_status"))) if request.POST.get("interview_status") else None
            university = get_object_or_404(University, id=int(request.POST.get("university"))) if request.POST.get("university") else None
            currency = get_object_or_404(Currency, id=int(request.POST.get("currency_id"))) if request.POST.get("currency_id") else None
            agent = get_object_or_404(ResStudent, id=int(request.POST.get('agents'))) if request.POST.get('agents') else None
            applied = get_object_or_404(ResStudent, id=int(request.POST.get('applied_id'))) if request.POST.get('applied_id') else None
            tution_fees = request.POST.get("tution_fees")
            net_tuition = float(tution_fees) if tution_fees not in (None, '') else None

            intake_year = request.POST.get("intake_year")
            intake_year = int(intake_year) if intake_year not in (None, '') else None

            UniversityApplication.objects.create(
                student_id=student, student_status_id=student_status, country_applied=country_applied,
                payment_status_id=payment_status, interview_status_id=interview_status,agent_id=agent,applied_to_id=applied,
                university_id=university, course=request.POST.get("course", ""), course_type=request.POST.get("course_type", ""),
                student=request.POST.get("student_id_char", ""), intakes=request.POST.get("intakes", ""),
                intake_year=intake_year, application=request.POST.get("application_id_char", ""),
                net_tuition=net_tuition, currency_id=currency,)

            messages.success(request, "University Application created successfully!")
            return redirect('contact:university-application')

        except ValueError as ve:
            messages.error(request, f"Invalid numeric input: {ve}")
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")

    context = {'agents': agents,'students': students,'student_status_id': student_statuses,
        'university_id': universities, 'payment_status_id': payment_statuses, 'interview_status_id': interview_statuses,
        'country_id': countries,'currencies': currencies, 'months': months, 'applied_id':applied_id}

    return render(request, 'uni_app_create.html', context)

def university_application_update(request, pk):
    university_app = get_object_or_404(UniversityApplication, pk=pk)
    countries = ResCountry.objects.all()
    student_statuses = StudentStatus.objects.all()
    payment_statuses = PaymentStatus.objects.all()
    interview_statuses = InterviewStatus.objects.all()
    universities = University.objects.all()
    currencies = Currency.objects.all()
    students = ResStudent.objects.filter(is_student=True)
    agents = ResStudent.objects.filter(is_agent=True)
    applied_id = ResStudent.objects.filter(is_applied=True)
    months = [
        ('jan', 'January'), ('feb', 'February'), ('mar', 'March'), ('apr', 'April'),
        ('may', 'May'), ('jun', 'June'), ('jul', 'July'), ('aug', 'August'),
        ('sep', 'September'), ('oct', 'October'), ('nov', 'November'), ('dec', 'December')
    ]

    if request.method == 'POST':
        try:
            student = get_object_or_404(ResStudent, id=int(request.POST.get("student_name"))) if request.POST.get("student_name") else None
            student_status = get_object_or_404(StudentStatus, id=int(request.POST.get("student_status"))) if request.POST.get("student_status") else None
            country_applied = get_object_or_404(ResCountry, id=int(request.POST.get("country_applied"))) if request.POST.get("country_applied") else None
            payment_status = get_object_or_404(PaymentStatus, id=int(request.POST.get("payment_status"))) if request.POST.get("payment_status") else None
            interview_status = get_object_or_404(InterviewStatus, id=int(request.POST.get("interview_status"))) if request.POST.get("interview_status") else None
            university = get_object_or_404(University, id=int(request.POST.get("university"))) if request.POST.get("university") else None
            currency = get_object_or_404(Currency, id=int(request.POST.get("currency_id"))) if request.POST.get("currency_id") else None
            agent = get_object_or_404(ResStudent, id=int(request.POST.get('agents'))) if request.POST.get('agents') else None
            applied_id = get_object_or_404(ResStudent, id=int(request.POST.get('applied_id'))) if request.POST.get('applied_id') else None
            tuition_fees = request.POST.get("tution_fees")
            tuition_fees = float(tuition_fees) if tuition_fees not in (None, '') else None

            intake_year = request.POST.get("intake_year")
            intake_year = int(intake_year) if intake_year not in (None, '') else None

            university_app.student_id = student
            university_app.student_status_id = student_status
            university_app.country_applied = country_applied
            university_app.payment_status_id = payment_status
            university_app.interview_status_id = interview_status
            university_app.university_id = university
            university_app.course = request.POST.get("course", "")
            university_app.course_type = request.POST.get("course_type", "")
            university_app.student = request.POST.get("student_id_char", "")
            university_app.intakes = request.POST.get("intakes", "")
            university_app.intake_year = intake_year
            university_app.application = request.POST.get("application_id_char", "")
            university_app.net_tuition = tuition_fees
            university_app.currency_id = currency
            university_app.agent_id = agent 
            university_app.applied_to_id = applied_id 
            university_app.save()
            messages.success(request, "University Application updated successfully!")
            return redirect('contact:university-application')

        except ValueError as ve:
            messages.error(request, f"Invalid numeric input: {ve}")
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")

    context = {
        'agents': agents, 'students': students, 'student_status_id': student_statuses,
        'university_id': universities, 'payment_status_id': payment_statuses, 'interview_status_id': interview_statuses,
        'country_id': countries, 'currencies': currencies, 'university_application': university_app, 'months': months, 'applied_id':applied_id}

    return render(request, 'uni_app_create.html', context)

def university_application_delete(request, pk):
    university_app = get_object_or_404(UniversityApplication, pk=pk)
    try:
        university_app.delete()
        messages.success(request, "University Application deleted successfully.")
    except ProtectedError:
        messages.warning(request, f"Cannot delete University Application '{university_app}' because it is in use.")
    except Exception as e:
        messages.error(request, f"An error occurred: {e}")
    return redirect('contact:university-application')

# def dashboard_view(request):
#     month = request.GET.get('month')
#     year = request.GET.get('year')
#     month_map = {v[:3].lower(): k for k, v in enumerate(calendar.month_name) if v}
#     if month:
#         month = str(month).lower()
#         month = month_map.get(month, month) 
#     applications = UniversityApplication.objects.all()
#     if month and year:
#         try:
#             applications = applications.filter(
#                 created_on__year=int(year),
#                 created_on__month=int(month)
#             )
#         except ValueError:
#             applications = UniversityApplication.objects.none()
    
#     university_data = (
#         applications.values('university_id', 'university_id__name')
#         .annotate(total_applications=Count('id'))
#         .order_by('-total_applications')
#     )

#     agent_data = (
#         applications.values('agent_id', 'agent_id__name')
#         .annotate(total_applications=Count('id'))
#         .order_by('-total_applications')
#     )
#     applied_data = (
#         applications.values('applied_to_id', 'applied_to_id__name')
#         .annotate(total_applications=Count('id'))
#         .order_by('-total_applications')
#     )
#     agent_count = ResStudent.objects.filter(is_agent=True).count()
#     uni_agent_count = agent_data.count()
#     uni_applied_count = applied_data.count()
#     applied_count = ResStudent.objects.filter(is_applied=True).count()
#     total_applications_count = applications.count()
#     uni_count = UniversityApplication.objects.all().count()
#     uni_university_count = university_data.count()
#     university_count = University.objects.all().count()

#     top_agent = agent_data.first()
#     top_university = university_data.first()
#     months = [(i, calendar.month_name[i]) for i in range(1, 13)]
#     context = {
#         'university_data': university_data, 'top_university': top_university,
#         'agent_data': agent_data,'top_agent': top_agent,
#         'month': month,'year': year,'months': months,
#         'total_applications_count': total_applications_count, 'uni_count': uni_count,
#         'agent_count':agent_count, 'uni_agent_count':uni_agent_count, 
#         'uni_university_count':uni_university_count, 'university_count':university_count,
#         'uni_applied_count':uni_applied_count, "applied_count":applied_count
#     }
#     return render(request, 'dashboard.html', context)
def dashboard_view(request):
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    applications = UniversityApplication.objects.all()

    # Filter by date range if provided
    if from_date and to_date:
        try:
            start_date = datetime.strptime(from_date, '%Y-%m-%d')
            end_date = datetime.strptime(to_date, '%Y-%m-%d')
            applications = applications.filter(created_on__date__range=(start_date, end_date))
        except ValueError:
            applications = UniversityApplication.objects.none()

    # Aggregate data
    university_data = (
        applications.values('university_id', 'university_id__name')
        .annotate(total_applications=Count('id'))
        .order_by('-total_applications')
    )

    agent_data = (
        applications.values('agent_id', 'agent_id__name')
        .annotate(total_applications=Count('id'))
        .order_by('-total_applications')
    )

    applied_data = (
        applications.values('applied_to_id', 'applied_to_id__name')
        .annotate(total_applications=Count('id'))
        .order_by('-total_applications')
    )

    agent_count = ResStudent.objects.filter(is_agent=True).count()
    uni_agent_count = agent_data.count()
    uni_applied_count = applied_data.count()
    applied_count = ResStudent.objects.filter(is_applied=True).count()
    total_applications_count = applications.count()
    uni_count = UniversityApplication.objects.all().count()
    uni_university_count = university_data.count()
    university_count = University.objects.all().count()

    top_agent = agent_data.first()
    top_university = university_data.first()

    context = {
        'university_data': university_data,
        'top_university': top_university,
        'agent_data': agent_data,
        'top_agent': top_agent,
        'from_date': from_date,
        'to_date': to_date,
        'total_applications_count': total_applications_count,
        'uni_count': uni_count,
        'agent_count': agent_count,
        'uni_agent_count': uni_agent_count,
        'uni_university_count': uni_university_count,
        'university_count': university_count,
        'uni_applied_count': uni_applied_count,
        'applied_count': applied_count,
    }

    return render(request, 'dashboard.html', context)

@login_required
def user_profile(request):
    user = request.user

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')

        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()
        # Optionally, add a success message
        from django.contrib import messages
        messages.success(request, "Profile updated successfully!")

    return render(request, 'profile.html', {'user': user})