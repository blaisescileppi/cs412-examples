from django.db import models
from django.utils import timezone

# Create your models here.
# The required data models for my application are designed to represent medical cases,
# symptoms, evidence, and possible diagnoses, along with the relationships between them.
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

#. example
class Condition(models.Model):
    name = models.CharField(max_length=100)
    CATEGORY_CHOICES = [
        ("Hormonal", "Hormonal"),
        ("Metabolic", "Metabolic"),
        ("Reproductive", "Reproductive"),
        ("Autoimmune", "Autoimmune"),
        ("Nutritional", "Nutritional"),
        ("Other", "Other"),
    ]

    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default="Other")
    description = models.TextField()
    common_age_group = models.CharField(max_length=100, blank=True)
    RED_FLAG_CHOICES = [
        ("Low", "Low"),
        ("Medium", "Medium"),
        ("High", "High"),
    ]
    red_flag_level = models.CharField(max_length=20, choices=RED_FLAG_CHOICES, default="Low")
    typical_duration = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name

class Symptom(models.Model):
    name = models.CharField(max_length=100)
    BODY_SYSTEM_CHOICES = [
        ("Reproductive", "Reproductive"),
        ("Endocrine", "Endocrine"),
        ("Digestive", "Digestive"),
        ("Neurological", "Neurological"),
        ("Skin", "Skin"),
        ("General", "General"),
        ("Other", "Other"),
    ]
    body_system = models.CharField(max_length=50, choices=BODY_SYSTEM_CHOICES, default="Other")
    description = models.TextField()
    is_common = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Case(models.Model):
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

    title = models.CharField(max_length=200)
    patient_alias = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    sex = models.CharField(max_length=30, choices=SEX_CHOICES)
    case_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Open")
    chief_complaint = models.CharField(max_length=255)
    date_started = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.title

class CaseSymptom(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="case_symptoms")
    symptom = models.ForeignKey(Symptom, on_delete=models.CASCADE, related_name="symptom_cases")
    FREQUENCY_CHOICES = [
        ("Daily", "Daily"),
        ("Weekly", "Weekly"),
        ("Occasional", "Occasional"),
    ]
    severity = models.PositiveIntegerField(help_text="Rate from 1 to 10") # find out how to restrict from 1-10
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default="Occasional")
    date_noticed = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.case.title} - {self.symptom.name}"

class Evidence(models.Model):
    EVIDENCE_TYPE_CHOICES = [
        ("Lab Result", "Lab Result"),
        ("Family History", "Family History"),
        ("Lifestyle Factor", "Lifestyle Factor"),
        ("Medication History", "Medication History"),
        ("Cycle History", "Cycle History"),
        ("Other", "Other"),
    ]

    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="evidence_items")
    evidence_type = models.CharField(max_length=30, choices=EVIDENCE_TYPE_CHOICES, default="Other")
    description = models.TextField()
    value_text = models.CharField(max_length=255, blank=True)
    date_recorded = models.DateField(default=timezone.now)
    supports_condition = models.CharField(max_length=100, blank=True)
    contradicts_condition = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.evidence_type} for {self.case.title}"

class CaseCondition(models.Model):
    STATUS_CHOICES = [
        ("Possible", "Possible"),
        ("Likely", "Likely"),
        ("Ruled Out", "Ruled Out"),
        ("Confirmed", "Confirmed"),
    ]

    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="possible_conditions")
    condition = models.ForeignKey(Condition, on_delete=models.CASCADE, related_name="condition_cases")
    confidence_score = models.PositiveIntegerField(help_text="Enter a value from 0 to 100") # restrict from 0-100
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Possible")
    reasoning_notes = models.TextField(blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.case.title} - {self.condition.name}"