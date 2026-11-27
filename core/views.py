from django.shortcuts import render
from .models import ServiceCategory

from django.shortcuts import redirect
from .forms import AppointmentForm

from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone

from .models import Appointment, Customer, Employee, Service, Product, Sale

from django.db.models import F, Sum
from datetime import timedelta

from django.db.models import Count, Sum
from django.utils.dateparse import parse_date

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction
from django.shortcuts import redirect
from .forms_stock import StockAdjustmentForm
from .models import Product, StockAdjustment




@staff_member_required(login_url="/admin/login/")
def dashboard(request):
    today = timezone.localdate()

    upcoming = (
        Appointment.objects
        .filter(appointment_date__gte=today)
        .exclude(status="cancelled")
        .select_related("service", "stylist")
        .order_by("appointment_date", "appointment_time")[:6]
    )

    low_stock = Product.objects.filter(
        is_active=True,
        stock_quantity__lte=F("reorder_level"),
    )

    context = {
        "today": today,
        "today_count": Appointment.objects.filter(appointment_date=today).count(),
        "pending_count": Appointment.objects.filter(status="pending").count(),
        "customer_count": Customer.objects.count(),
        "employee_count": Employee.objects.filter(is_active=True).count(),
        "service_count": Service.objects.filter(is_available=True).count(),
        "upcoming": upcoming,
                "revenue": Sale.objects.filter(
            payment_status="paid"
        ).aggregate(total=Sum("amount"))["total"] or 0,
        "paid_sales_count": Sale.objects.filter(payment_status="paid").count(),
        "low_stock": low_stock[:5],
        "low_stock_count": low_stock.count(),
    }
    return render(request, "core/dashboard.html", context)

def home(request):
    categories = ServiceCategory.objects.prefetch_related("services").all()

    return render(request, "core/home.html", {
        "categories": categories,
    })


def book_appointment(request):
    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            email = appointment.contact_email.strip()

            customer = Customer.objects.filter(email__iexact=email).first()

            if customer is None:
                customer = Customer.objects.create(
                    name=appointment.customer_name,
                    email=email,
                )

            appointment.customer = customer
            appointment.save()



            return redirect("booking_success")
    else:
        form = AppointmentForm()

    return render(request, "core/book_appointment.html", {"form": form})


def booking_success(request):
    return render(request, "core/booking_success.html")


@staff_member_required(login_url="/admin/login/")
def sales_report(request):
    today = timezone.localdate()
    default_start = today - timedelta(days=29)

    start_date = parse_date(request.GET.get("from", "")) or default_start
    end_date = parse_date(request.GET.get("to", "")) or today

    if start_date > end_date:
        start_date, end_date = end_date, start_date

    sales = Sale.objects.filter(
        payment_status="paid",
        created_at__date__gte=start_date,
        created_at__date__lte=end_date,
    )

    total_revenue = sales.aggregate(total=Sum("amount"))["total"] or 0
    service_totals = (
        sales.values("service__name")
        .annotate(sale_count=Count("id"), revenue=Sum("amount"))
        .order_by("-revenue")
    )

    return render(request, "core/reports.html", {
        "start_date": start_date,
        "end_date": end_date,
        "sale_count": sales.count(),
        "total_revenue": total_revenue,
        "service_totals": service_totals,
    })

@staff_member_required(login_url="/admin/login/")
def adjust_stock(request):
    form = StockAdjustmentForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            product = Product.objects.select_for_update().get(
                pk=form.cleaned_data["product"].pk
            )
            change = form.cleaned_data["quantity_change"]

            if product.stock_quantity + change < 0:
                form.add_error("quantity_change", "Stock cannot go below zero.")
            else:
                adjustment = form.save(commit=False)
                adjustment.product = product
                adjustment.adjusted_by = request.user

                product.stock_quantity += change
                product.save(update_fields=["stock_quantity"])
                adjustment.save()

                messages.success(request, "Stock adjustment saved.")
                return redirect("adjust_stock")

    return render(request, "core/adjust_stock.html", {"form": form})