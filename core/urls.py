from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("book/", views.book_appointment, name="book_appointment"),
    path("booking-success/", views.booking_success, name="booking_success"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("reports/", views.sales_report, name="sales_report"),
    path("inventory/adjust/", views.adjust_stock, name="adjust_stock"),
]