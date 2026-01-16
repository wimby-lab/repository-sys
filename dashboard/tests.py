from django.contrib import admin
from django.test import Client, TestCase
from django.urls import reverse

class AdminBrandingTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_admin_site_header(self):
        self.assertEqual(admin.site.site_header, "COMSOC Administration")

    def test_admin_login_page_branding(self):
        response = self.client.get(reverse("admin:login"))
        self.assertContains(response, "COMSOC Administration")
