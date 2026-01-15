from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('inventory/', views.document_inventory, name='document_inventory'),
    path('activity/', views.activity_report, name='activity_report'),
    path('inventory/export/', views.export_inventory_csv, name='export_inventory_csv'),
    path('activity/export/', views.export_activity_csv, name='export_activity_csv'),
]
