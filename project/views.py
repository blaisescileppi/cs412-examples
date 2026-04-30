# File: project/views.py
# Author: Blaise Scileppi (blaises@bu.edu), April 2026
# Description: All views for the Medical Mystery Solver project.
# Organized into: helpers, auth/landing, registration, doctor views,
# patient views, search, profile views, and reference data views.
# Uses a mix of class-based generic views and function-based views
# where the generic approach would be too rigid.

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
)
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.db.models import Q, Count
from datetime import timedelta

from .models import (
    DoctorProfile, PatientProfile,
    Case, CaseSymptom, Evidence, CaseCondition,
    Condition, Symptom,
    PatientNote, PatientSymptomCheck,
    DoctorAvailabilitySlot, Appointment,
)
from .forms import (
    DoctorRegistrationForm, PatientRegistrationForm,
    DoctorProfileForm, PatientProfileForm,
    CaseForm, EvidenceForm, CaseSymptomForm,
    CaseConditionForm, UpdateCaseConditionForm,
    CaseSearchForm,
    PatientNoteForm, PatientSymptomCheckForm,
    DoctorAvailabilitySlotForm, AppointmentRequestForm,
)


# ── access-control mixins ──────────────────────────────────────────────────────

class DoctorRequiredMixin:
    """
    Redirect unauthenticated users or non-doctors to the doctor login page.
    Views that inherit this can call self.get_doctor() to get the profile.
    """

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse("login_doctor") + f"?next={request.path}")
        if not DoctorProfile.objects.filter(user=request.user).exists():
            return redirect("login_doctor")
        return super().dispatch(request, *args, **kwargs)

    def get_doctor(self):
        """Return the DoctorProfile for the currently logged-in user."""
        return DoctorProfile.objects.get(user=self.request.user)


class PatientRequiredMixin:
    """
    Redirect unauthenticated users or non-patients to the patient login page.
    Views that inherit this can call self.get_patient() to get the profile.
    """

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse("login_patient") + f"?next={request.path}")
        if not PatientProfile.objects.filter(user=request.user).exists():
            return redirect("login_patient")
        return super().dispatch(request, *args, **kwargs)

    def get_patient(self):
        """Return the PatientProfile for the currently logged-in user."""
        return PatientProfile.objects.get(user=self.request.user)


# ── landing & auth ─────────────────────────────────────────────────────────────

def home(request):
    """
    Landing page shown to all visitors. Redirects to the correct dashboard
    if the user is already logged in.
    """
    if request.user.is_authenticated:
        if DoctorProfile.objects.filter(user=request.user).exists():
            return redirect("doctor_dashboard")
        if PatientProfile.objects.filter(user=request.user).exists():
            return redirect("patient_dashboard")
    return render(request, "project/home.html")


def login_doctor(request):
    """
    Doctor-only login page. After successful authentication, checks that the
    user actually has a DoctorProfile before granting access. Shows a specific
    error if they try to log in as a patient account.
    """
    error = None
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if DoctorProfile.objects.filter(user=user).exists():
                login(request, user)
                next_url = request.GET.get("next", reverse("doctor_dashboard"))
                return redirect(next_url)
            else:
                error = "This account isn't registered as a doctor. Try the patient login instead."
        else:
            error = "Incorrect username or password."
    else:
        form = AuthenticationForm()
    return render(request, "project/login_doctor.html", {"form": form, "error": error})


def login_patient(request):
    """
    Patient-only login page. Similar to login_doctor but checks for a
    PatientProfile and redirects to the patient dashboard.
    """
    error = None
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if PatientProfile.objects.filter(user=user).exists():
                login(request, user)
                next_url = request.GET.get("next", reverse("patient_dashboard"))
                return redirect(next_url)
            else:
                error = "This account isn't registered as a patient. Try the doctor login instead."
        else:
            error = "Incorrect username or password."
    else:
        form = AuthenticationForm()
    return render(request, "project/login_patient.html", {"form": form, "error": error})


def logout_view(request):
    """Log the user out and return them to the landing page."""
    logout(request)
    return redirect("home")


# ── registration ───────────────────────────────────────────────────────────────

class CreateDoctorView(CreateView):
    """
    Registration for new doctor accounts. Renders both Django's UserCreationForm
    and the DoctorRegistrationForm together, validates both, and creates the
    User + DoctorProfile in one step.
    """

    template_name = "project/register_doctor.html"
    form_class = DoctorRegistrationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass the user creation form to the template separately
        context["user_form"] = UserCreationForm(self.request.POST or None)
        return context

    def form_valid(self, form):
        user_form = UserCreationForm(self.request.POST)
        if not user_form.is_valid():
            # Re-render with both sets of errors visible
            return self.render_to_response(self.get_context_data(form=form))
        user = user_form.save()
        login(self.request, user)
        form.instance.user = user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("doctor_dashboard")


class CreatePatientView(CreateView):
    """
    Registration for new patient accounts. Same dual-form pattern as the
    doctor registration — creates both the User and PatientProfile together.
    """

    template_name = "project/register_patient.html"
    form_class = PatientRegistrationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_form"] = UserCreationForm(self.request.POST or None)
        return context

    def form_valid(self, form):
        user_form = UserCreationForm(self.request.POST)
        if not user_form.is_valid():
            return self.render_to_response(self.get_context_data(form=form))
        user = user_form.save()
        login(self.request, user)
        form.instance.user = user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("patient_dashboard")


# ── doctor dashboard ────────────────────────────────────────────────────────────

class DoctorDashboardView(DoctorRequiredMixin, TemplateView):
    """
    Main landing page after a doctor logs in. Shows a summary of their cases
    broken down by status, plus the five most recently opened cases.
    """

    template_name = "project/doctor_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        doctor = self.get_doctor()
        cases = doctor.cases.order_by("-date_started")

        context["doctor"] = doctor
        context["total_cases"] = cases.count()
        context["open_cases"] = cases.filter(case_status="Open").count()
        context["investigating_cases"] = cases.filter(case_status="Investigating").count()
        context["resolved_cases"] = cases.filter(case_status="Resolved").count()
        context["recent_cases"] = cases[:5]
        return context


# ── patient dashboard ───────────────────────────────────────────────────────────

class PatientDashboardView(PatientRequiredMixin, TemplateView):
    """
    Main landing page after a patient logs in. Shows total appointment count,
    a breakdown by doctor, and the five most recent cases.
    """

    template_name = "project/patient_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = self.get_patient()
        cases = patient.cases.order_by("-date_started")

        # Build a count of appointments per doctor so the patient can see
        # "You've had X appointments with Dr. Y"
        by_doctor = (
            cases
            .values("doctor__first_name", "doctor__last_name", "doctor__pk")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        context["patient"] = patient
        context["total_appointments"] = cases.count()
        context["recent_cases"] = cases[:5]
        context["by_doctor"] = by_doctor
        return context


# ── doctor case views ───────────────────────────────────────────────────────────

class DoctorCaseListView(DoctorRequiredMixin, ListView):
    """
    Paginated list of cases belonging to the logged-in doctor.
    Supports filtering by status and by time period (day / week / month / year).
    """

    model = Case
    template_name = "project/case_list_doctor.html"
    context_object_name = "cases"
    paginate_by = 20

    def get_queryset(self):
        doctor = self.get_doctor()
        qs = doctor.cases.order_by("-date_started")

        # Date-period filter
        period = self.request.GET.get("period", "")
        now = timezone.now().date()
        if period == "day":
            qs = qs.filter(date_started=now)
        elif period == "week":
            qs = qs.filter(date_started__gte=now - timedelta(days=7))
        elif period == "month":
            qs = qs.filter(date_started__gte=now - timedelta(days=30))
        elif period == "year":
            qs = qs.filter(date_started__gte=now - timedelta(days=365))

        # Status filter
        status = self.request.GET.get("status", "")
        if status:
            qs = qs.filter(case_status=status)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["doctor"] = self.get_doctor()
        context["period"] = self.request.GET.get("period", "")
        context["status_filter"] = self.request.GET.get("status", "")
        context["status_choices"] = Case.STATUS_CHOICES
        return context


class CaseDetailView(DoctorRequiredMixin, DetailView):
    """
    Full detail page for a single case, visible only to the doctor who owns it.
    Loads related symptoms, evidence, and conditions in one context.
    """

    model = Case
    template_name = "project/case_detail.html"
    context_object_name = "case"

    def get_queryset(self):
        # Only return cases that belong to this doctor
        return self.get_doctor().cases.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["doctor"] = self.get_doctor()
        context["symptoms"] = (
            self.object.case_symptoms
            .select_related("symptom")
            .order_by("-date_noticed")
        )
        context["evidence"] = self.object.evidence_items.order_by("-date_recorded")
        context["conditions"] = (
            self.object.possible_conditions
            .select_related("condition")
            .order_by("-confidence_score")
        )
        return context


class CreateCaseView(DoctorRequiredMixin, CreateView):
    """Form to open a new case. Automatically assigns the current doctor."""

    model = Case
    form_class = CaseForm
    template_name = "project/case_form.html"

    def form_valid(self, form):
        form.instance.doctor = self.get_doctor()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Open New"
        context["doctor"] = self.get_doctor()
        return context


class UpdateCaseView(DoctorRequiredMixin, UpdateView):
    """Edit an existing case. Scoped to the current doctor's cases."""

    model = Case
    form_class = CaseForm
    template_name = "project/case_form.html"

    def get_queryset(self):
        return self.get_doctor().cases.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Update"
        context["doctor"] = self.get_doctor()
        return context


class DeleteCaseView(DoctorRequiredMixin, DeleteView):
    """Confirmation page before permanently deleting a case."""

    model = Case
    template_name = "project/case_confirm_delete.html"
    success_url = reverse_lazy("doctor_case_list")

    def get_queryset(self):
        return self.get_doctor().cases.all()


# ── evidence views ──────────────────────────────────────────────────────────────

class AddEvidenceView(DoctorRequiredMixin, CreateView):
    """
    Add a piece of evidence to a specific case. The case is identified by
    case_pk in the URL, and ownership is verified before saving.
    """

    model = Evidence
    form_class = EvidenceForm
    template_name = "project/evidence_form.html"

    def get_case(self):
        return get_object_or_404(Case, pk=self.kwargs["case_pk"], doctor=self.get_doctor())

    def form_valid(self, form):
        form.instance.case = self.get_case()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["case"] = self.get_case()
        context["action"] = "Add"
        return context

    def get_success_url(self):
        return reverse("case_detail", kwargs={"pk": self.kwargs["case_pk"]})


class UpdateEvidenceView(DoctorRequiredMixin, UpdateView):
    """Edit an existing evidence entry. Verifies the doctor owns the parent case."""

    model = Evidence
    form_class = EvidenceForm
    template_name = "project/evidence_form.html"

    def get_queryset(self):
        return Evidence.objects.filter(case__doctor=self.get_doctor())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["case"] = self.object.case
        context["action"] = "Update"
        return context

    def get_success_url(self):
        return reverse("case_detail", kwargs={"pk": self.object.case.pk})


class DeleteEvidenceView(DoctorRequiredMixin, DeleteView):
    """Delete a piece of evidence. Returns to the parent case detail page."""

    model = Evidence
    template_name = "project/evidence_confirm_delete.html"

    def get_queryset(self):
        return Evidence.objects.filter(case__doctor=self.get_doctor())

    def get_success_url(self):
        return reverse("case_detail", kwargs={"pk": self.object.case.pk})


# ── case symptom views ──────────────────────────────────────────────────────────

class AddCaseSymptomView(DoctorRequiredMixin, CreateView):
    """Add a symptom to a case with severity and frequency information."""

    model = CaseSymptom
    form_class = CaseSymptomForm
    template_name = "project/case_symptom_form.html"

    def get_case(self):
        return get_object_or_404(Case, pk=self.kwargs["case_pk"], doctor=self.get_doctor())

    def form_valid(self, form):
        form.instance.case = self.get_case()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["case"] = self.get_case()
        return context

    def get_success_url(self):
        return reverse("case_detail", kwargs={"pk": self.kwargs["case_pk"]})


class DeleteCaseSymptomView(DoctorRequiredMixin, DeleteView):
    """Remove a symptom from a case."""

    model = CaseSymptom
    template_name = "project/casesymptom_confirm_delete.html"

    def get_queryset(self):
        return CaseSymptom.objects.filter(case__doctor=self.get_doctor())

    def get_success_url(self):
        return reverse("case_detail", kwargs={"pk": self.object.case.pk})


# ── case condition views ────────────────────────────────────────────────────────

class AddCaseConditionView(DoctorRequiredMixin, CreateView):
    """
    Associate a possible condition with a case. Sets the initial confidence
    score and status. The doctor can update these as new evidence comes in.
    """

    model = CaseCondition
    form_class = CaseConditionForm
    template_name = "project/case_condition_form.html"

    def get_case(self):
        return get_object_or_404(Case, pk=self.kwargs["case_pk"], doctor=self.get_doctor())

    def form_valid(self, form):
        form.instance.case = self.get_case()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["case"] = self.get_case()
        context["action"] = "Add"
        return context

    def get_success_url(self):
        return reverse("case_detail", kwargs={"pk": self.kwargs["case_pk"]})


class UpdateCaseConditionView(DoctorRequiredMixin, UpdateView):
    """
    Update the confidence score and status of a condition that's already
    associated with a case. This is the main way the doctor tracks how
    likely each diagnosis is as new evidence comes in.
    """

    model = CaseCondition
    form_class = UpdateCaseConditionForm
    template_name = "project/case_condition_form.html"

    def get_queryset(self):
        return CaseCondition.objects.filter(case__doctor=self.get_doctor())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["case"] = self.object.case
        context["action"] = "Update"
        context["condition_name"] = self.object.condition.name
        return context

    def get_success_url(self):
        return reverse("case_detail", kwargs={"pk": self.object.case.pk})


class DeleteCaseConditionView(DoctorRequiredMixin, DeleteView):
    """Remove a condition from a case's differential."""

    model = CaseCondition
    template_name = "project/casecondition_confirm_delete.html"

    def get_queryset(self):
        return CaseCondition.objects.filter(case__doctor=self.get_doctor())

    def get_success_url(self):
        return reverse("case_detail", kwargs={"pk": self.object.case.pk})


# ── search ──────────────────────────────────────────────────────────────────────

class SearchCasesView(DoctorRequiredMixin, ListView):
    """
    Lets a doctor search and filter their cases by keyword, status, symptom
    name, minimum condition confidence score, and date range. All filters
    can be combined.
    """

    model = Case
    template_name = "project/search_results.html"
    context_object_name = "cases"

    def get_queryset(self):
        doctor = self.get_doctor()
        qs = doctor.cases.order_by("-date_started")

        query = self.request.GET.get("query", "").strip()
        if query:
            qs = qs.filter(
                Q(title__icontains=query)
                | Q(chief_complaint__icontains=query)
                | Q(patient_alias__icontains=query)
                | Q(notes__icontains=query)
            )

        status = self.request.GET.get("status", "")
        if status:
            qs = qs.filter(case_status=status)

        symptom = self.request.GET.get("symptom", "").strip()
        if symptom:
            qs = qs.filter(case_symptoms__symptom__name__icontains=symptom).distinct()

        min_conf = self.request.GET.get("min_confidence", "").strip()
        if min_conf:
            try:
                qs = qs.filter(
                    possible_conditions__confidence_score__gte=int(min_conf)
                ).distinct()
            except ValueError:
                pass

        period = self.request.GET.get("period", "")
        now = timezone.now().date()
        if period == "day":
            qs = qs.filter(date_started=now)
        elif period == "week":
            qs = qs.filter(date_started__gte=now - timedelta(days=7))
        elif period == "month":
            qs = qs.filter(date_started__gte=now - timedelta(days=30))
        elif period == "year":
            qs = qs.filter(date_started__gte=now - timedelta(days=365))

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["doctor"] = self.get_doctor()
        context["form"] = CaseSearchForm(self.request.GET or None)
        context["query"] = self.request.GET.get("query", "")
        context["result_count"] = self.get_queryset().count()
        return context


# ── doctor profile views ────────────────────────────────────────────────────────

class DoctorProfileView(DoctorRequiredMixin, TemplateView):
    """Shows the logged-in doctor their own profile information."""

    template_name = "project/doctor_profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["doctor"] = self.get_doctor()
        return context


class UpdateDoctorProfileView(DoctorRequiredMixin, UpdateView):
    """Edit the logged-in doctor's profile."""

    model = DoctorProfile
    form_class = DoctorProfileForm
    template_name = "project/doctor_profile_form.html"

    def get_object(self):
        return self.get_doctor()

    def get_success_url(self):
        return reverse("doctor_profile")


# ── patient profile views ───────────────────────────────────────────────────────

class PatientProfileView(PatientRequiredMixin, TemplateView):
    """Shows the logged-in patient their own profile."""

    template_name = "project/patient_profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["patient"] = self.get_patient()
        return context


class UpdatePatientProfileView(PatientRequiredMixin, UpdateView):
    """Edit the logged-in patient's profile."""

    model = PatientProfile
    form_class = PatientProfileForm
    template_name = "project/patient_profile_form.html"

    def get_object(self):
        return self.get_patient()

    def get_success_url(self):
        return reverse("patient_profile")


# ── patient case views ──────────────────────────────────────────────────────────

class PatientCaseListView(PatientRequiredMixin, ListView):
    """
    Shows all cases linked to the logged-in patient, ordered by most recent.
    Patients can only see cases where they were explicitly linked by a doctor.
    """

    model = Case
    template_name = "project/case_list_patient.html"
    context_object_name = "cases"

    def get_queryset(self):
        return self.get_patient().cases.order_by("-date_started")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = self.get_patient()
        context["patient"] = patient
        context["total_appointments"] = patient.cases.count()
        return context


class CaseDetailPatientView(PatientRequiredMixin, DetailView):
    """
    Read-only view of a case for the patient. Only shows active symptoms
    and the confirmed/likely conditions — hides ruled-out ones.
    """

    model = Case
    template_name = "project/case_detail_patient.html"
    context_object_name = "case"

    def get_queryset(self):
        return self.get_patient().cases.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["patient"] = self.get_patient()
        context["symptoms"] = (
            self.object.case_symptoms
            .select_related("symptom")
            .filter(is_active=True)
            .order_by("-date_noticed")
        )
        context["conditions"] = (
            self.object.possible_conditions
            .select_related("condition")
            .exclude(status="Ruled Out")
            .order_by("-confidence_score")
        )
        return context


# ── reference data views (public) ───────────────────────────────────────────────

class ConditionListView(ListView):
    """
    Public listing of all conditions in the database, with optional filtering
    by category. Used by doctors as a reference when adding to a case.
    """

    model = Condition
    template_name = "project/condition_list.html"
    context_object_name = "conditions"

    def get_queryset(self):
        qs = Condition.objects.all()
        category = self.request.GET.get("category", "")
        if category:
            qs = qs.filter(category=category)
        return qs.order_by("name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Condition.CATEGORY_CHOICES
        context["selected_category"] = self.request.GET.get("category", "")
        return context


class ConditionDetailView(DetailView):
    """Detail page for a single condition."""

    model = Condition
    template_name = "project/condition_detail.html"
    context_object_name = "condition"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Show how many open cases are currently considering this condition
        context["active_case_count"] = (
            self.object.condition_cases
            .exclude(status="Ruled Out")
            .count()
        )
        return context


class SymptomListView(ListView):
    """
    Public listing of all symptoms, with optional filtering by body system.
    Doctors can use this as a reference while logging symptoms on a case.
    """

    model = Symptom
    template_name = "project/symptom_list.html"
    context_object_name = "symptoms"

    def get_queryset(self):
        qs = Symptom.objects.all()
        body_system = self.request.GET.get("body_system", "")
        if body_system:
            qs = qs.filter(body_system=body_system)
        return qs.order_by("name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["body_systems"] = Symptom.BODY_SYSTEM_CHOICES
        context["selected_system"] = self.request.GET.get("body_system", "")
        return context


class SymptomDetailView(DetailView):
    """Detail page for a single symptom."""

    model = Symptom
    template_name = "project/symptom_detail.html"
    context_object_name = "symptom"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["case_count"] = self.object.symptom_cases.count()
        return context


# ── patient notes ──────────────────────────────────────────────────────────────

class PatientNoteListView(PatientRequiredMixin, ListView):
    """
    Shows the logged-in patient's sent notes, newest first.
    Also shows a link to add a new note.
    """

    model = PatientNote
    template_name = "project/patient_notes_list.html"
    context_object_name = "notes"

    def get_queryset(self):
        return PatientNote.objects.filter(
            patient=self.get_patient()
        ).order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["patient"] = self.get_patient()
        return context


class AddPatientNoteView(PatientRequiredMixin, CreateView):
    """
    Patient writes a note to one of their doctors. The PatientNoteForm
    filters the doctor and case dropdowns to only show records that belong
    to this patient so they can't message unrelated doctors.
    """

    model = PatientNote
    template_name = "project/patient_note_form.html"
    form_class = PatientNoteForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["patient"] = self.get_patient()
        return kwargs

    def form_valid(self, form):
        form.instance.patient = self.get_patient()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["patient"] = self.get_patient()
        return context

    def get_success_url(self):
        return reverse("patient_notes_list")


# ── patient symptom check ──────────────────────────────────────────────────────

def patient_symptom_check(request):
    """
    Function-based view because the form processing logic here is more complex
    than what a generic CreateView can handle — we need to create multiple
    PatientSymptomCheck records (one per checked symptom) from a single form
    submission.

    GET:  shows the checkbox form with all symptoms.
    POST: creates one PatientSymptomCheck per checked symptom, then redirects
          to the patient dashboard.
    """
    if not request.user.is_authenticated:
        return redirect(reverse("login_patient") + f"?next={request.path}")
    patient = PatientProfile.objects.filter(user=request.user).first()
    if not patient:
        return redirect("login_patient")

    if request.method == "POST":
        form = PatientSymptomCheckForm(request.POST)
        if form.is_valid():
            symptoms  = form.cleaned_data["symptoms"]
            notes_txt = form.cleaned_data["notes"]
            for symptom in symptoms:
                PatientSymptomCheck.objects.create(
                    patient=patient,
                    symptom=symptom,
                    notes=notes_txt,
                )
            return redirect("patient_dashboard")
    else:
        form = PatientSymptomCheckForm()

    # Pass today's existing checks so the patient can see what they already reported
    todays_checks = PatientSymptomCheck.objects.filter(
        patient=patient,
        date_reported=timezone.now().date()
    ).select_related("symptom")

    return render(request, "project/patient_symptom_check.html", {
        "form": form,
        "patient": patient,
        "todays_checks": todays_checks,
    })


# ── doctor patient notes ───────────────────────────────────────────────────────

class DoctorPatientNotesView(DoctorRequiredMixin, ListView):
    """
    Doctor sees all notes sent to them, split into unread and read.
    Also shows recent patient symptom check-offs from patients whose
    cases belong to this doctor.
    """

    model = PatientNote
    template_name = "project/doctor_patient_notes.html"
    context_object_name = "notes"

    def get_queryset(self):
        return PatientNote.objects.filter(
            doctor=self.get_doctor()
        ).order_by("is_read", "-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        doctor = self.get_doctor()
        context["doctor"] = doctor
        context["unread_count"] = PatientNote.objects.filter(
            doctor=doctor, is_read=False
        ).count()

        # Collect recent symptom self-reports from all patients with cases under this doctor
        patient_ids = (
            Case.objects.filter(doctor=doctor)
            .values_list("patient_id", flat=True)
            .distinct()
        )
        context["symptom_checks"] = (
            PatientSymptomCheck.objects
            .filter(patient_id__in=patient_ids)
            .select_related("patient", "symptom")
            .order_by("-date_reported", "patient")[:50]
        )
        return context


def mark_note_read(request, pk):
    """
    Marks a single patient note as read and redirects back to the notes page.
    Function-based because it's a simple one-field update that doesn't need
    a full UpdateView — there's no form to render, just a POST action.
    """
    if not request.user.is_authenticated:
        return redirect("login_doctor")
    doctor = DoctorProfile.objects.filter(user=request.user).first()
    if not doctor:
        return redirect("login_doctor")

    note = get_object_or_404(PatientNote, pk=pk, doctor=doctor)
    note.is_read = True
    note.save()
    return redirect("doctor_patient_notes")


# ── doctor availability & scheduling ──────────────────────────────────────────

class DoctorAvailabilityManageView(DoctorRequiredMixin, TemplateView):
    """
    Doctor's availability management page. Shows upcoming open slots,
    booked slots, and pending appointment requests. Doctors can add
    new slots or delete unbooked ones from here.
    """

    template_name = "project/doctor_availability_manage.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        doctor = self.get_doctor()
        today = timezone.now().date()

        context["doctor"] = doctor
        context["open_slots"] = DoctorAvailabilitySlot.objects.filter(
            doctor=doctor, is_booked=False, date__gte=today
        )
        context["booked_slots"] = DoctorAvailabilitySlot.objects.filter(
            doctor=doctor, is_booked=True, date__gte=today
        ).select_related("appointment__patient")
        context["pending_appointments"] = Appointment.objects.filter(
            slot__doctor=doctor, status="Requested"
        ).select_related("patient", "slot").order_by("slot__date", "slot__start_time")
        return context


class AddAvailabilitySlotView(DoctorRequiredMixin, CreateView):
    """
    Doctor adds a new 30-minute availability slot. The form validates that
    the slot is in the future and doesn't duplicate an existing one.
    """

    model = DoctorAvailabilitySlot
    form_class = DoctorAvailabilitySlotForm
    template_name = "project/doctor_add_slot.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["doctor"] = self.get_doctor()
        return kwargs

    def form_valid(self, form):
        form.instance.doctor = self.get_doctor()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["doctor"] = self.get_doctor()
        return context

    def get_success_url(self):
        return reverse("doctor_availability")


class DeleteAvailabilitySlotView(DoctorRequiredMixin, DeleteView):
    """
    Doctor removes an availability slot. Only unbooked slots can be deleted
    (the queryset excludes booked ones so Django returns 404 if they try).
    """

    model = DoctorAvailabilitySlot
    template_name = "project/slot_confirm_delete.html"
    success_url = reverse_lazy("doctor_availability")

    def get_queryset(self):
        return DoctorAvailabilitySlot.objects.filter(
            doctor=self.get_doctor(), is_booked=False
        )


def update_appointment_status(request, pk, action):
    """
    Doctor confirms or cancels an appointment request.
    action must be 'confirm' or 'cancel'.

    Function-based because the logic branches on the action string and
    also needs to update the linked slot's is_booked field when confirming —
    a generic UpdateView would make this awkward.
    """
    if not request.user.is_authenticated:
        return redirect("login_doctor")
    doctor = DoctorProfile.objects.filter(user=request.user).first()
    if not doctor:
        return redirect("login_doctor")

    appt = get_object_or_404(Appointment, pk=pk, slot__doctor=doctor)

    if action == "confirm":
        appt.status = "Confirmed"
        appt.slot.is_booked = True
        appt.slot.save()
    elif action == "cancel":
        appt.status = "Cancelled"
        appt.slot.is_booked = False
        appt.slot.save()

    appt.save()
    return redirect("doctor_availability")


# ── patient booking ────────────────────────────────────────────────────────────

class PatientBookingView(PatientRequiredMixin, TemplateView):
    """
    Patient sees available slots from doctors they've had cases with.
    Slots are grouped by doctor and then by date so it's easy to scan.
    If the patient has no linked cases yet, all doctors with open slots
    are shown instead.
    """

    template_name = "project/patient_booking.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = self.get_patient()
        today = timezone.now().date()

        # Try to limit slots to doctors this patient already knows
        doctor_ids = (
            Case.objects.filter(patient=patient)
            .values_list("doctor_id", flat=True)
            .distinct()
        )

        if doctor_ids:
            slots = DoctorAvailabilitySlot.objects.filter(
                doctor_id__in=doctor_ids, is_booked=False, date__gte=today
            )
        else:
            # Patient has no linked cases yet — show everyone
            slots = DoctorAvailabilitySlot.objects.filter(
                is_booked=False, date__gte=today
            )

        # Group slots by doctor for the template
        slots = slots.select_related("doctor").order_by(
            "doctor__last_name", "date", "start_time"
        )

        # Check which slots this patient has already requested
        requested_slot_ids = set(
            Appointment.objects.filter(patient=patient)
            .values_list("slot_id", flat=True)
        )

        context["patient"] = patient
        context["slots"] = slots
        context["requested_slot_ids"] = requested_slot_ids
        return context


def request_appointment(request, slot_pk):
    """
    Patient requests a specific availability slot. After submitting the reason
    form, creates an Appointment with status=Requested. Function-based because
    we need to pre-validate the slot (must be open, must not already be
    requested by this patient) before showing the form.
    """
    if not request.user.is_authenticated:
        return redirect(reverse("login_patient") + f"?next={request.path}")
    patient = PatientProfile.objects.filter(user=request.user).first()
    if not patient:
        return redirect("login_patient")

    slot = get_object_or_404(DoctorAvailabilitySlot, pk=slot_pk, is_booked=False)

    # Guard: patient shouldn't be able to request the same slot twice
    if Appointment.objects.filter(patient=patient, slot=slot).exists():
        return redirect("patient_booking")

    if request.method == "POST":
        form = AppointmentRequestForm(request.POST)
        if form.is_valid():
            appt = form.save(commit=False)
            appt.patient = patient
            appt.slot = slot
            appt.save()
            return redirect("patient_appointments")
    else:
        form = AppointmentRequestForm()

    return render(request, "project/appointment_request_form.html", {
        "form": form,
        "slot": slot,
        "patient": patient,
    })


class PatientAppointmentListView(PatientRequiredMixin, ListView):
    """Shows the patient all their appointment requests and their current status."""

    model = Appointment
    template_name = "project/patient_appointments.html"
    context_object_name = "appointments"

    def get_queryset(self):
        return Appointment.objects.filter(
            patient=self.get_patient()
        ).select_related("slot", "slot__doctor").order_by("-slot__date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["patient"] = self.get_patient()
        return context
