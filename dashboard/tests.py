from django.contrib import admin
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import Role, User

class AdminBrandingTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_admin_site_header(self):
        self.assertEqual(admin.site.site_header, "COMSOC Administration")

    def test_admin_login_page_branding(self):
        response = self.client.get(reverse("admin:login"))
        self.assertContains(response, "COMSOC Administration")


class DashboardOfficerTests(TestCase):
    def setUp(self):
        self.role = Role.objects.create(name=Role.PRESIDENT)
        self.user = User.objects.create_user(
            username="president",
            password="testpass123",
            first_name="Alex",
            last_name="Santos",
            role=self.role,
        )

    def test_dashboard_shows_officers(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("dashboard:index"))
        current_date = timezone.localtime(timezone.now())
        school_year_start = current_date.year if current_date.month >= 6 else current_date.year - 1
        school_year_label = f"{school_year_start}-{school_year_start + 1}"

        self.assertContains(response, f"COMSOC Officers S.Y. {school_year_label}")
        self.assertContains(response, "President")
        self.assertContains(response, "Alex Santos")
