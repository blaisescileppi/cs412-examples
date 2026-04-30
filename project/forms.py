# File: project/forms.py
# Author: Blaise Scileppi (blaises@bu.edu), April 2026
# Description: ModelForms and regular Forms for the Medical Mystery Solver.
# Covers registration, profile editing, case CRUD, and search/filtering.

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import (
    DoctorProfile, PatientProfile, Case, CaseSymptom, Evidence, CaseCondition,
    PatientNote, PatientSymptomCheck, DoctorAvailabilitySlot, Appointment, Symptom,
)


class DoctorRegistrationForm(forms.ModelForm):
    """Profile fields collected when a new doctor registers."""

    class Meta:
        model = DoctorProfile
        fields = ["first_name", "last_name", "specialization", "license_number", "bio"]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 3, "placeholder": "Brief professional background (optional)"}),
            "license_number": forms.TextInput(attrs={"placeholder": "e.g. MA-123456"}),
        }


class PatientRegistrationForm(forms.ModelForm):
    """Profile fields collected when a new patient registers."""

    class Meta:
        model = PatientProfile
        fields = ["first_name", "last_name", "date_of_birth", "sex", "contact_email"]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
            "contact_email": forms.EmailInput(attrs={"placeholder": "Optional"}),
        }


class DoctorProfileForm(forms.ModelForm):
    """Used to update an existing doctor profile."""

    class Meta:
        model = DoctorProfile
        fields = ["first_name", "last_name", "specialization", "license_number", "bio"]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 3}),
        }


class PatientProfileForm(forms.ModelForm):
    """Used to update an existing patient profile."""

    class Meta:
        model = PatientProfile
        fields = ["first_name", "last_name", "date_of_birth", "sex", "contact_email"]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
        }


class CaseForm(forms.ModelForm):
    """
    Creates or updates a medical case. The doctor FK is set in the view,
    so it's excluded here. Patient link is optional.
    """

    class Meta:
        model = Case
        fields = [
            "title", "patient_alias", "age", "sex",
            "case_status", "chief_complaint", "date_started",
            "patient", "notes",
        ]
        widgets = {
            "date_started": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 4, "placeholder": "Additional clinical notes..."}),
            "chief_complaint": forms.TextInput(attrs={"placeholder": "Primary reason for visit"}),
            "patient_alias": forms.TextInput(attrs={"placeholder": "Anonymized identifier, e.g. Patient A"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["patient"].queryset = PatientProfile.objects.all().order_by("last_name")
        self.fields["patient"].required = False
        self.fields["patient"].label = "Linked patient account (optional)"
        self.fields["patient"].empty_label = "— unlinked —"


class EvidenceForm(forms.ModelForm):
    """Add or update a piece of clinical evidence for a case."""

    class Meta:
        model = Evidence
        fields = [
            "evidence_type", "description", "value_text",
            "date_recorded", "supports_condition", "contradicts_condition",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "date_recorded": forms.DateInput(attrs={"type": "date"}),
            "value_text": forms.TextInput(attrs={"placeholder": "e.g. TSH: 0.02 mIU/L"}),
            "supports_condition": forms.TextInput(attrs={"placeholder": "Condition name (optional)"}),
            "contradicts_condition": forms.TextInput(attrs={"placeholder": "Condition name (optional)"}),
        }


class CaseSymptomForm(forms.ModelForm):
    """Link a symptom to a case with severity, frequency, and timing."""

    class Meta:
        model = CaseSymptom
        fields = ["symptom", "severity", "frequency", "date_noticed", "is_active"]
        widgets = {
            "date_noticed": forms.DateInput(attrs={"type": "date"}),
            "severity": forms.NumberInput(attrs={"min": 1, "max": 10}),
        }

    def clean_severity(self):
        val = self.cleaned_data["severity"]
        if val < 1 or val > 10:
            raise forms.ValidationError("Severity must be between 1 and 10.")
        return val


class CaseConditionForm(forms.ModelForm):
    """Associate a condition with a case and set the initial confidence score."""

    class Meta:
        model = CaseCondition
        fields = ["condition", "confidence_score", "status", "reasoning_notes"]
        widgets = {
            "reasoning_notes": forms.Textarea(attrs={"rows": 3, "placeholder": "Why is this condition being considered?"}),
            "confidence_score": forms.NumberInput(attrs={"min": 0, "max": 100}),
        }

    def clean_confidence_score(self):
        val = self.cleaned_data["confidence_score"]
        if val < 0 or val > 100:
            raise forms.ValidationError("Confidence score must be between 0 and 100.")
        return val


class UpdateCaseConditionForm(forms.ModelForm):
    """Update the confidence score and status for an existing case condition."""

    class Meta:
        model = CaseCondition
        fields = ["confidence_score", "status", "reasoning_notes"]
        widgets = {
            "reasoning_notes": forms.Textarea(attrs={"rows": 3}),
            "confidence_score": forms.NumberInput(attrs={"min": 0, "max": 100}),
        }

    def clean_confidence_score(self):
        val = self.cleaned_data["confidence_score"]
        if val < 0 or val > 100:
            raise forms.ValidationError("Confidence score must be between 0 and 100.")
        return val


class CaseSearchForm(forms.Form):
    """Search and filter form for the doctor's case list."""

    PERIOD_CHOICES = [
        ("", "All time"),
        ("day", "Today"),
        ("week", "Past 7 days"),
        ("month", "Past 30 days"),
        ("year", "Past year"),
    ]

    STATUS_CHOICES = [("", "All statuses")] + Case.STATUS_CHOICES

    query = forms.CharField(
        required=False,
        label="Keyword",
        widget=forms.TextInput(attrs={"placeholder": "Search title, complaint, alias..."}),
    )
    status = forms.ChoiceField(required=False, choices=STATUS_CHOICES, label="Status")
    symptom = forms.CharField(
        required=False,
        label="Symptom contains",
        widget=forms.TextInput(attrs={"placeholder": "e.g. fatigue"}),
    )
    min_confidence = forms.IntegerField(
        required=False,
        min_value=0,
        max_value=100,
        label="Min condition confidence",
        widget=forms.NumberInput(attrs={"min": 0, "max": 100, "placeholder": "0–100"}),
    )
    period = forms.ChoiceField(required=False, choices=PERIOD_CHOICES, label="Date range")


# ── patient messaging & symptom check ─────────────────────────────────────────

class PatientNoteForm(forms.ModelForm):
    """
    Patient composes a note to a specific doctor. The doctor dropdown is
    filtered to only doctors the patient has had cases with, so they aren't
    sending messages to random doctors.
    """

    class Meta:
        model = PatientNote
        fields = ["doctor", "case", "body"]
        widgets = {
            "body": forms.Textarea(attrs={
                "rows": 5,
                "placeholder": "Write your message for the doctor here..."
            }),
        }
        labels = {
            "body": "Your message",
        }

    def __init__(self, patient, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show doctors the patient has had cases with
        doctor_ids = (
            Case.objects.filter(patient=patient)
            .values_list("doctor_id", flat=True)
            .distinct()
        )
        self.fields["doctor"].queryset = DoctorProfile.objects.filter(pk__in=doctor_ids)
        self.fields["doctor"].label = "Send to doctor"

        # Only show the patient's own cases
        self.fields["case"].queryset = Case.objects.filter(patient=patient)
        self.fields["case"].required = False
        self.fields["case"].empty_label = "— not linked to a specific case —"
        self.fields["case"].label = "Related case (optional)"


class PatientSymptomCheckForm(forms.Form):
    """
    A checkbox form where the patient selects all symptoms they're currently
    experiencing. Each checked symptom becomes a PatientSymptomCheck record.
    Common symptoms are shown first so the most relevant ones are at the top.
    """

    symptoms = forms.ModelMultipleChoiceField(
        queryset=Symptom.objects.all().order_by("-is_common", "name"),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Check every symptom you're currently experiencing",
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "rows": 3,
            "placeholder": "Any extra detail you want the doctor to know (optional)"
        }),
        label="Additional notes",
    )


# ── scheduling ────────────────────────────────────────────────────────────────

class DoctorAvailabilitySlotForm(forms.ModelForm):
    """
    Doctor creates a new 30-minute availability slot by choosing a date and
    start time. The form validates that the slot isn't in the past and doesn't
    overlap with an existing slot for the same doctor.
    """

    class Meta:
        model = DoctorAvailabilitySlot
        fields = ["date", "start_time"]
        widgets = {
            "date":       forms.DateInput(attrs={"type": "date"}),
            "start_time": forms.TimeInput(attrs={"type": "time"}),
        }
        help_texts = {
            "start_time": "Each slot is 30 minutes long.",
        }

    def __init__(self, doctor=None, *args, **kwargs):
        self.doctor = doctor
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        date = cleaned.get("date")
        start = cleaned.get("start_time")

        if date and start:
            from django.utils import timezone as tz
            import datetime

            # Slot must be in the future
            slot_dt = tz.make_aware(datetime.datetime.combine(date, start))
            if slot_dt <= tz.now():
                raise forms.ValidationError("Availability slots must be in the future.")

            # No overlapping slot for the same doctor
            if self.doctor and DoctorAvailabilitySlot.objects.filter(
                doctor=self.doctor, date=date, start_time=start
            ).exists():
                raise forms.ValidationError(
                    "You already have a slot at that date and time."
                )
        return cleaned


class AppointmentRequestForm(forms.ModelForm):
    """Patient fills in a reason when requesting an appointment slot."""

    class Meta:
        model = Appointment
        fields = ["reason"]
        widgets = {
            "reason": forms.Textarea(attrs={
                "rows": 3,
                "placeholder": "Briefly describe why you'd like this appointment..."
            }),
        }
