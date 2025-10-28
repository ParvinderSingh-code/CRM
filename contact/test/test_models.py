from django.test import TestCase
from django.contrib.auth.models import User
from contact.models import *
from datetime import date

class BaseSetupMixin(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="tester")
        self.country = ResCountry.objects.create(name="India", country_code="IN")
        self.state = ResState.objects.create(name="Punjab", country_id=self.country)
        self.currency = Currency.objects.create(name="Rupee", code="INR", symbol="₹")
        self.student = ResStudent.objects.create(
            name="John Doe",
            email="john@example.com",
            country_id=self.country,
            state_id=self.state,
            gender="male",
            is_student=True
        )
        print("first")

class TestResCountry(BaseSetupMixin):
    def test_country_str(self):
        self.assertEqual(str(self.country), "India")
        self.assertEqual(self.country.country_code, "IN")

class TestResState(BaseSetupMixin):
    def test_state_country_link(self):
        self.assertEqual(self.state.country_id.name, "India")

class TestResStudent(BaseSetupMixin):
    def test_student_creation(self):
        self.assertEqual(self.student.name, "John Doe")
        self.assertTrue(self.student.is_student)
        self.assertEqual(str(self.student), "John Doe")


class TestUniversityApplication(BaseSetupMixin):
    def setUp(self):
        super().setUp()
        self.university = University.objects.create(name="Delhi University", country_id=self.country)
        self.application = UniversityApplication.objects.create(
            student_id=self.student,
            passport_number="A1234567",
            country_applied=self.country,
            university_id=self.university,
            course="B.Tech",
            net_tuition=10000,
            currency_id=self.currency
        )

    def test_auto_name_generation(self):
        self.assertTrue(self.application.name.startswith("AP#0"))
        self.assertIn(str(self.application.id), self.application.name)


class TestPayment(BaseSetupMixin):
    def test_payment_auto_name(self):
        payment = Payment.objects.create(
            student_id=self.student,
            contact_id=self.student,
            created_by=self.user,
            amount=5000,
            currency_id=self.currency,
            payment_date=date.today()
        )
        self.assertTrue(payment.name.startswith("Payment #"))
        self.assertEqual(payment.amount, 5000)
