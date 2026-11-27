from datetime import datetime, time, timedelta

from django import forms
from django.utils import timezone

from .models import Appointment, Employee, Service


class AppointmentForm(forms.ModelForm):
    service = forms.ModelChoiceField(
        queryset=Service.objects.filter(is_available=True),
        empty_label="Choose a service",
    )
    stylist = forms.ModelChoiceField(
        queryset=Employee.objects.filter(is_active=True),
        empty_label="Choose a stylist",
    )

    class Meta:
        model = Appointment
        fields = [
            "customer_name",
            "contact_email",
            "service",
            "stylist",
            "appointment_date",
            "appointment_time",
            "notes",
        ]
        widgets = {
            "appointment_date": forms.DateInput(attrs={"type": "date"}),
            "appointment_time": forms.TimeInput(attrs={"type": "time"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def clean(self):
        cleaned = super().clean()
        date = cleaned.get("appointment_date")
        start = cleaned.get("appointment_time")
        service = cleaned.get("service")
        stylist = cleaned.get("stylist")

        if not date or not start or not service or not stylist:
            return cleaned

        now = timezone.localtime()

        if date < timezone.localdate():
            self.add_error("appointment_date", "Choose today or a future date.")
        elif date == timezone.localdate() and start <= now.time():
            self.add_error("appointment_time", "Choose a future time.")

        opening = time(9, 0)
        closing = time(19, 0)

        if start < opening or start >= closing:
            self.add_error(
                "appointment_time",
                "Choose a time between 9:00 AM and 7:00 PM.",
            )

        new_start = datetime.combine(date, start)
        new_end = new_start + timedelta(minutes=service.duration_minutes)

        if new_end.time() > closing:
            self.add_error(
                "appointment_time",
                "This service would finish after closing.",
            )

        existing = Appointment.objects.filter(
            appointment_date=date,
            stylist=stylist,
            status__in=["pending", "confirmed"],
        )

        if self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)

        for appointment in existing:
            existing_start = datetime.combine(
                appointment.appointment_date,
                appointment.appointment_time,
            )
            existing_end = existing_start + timedelta(
                minutes=appointment.service.duration_minutes
            )

            if new_start < existing_end and existing_start < new_end:
                self.add_error(
                    "appointment_time",
                    "That stylist is already booked then. Choose another time.",
                )
                break

        return cleaned