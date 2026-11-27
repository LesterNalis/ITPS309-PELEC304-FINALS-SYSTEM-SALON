from django.contrib import admin
from .models import (
    Appointment,
    Customer,
    Employee,
    Sale,
    Service,
    ServiceCategory,
    Product,
    Sale,
)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "phone", "created_at"]
    search_fields = ["name", "email", "phone"]


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ["name", "position", "email", "phone", "is_active"]
    list_filter = ["position", "is_active"]
    search_fields = ["name", "email", "phone"]


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    search_fields = ["name"]


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "price", "duration_minutes", "is_available"]
    list_filter = ["category", "is_available"]
    search_fields = ["name", "description"]


@admin.action(description="Confirm selected appointments")
def confirm_appointments(modeladmin, request, queryset):
    queryset.update(status="confirmed")


@admin.action(description="Cancel selected appointments")
def cancel_appointments(modeladmin, request, queryset):
    queryset.update(status="cancelled")


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = [
        "customer_name",
        "customer",
        "service",
        "stylist",
        "appointment_date",
        "appointment_time",
        "status",
    ]
    list_filter = ["status", "appointment_date", "stylist"]
    search_fields = ["customer_name", "contact_email", "service__name"]
    actions = [confirm_appointments, cancel_appointments]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "name", "category", "stock_quantity", "reorder_level", "needs_restock"
    ]
    list_filter = ["category", "is_active"]
    search_fields = ["name", "category"]


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = [
        "created_at", "customer", "service", "amount",
        "payment_method", "payment_status",
        
    ]
    list_filter = ["payment_method", "payment_status", "created_at"]
    search_fields = ["customer__name", "service__name"]
    
    