# File: project/admin.py
# Author: Blaise Scileppi (blaises@bu.edu), April 2026
# Description: Admin configuration for the Medical Mystery Solver project.
# Registers all models with custom list displays so that the admin tool
# shows useful column info instead of just the __str__ representation.

from django.contrib import admin
from .models import (
    DoctorProfile, PatientProfile,
    Condition, Symptom,
    Case, CaseSymptom, Evidence, CaseCondition,
    PatientNote, PatientSymptomCheck,
    DoctorAvailabilitySlot, Appointment,
)


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "specialization", "license_number")
    search_fields = ("last_name", "first_name", "specialization")


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "sex", "date_of_birth", "contact_email")
    search_fields = ("last_name", "first_name")


@admin.register(Condition)
class ConditionAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "red_flag_level", "common_age_group", "typical_duration")
    list_filter = ("category", "red_flag_level")
    search_fields = ("name",)


@admin.register(Symptom)
class SymptomAdmin(admin.ModelAdmin):
    list_display = ("name", "body_system", "is_common")
    list_filter = ("body_system", "is_common")
    search_fields = ("name",)


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ("title", "doctor", "patient_alias", "age", "sex", "case_status", "date_started")
    list_filter = ("case_status", "sex")
    search_fields = ("title", "patient_alias", "chief_complaint")
    date_hierarchy = "date_started"


@admin.register(CaseSymptom)
class CaseSymptomAdmin(admin.ModelAdmin):
    list_display = ("case", "symptom", "severity", "frequency", "date_noticed", "is_active")
    list_filter = ("frequency", "is_active")


@admin.register(Evidence)
class EvidenceAdmin(admin.ModelAdmin):
    list_display = ("case", "evidence_type", "date_recorded", "supports_condition", "contradicts_condition")
    list_filter = ("evidence_type",)


@admin.register(CaseCondition)
class CaseConditionAdmin(admin.ModelAdmin):
    list_display = ("case", "condition", "confidence_score", "status", "last_updated")
    list_filter = ("status",)


@admin.register(PatientNote)
class PatientNoteAdmin(admin.ModelAdmin):
    list_display = ("patient", "doctor", "case", "created_at", "is_read")
    list_filter = ("is_read",)
    search_fields = ("patient__last_name", "body")


@admin.register(PatientSymptomCheck)
class PatientSymptomCheckAdmin(admin.ModelAdmin):
    list_display = ("patient", "symptom", "date_reported")
    list_filter = ("date_reported",)


@admin.register(DoctorAvailabilitySlot)
class DoctorAvailabilitySlotAdmin(admin.ModelAdmin):
    list_display = ("doctor", "date", "start_time", "is_booked")
    list_filter = ("is_booked", "date")


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("patient", "slot", "status", "created_at")
    list_filter = ("status",)
