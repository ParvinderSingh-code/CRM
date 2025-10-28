from django.db import models
from django.contrib.auth.models import User


class ResCountry(models.Model):
    name = models.CharField(max_length=50)
    country_code = models.CharField(max_length=5)

    def __str__(self):
        return self.name


class ResState(models.Model):
    name = models.CharField(max_length=50)
    country_id = models.ForeignKey(ResCountry, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name
    

class University(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    country_id = models.ForeignKey(ResCountry, on_delete=models.RESTRICT, null=True, blank=True)

    def __str__(self):
        return self.name
    
class VisaType(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name
    

class AcademicQualification(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name
    

class StudentStatus(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    is_completed = models.BooleanField(null=True, blank=True)

    def __str__(self):
        return self.name
    
class InterviewStatus(models.Model):
    name = models.CharField(max_length=100,null=True, blank=True)
    is_completed = models.BooleanField(null=True, blank=True)

    def __str__(self):
        return self.name
    
class PaymentStatus(models.Model):
    name = models.CharField(max_length=100,null=True, blank=True)
    is_completed = models.BooleanField(null=True, blank=True)

    def __str__(self):
        return self.name
    
class PaymentMethod(models.Model):
    name = models.CharField(max_length=100,null=True, blank=True)

    def __str__(self):
        return self.name
    
class AcademicYear(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name
    
class Currency(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=3, unique=True) 
    symbol = models.CharField(max_length=5, blank=True)

    def __str__(self):
        return self.name

    
class ResStudent(models.Model):
    gender_CHOICES = [('male', 'Male'), ('female', 'Female'),('other', 'Other'),]
    martial_CHOICES = [('married', 'Married'), ('unmarried', 'Unmarried')]
    name = models.CharField(max_length=100, null=True, blank=True)
    street = models.CharField(max_length=99, null=True, blank=True)
    street2 = models.CharField(max_length=99,null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    zip = models.CharField(max_length=10,null=True, blank=True)
    state_id = models.ForeignKey(ResState, on_delete=models.RESTRICT, null=True, blank=True)
    country_id = models.ForeignKey(ResCountry, on_delete=models.RESTRICT, null=True, blank=True, related_name='country')
    nationality = models.ForeignKey(ResCountry, on_delete=models.RESTRICT, null=True, blank=True, related_name='nation')
    passport_number = models.CharField(max_length=10,null=True, blank=True)
    phone = models.CharField(max_length=15,null=True, blank=True)
    email = models.EmailField(max_length=50,null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(choices=gender_CHOICES, max_length=10,null=True, blank=True)
    martial_status = models.CharField(max_length=15, choices=martial_CHOICES,null=True, blank=True)
    profile = models.BinaryField(null=True, blank=True)
    parent = models.ForeignKey("self", on_delete=models.RESTRICT, null=True, blank=True,related_name="children")
    is_agent = models.BooleanField(null=True, blank=True)
    is_student = models.BooleanField(null=True, blank=True)
    is_applied = models.BooleanField(null=True, blank=True)

    def __str__(self):
        return self.name
    
class UniversityApplication(models.Model):
    type = [('ug', 'Under Graduate'), ('pg', 'Post Graduate')]
    month_type = [('jan','Jan'),('feb','Feburary'),('mar','March'),('apr','Apri;'),('may','May'),('jun','June'),('jul','July'),
             ('aug','August'),('sep','September'),('oct','October'),('nov','November'),('dec','December')]
    name = models.CharField(max_length=10,null=True, blank=True)
    student_id = models.ForeignKey(ResStudent, on_delete=models.RESTRICT, null=True, blank=True, related_name="student")
    passport_number = models.CharField(max_length=50,null=True, blank=True)
    country_applied = models.ForeignKey(ResCountry, on_delete=models.RESTRICT, null=True, blank=True,)
    university_id = models.ForeignKey(University, on_delete=models.RESTRICT, null=True, blank=True)
    course = models.CharField(max_length=100,null=True, blank=True)
    course_type = models.CharField(choices=type, max_length=100, null=True,blank=True)
    intakes = models.CharField(choices=month_type,max_length=100, null=True,blank=True)
    intake_year = models.CharField(max_length=4, null=True, blank=True)
    net_tuition = models.FloatField(null=True, blank=True)
    currency_id = models.ForeignKey(Currency, on_delete=models.RESTRICT, null=True, blank=True)
    student_status_id = models.ForeignKey(StudentStatus,on_delete=models.RESTRICT, null=True, blank=True)
    payment_status_id = models.ForeignKey(PaymentStatus,on_delete=models.RESTRICT, null=True, blank=True)
    interview_status_id = models.ForeignKey(InterviewStatus,on_delete=models.RESTRICT, null=True, blank=True)
    student = models.CharField(max_length=100,null=True, blank=True)
    application = models.CharField(max_length=100,null=True, blank=True)
    agent_id = models.ForeignKey(ResStudent, null=True, blank=True, on_delete=models.RESTRICT, related_name='agent')
    applied_to_id = models.ForeignKey(ResStudent, null=True, blank=True, on_delete=models.RESTRICT, related_name='applied')
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.name or f"Application #{self.id}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.name:
            self.name = f"AP#0{self.id}"
            super().save(update_fields=['name'])
    

class Travel(models.Model):
    country_id = models.ForeignKey(ResCountry, on_delete=models.RESTRICT, null=True, blank=True,)
    date_from = models.DateField(null=True, blank=True)
    date_to = models.DateField(null=True, blank=True)
    visa_type = models.ForeignKey(VisaType, on_delete=models.RESTRICT, null=True, blank=True)
    purpose = models.CharField(max_length=100, null=True, blank=True)
    student_id = models.ForeignKey(ResStudent, null=True, blank=True, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, null=True, blank=True,on_delete=models.DO_NOTHING)
    created_on = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=100, null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.name:
            self.name = f"Travel #{self.id}"
            super().save(update_fields=['name'])

    def __str__(self):
        return f"Travel #{self.id}"
    
class Refusal(models.Model):
    country_id = models.ForeignKey(ResCountry, on_delete=models.RESTRICT, null=True, blank=True,)
    visa_type = models.ForeignKey(VisaType, on_delete=models.RESTRICT, null=True, blank=True)
    date_refusal = models.DateField(null=True, blank=True)
    reason = models.CharField(max_length=100, null=True, blank=True)
    student_id = models.ForeignKey(ResStudent, null=True, blank=True, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, null=True, blank=True,on_delete=models.DO_NOTHING)
    created_on = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=100, null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.name:
            self.name = f"Refusal #{self.id}"
            super().save(update_fields=['name'])

    def __str__(self):
        return f"Refusal #{self.id}"

class WorkExperience(models.Model):
    company = models.CharField(max_length=100, null=True, blank=True)
    date_from = models.DateField(null=True, blank=True)
    date_to = models.DateField(null=True, blank=True)
    period = models.CharField(max_length=20, null=True, blank=True)
    designation = models.CharField(max_length=50, null=True, blank=True)
    student_id = models.ForeignKey(ResStudent, null=True, blank=True, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, null=True, blank=True,on_delete=models.DO_NOTHING)
    created_on = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=100, null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.name:
            self.name = f"Work Experience #{self.id}"
            super().save(update_fields=['name'])

    def __str__(self):
        return f"Work Experience #{self.id}"
    

class AcademicDetails(models.Model):
    qualification = models.ForeignKey(AcademicQualification, on_delete=models.RESTRICT, null=True, blank=True)
    date_of_completion = models.DateField(null=True, blank=True)
    university = models.CharField(max_length=50, null=True, blank=True)
    percentage = models.CharField(max_length=10, null=True, blank=True)
    student_id = models.ForeignKey(ResStudent, null=True, blank=True, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, null=True, blank=True,on_delete=models.DO_NOTHING)
    created_on = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=100, null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.name:
            self.name = f"Academic Details #{self.id}"
            super().save(update_fields=['name'])

    def __str__(self):
        return f"Academic Details #{self.id}"
    

class UploadDoc(models.Model):
    attachment = models.BinaryField(null=True, blank=True)
    attach_file = models.FileField(upload_to="doc/", max_length=500, null=True,blank=True)
    student_id = models.ForeignKey(ResStudent, null=True, blank=True, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, null=True, blank=True,on_delete=models.DO_NOTHING)
    created_on = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=100, null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.name:
            self.name = f"Attachment Doc #{self.id}"
            super().save(update_fields=['name'])

    def __str__(self):
        return f"Attachment Doc #{self.id}"
    

class Payment(models.Model):
    student_id = models.ForeignKey(ResStudent, null=True, blank=True, on_delete=models.CASCADE, related_name="linkage_student")
    created_by = models.ForeignKey(User, null=True, blank=True,on_delete=models.DO_NOTHING)
    created_on = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    payment_date = models.DateField(null=True, blank=True)
    contact_id = models.ForeignKey(ResStudent, null=True, blank=True, on_delete=models.CASCADE, related_name="contact")
    amount = models.FloatField(null=True, blank=True)
    currency_id = models.ForeignKey(Currency, null=True, blank=True, on_delete=models.RESTRICT)
    ref = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.name:
            self.name = f"Payment #{self.id}"
            super().save(update_fields=['name'])

    def __str__(self):
        return f"Payment #{self.id}"

