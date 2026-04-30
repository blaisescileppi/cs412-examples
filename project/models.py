# File: project/models.py
# Author: Blaise Scileppi (blaises@bu.edu), April 2026
# Description: Data models for the Medical Mystery Solver project.
# Defines models for doctors, patients, medical cases, symptoms, evidence,
# diagnoses, patient messaging, symptom self-reporting, doctor availability
# slots, and appointment scheduling.

from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class DoctorProfile(models.Model):
    """Stores extra information for a user account that belongs to a doctor."""

    SPECIALIZATION_CHOICES = [
        ("General Practice", "General Practice"),
        ("Internal Medicine", "Internal Medicine"),
        ("Endocrinology", "Endocrinology"),
        ("Gynecology", "Gynecology"),
        ("Neurology", "Neurology"),
        ("Cardiology", "Cardiology"),
        ("Other", "Other"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="doctor_profile")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=50, choices=SPECIALIZATION_CHOICES, default="General Practice")
    license_number = models.CharField(max_length=50, blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"Dr. {self.last_name} ({self.specialization})"

    def get_absolute_url(self):
        return reverse("doctor_profile")

    def get_case_count(self):
        """Return total number of cases this doctor has created."""
        return self.cases.count()

    def get_unread_note_count(self):
        """Return how many patient notes addressed to this doctor haven't been read yet."""
        return PatientNote.objects.filter(doctor=self, is_read=False).count()

    def get_pending_appointment_count(self):
        """Return how many appointment requests are still in 'Requested' status."""
        return Appointment.objects.filter(
            slot__doctor=self, status="Requested"
        ).count()


class PatientProfile(models.Model):
    """Stores extra information for a user account that belongs to a patient."""

    SEX_CHOICES = [
        ("Female", "Female"),
        ("Male", "Male"),
        ("Prefer not to say", "Prefer not to say"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="patient_profile")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    sex = models.CharField(max_length=30, choices=SEX_CHOICES, default="Prefer not to say")
    contact_email = models.EmailField(blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_absolute_url(self):
        return reverse("patient_profile")

    def get_appointment_count(self):
        """Return how many cases are linked to this patient."""
        return self.cases.count()


class Condition(models.Model):
    """A medical condition that can be associated with a case as a possible diagnosis."""

    CATEGORY_CHOICES = [
        ("Hormonal", "Hormonal"),
        ("Metabolic", "Metabolic"),
        ("Reproductive", "Reproductive"),
        ("Autoimmune", "Autoimmune"),
        ("Nutritional", "Nutritional"),
        ("Infectious", "Infectious"),
        ("Other", "Other"),
    ]

    RED_FLAG_CHOICES = [
        ("Low", "Low"),
        ("Medium", "Medium"),
        ("High", "High"),
    ]

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default="Other")
    description = models.TextField()
    common_age_group = models.CharField(max_length=100, blank=True)
    red_flag_level = models.CharField(max_length=20, choices=RED_FLAG_CHOICES, default="Low")
    typical_duration = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("condition_detail", kwargs={"pk": self.pk})


class Symptom(models.Model):
    """A clinical symptom that can be logged on a case with severity and frequency."""

    BODY_SYSTEM_CHOICES = [
        ("Reproductive", "Reproductive"),
        ("Endocrine", "Endocrine"),
        ("Digestive", "Digestive"),
        ("Neurological", "Neurological"),
        ("Skin", "Skin"),
        ("Cardiovascular", "Cardiovascular"),
        ("General", "General"),
        ("Other", "Other"),
    ]

    name = models.CharField(max_length=100)
    body_system = models.CharField(max_length=50, choices=BODY_SYSTEM_CHOICES, default="Other")
    description = models.TextField()
    is_common = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("symptom_detail", kwargs={"pk": self.pk})


class Case(models.Model):
    """
    A medical case managed by a doctor. Optionally linked to a registered
    patient profile. Tracks chief complaint, basic demographics, and status.
    """

    STATUS_CHOICES = [
        ("Open", "Open"),
        ("Investigating", "Investigating"),
        ("Resolved", "Resolved"),
    ]

    SEX_CHOICES = [
        ("Female", "Female"),
        ("Male", "Male"),
        ("Prefer not to say", "Prefer not to say"),
    ]

    # A case must belong to a doctor; can optionally be linked to a patient.
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name="cases")
    patient = models.ForeignKey(
        PatientProfile, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="cases"
    )

    title = models.CharField(max_length=200)
    patient_alias = models.CharField(max_length=100, help_text="Anonymized name used for this case")
    age = models.PositiveIntegerField()
    sex = models.CharField(max_length=30, choices=SEX_CHOICES)
    case_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Open")
    chief_complaint = models.CharField(max_length=255)
    date_started = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("case_detail", kwargs={"pk": self.pk})

    def get_top_condition(self):
        """Return the CaseCondition with the highest confidence score, or None."""
        return self.possible_conditions.order_by("-confidence_score").first()


class CaseSymptom(models.Model):
    """
    Junction table linking a Symptom to a Case. Adds severity, frequency,
    when it was first noticed, and whether it's currently active.
    """

    FREQUENCY_CHOICES = [
        ("Daily", "Daily"),
        ("Weekly", "Weekly"),
        ("Occasional", "Occasional"),
    ]

    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="case_symptoms")
    symptom = models.ForeignKey(Symptom, on_delete=models.CASCADE, related_name="symptom_cases")
    severity = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Rate from 1 (very mild) to 10 (severe)"
    )
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default="Occasional")
    date_noticed = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.case.title} – {self.symptom.name}"


class Evidence(models.Model):
    """
    A piece of evidence or clinical finding for a case. Can indicate which
    conditions it supports or contradicts.
    """

    EVIDENCE_TYPE_CHOICES = [
        ("Lab Result", "Lab Result"),
        ("Family History", "Family History"),
        ("Lifestyle Factor", "Lifestyle Factor"),
        ("Medication History", "Medication History"),
        ("Cycle History", "Cycle History"),
        ("Physical Exam", "Physical Exam"),
        ("Other", "Other"),
    ]

    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="evidence_items")
    evidence_type = models.CharField(max_length=30, choices=EVIDENCE_TYPE_CHOICES, default="Other")
    description = models.TextField()
    value_text = models.CharField(max_length=255, blank=True, help_text="e.g. lab value or measurement")
    date_recorded = models.DateField(default=timezone.now)
    supports_condition = models.CharField(max_length=100, blank=True)
    contradicts_condition = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.evidence_type} – {self.case.title}"


class CaseCondition(models.Model):
    """
    Associates a Condition with a Case as a possible diagnosis. Tracks a
    confidence score (0–100) and status that can be updated as more evidence
    comes in.
    """

    STATUS_CHOICES = [
        ("Possible", "Possible"),
        ("Likely", "Likely"),
        ("Ruled Out", "Ruled Out"),
        ("Confirmed", "Confirmed"),
    ]

    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="possible_conditions")
    condition = models.ForeignKey(Condition, on_delete=models.CASCADE, related_name="condition_cases")
    confidence_score = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Enter a value from 0 to 100"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Possible")
    reasoning_notes = models.TextField(blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.case.title} – {self.condition.name} ({self.confidence_score}%)"


# ── patient messaging & self-reporting ────────────────────────────────────────

class PatientNote(models.Model):
    """
    A message sent by a patient to a specific doctor. Optionally linked to
    one of the patient's cases. The doctor sees an unread badge in the nav
    until they view and mark the note as read.
    """

    patient = models.ForeignKey(
        PatientProfile, on_delete=models.CASCADE, related_name="notes"
    )
    doctor = models.ForeignKey(
        DoctorProfile, on_delete=models.CASCADE, related_name="patient_notes"
    )
    case = models.ForeignKey(
        Case, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="patient_notes"
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Note from {self.patient} to Dr. {self.doctor.last_name} ({self.created_at.date()})"


class PatientSymptomCheck(models.Model):
    """
    A self-reported symptom from a patient. When a patient submits the
    symptom check-off form, one record is created per checked symptom.
    The doctor can see these grouped by patient and date.
    """

    patient = models.ForeignKey(
        PatientProfile, on_delete=models.CASCADE, related_name="symptom_checks"
    )
    symptom = models.ForeignKey(
        Symptom, on_delete=models.CASCADE, related_name="patient_checks"
    )
    date_reported = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True, help_text="Any additional detail about this symptom")

    def __str__(self):
        return f"{self.patient} – {self.symptom.name} on {self.date_reported}"


# ── scheduling ────────────────────────────────────────────────────────────────

class DoctorAvailabilitySlot(models.Model):
    """
    A 30-minute time block that a doctor has marked as available for appointments.
    is_booked flips to True when a patient's appointment request is confirmed.
    """

    doctor = models.ForeignKey(
        DoctorProfile, on_delete=models.CASCADE, related_name="availability_slots"
    )
    date = models.DateField()
    start_time = models.TimeField()
    is_booked = models.BooleanField(default=False)

    class Meta:
        ordering = ["date", "start_time"]
        unique_together = [["doctor", "date", "start_time"]]

    def __str__(self):
        return f"Dr. {self.doctor.last_name} – {self.date} {self.start_time}"

    @property
    def end_time(self):
        """End time is always 30 minutes after start_time."""
        from datetime import datetime, timedelta
        dt = datetime.combine(self.date, self.start_time) + timedelta(minutes=30)
        return dt.time()


class Appointment(models.Model):
    """
    Tracks a patient's request to book one of the doctor's availability slots.
    Status starts as Requested, then the doctor moves it to Confirmed or Cancelled.
    Confirming an appointment marks the linked slot as booked.
    """

    STATUS_CHOICES = [
        ("Requested", "Requested"),
        ("Confirmed", "Confirmed"),
        ("Cancelled", "Cancelled"),
    ]

    patient = models.ForeignKey(
        PatientProfile, on_delete=models.CASCADE, related_name="appointments"
    )
    slot = models.OneToOneField(
        DoctorAvailabilitySlot, on_delete=models.CASCADE, related_name="appointment"
    )
    reason = models.TextField(blank=True, help_text="Briefly describe the reason for the appointment")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Requested")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient} w/ Dr. {self.slot.doctor.last_name} on {self.slot.date} – {self.status}"
