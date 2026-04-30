# File: project/urls.py
# Author: Blaise Scileppi (blaises@bu.edu), April 2026
# Description: URL patterns for the Medical Mystery Solver application.
# Organized into: landing, auth, registration, doctor case/evidence/symptom/
# condition views, doctor notes/availability/appointments, search, profiles,
# patient cases/notes/symptom-check/booking, and reference data.

from django.urls import path
from .views import (
    home,
    login_doctor, login_patient, logout_view,
    CreateDoctorView, CreatePatientView,
    DoctorDashboardView, PatientDashboardView,
    DoctorCaseListView, CaseDetailView,
    CreateCaseView, UpdateCaseView, DeleteCaseView,
    AddEvidenceView, UpdateEvidenceView, DeleteEvidenceView,
    AddCaseSymptomView, DeleteCaseSymptomView,
    AddCaseConditionView, UpdateCaseConditionView, DeleteCaseConditionView,
    PatientCaseListView, CaseDetailPatientView,
    ConditionListView, ConditionDetailView,
    SymptomListView, SymptomDetailView,
    SearchCasesView,
    DoctorProfileView, UpdateDoctorProfileView,
    PatientProfileView, UpdatePatientProfileView,
    # messaging & symptom check
    PatientNoteListView, AddPatientNoteView,
    patient_symptom_check,
    DoctorPatientNotesView, mark_note_read,
    # scheduling
    DoctorAvailabilityManageView, AddAvailabilitySlotView,
    DeleteAvailabilitySlotView, update_appointment_status,
    PatientBookingView, request_appointment, PatientAppointmentListView,
)

urlpatterns = [
    # landing
    path("", home, name="home"),

    # auth
    path("login/doctor/", login_doctor, name="login_doctor"),
    path("login/patient/", login_patient, name="login_patient"),
    path("logout/", logout_view, name="logout"),

    # registration
    path("register/doctor/", CreateDoctorView.as_view(), name="register_doctor"),
    path("register/patient/", CreatePatientView.as_view(), name="register_patient"),

    # doctor dashboard and case list
    path("doctor/", DoctorDashboardView.as_view(), name="doctor_dashboard"),
    path("doctor/cases/", DoctorCaseListView.as_view(), name="doctor_case_list"),
    path("doctor/cases/new/", CreateCaseView.as_view(), name="create_case"),
    path("doctor/cases/<int:pk>/", CaseDetailView.as_view(), name="case_detail"),
    path("doctor/cases/<int:pk>/edit/", UpdateCaseView.as_view(), name="update_case"),
    path("doctor/cases/<int:pk>/delete/", DeleteCaseView.as_view(), name="delete_case"),

    # evidence
    path("doctor/cases/<int:case_pk>/evidence/add/", AddEvidenceView.as_view(), name="add_evidence"),
    path("doctor/evidence/<int:pk>/edit/", UpdateEvidenceView.as_view(), name="update_evidence"),
    path("doctor/evidence/<int:pk>/delete/", DeleteEvidenceView.as_view(), name="delete_evidence"),

    # case symptoms
    path("doctor/cases/<int:case_pk>/symptoms/add/", AddCaseSymptomView.as_view(), name="add_case_symptom"),
    path("doctor/case-symptoms/<int:pk>/delete/", DeleteCaseSymptomView.as_view(), name="delete_case_symptom"),

    # case conditions (differential diagnosis tracking)
    path("doctor/cases/<int:case_pk>/conditions/add/", AddCaseConditionView.as_view(), name="add_case_condition"),
    path("doctor/case-conditions/<int:pk>/edit/", UpdateCaseConditionView.as_view(), name="update_case_condition"),
    path("doctor/case-conditions/<int:pk>/delete/", DeleteCaseConditionView.as_view(), name="delete_case_condition"),

    # doctor: patient notes & notifications
    path("doctor/patient-notes/", DoctorPatientNotesView.as_view(), name="doctor_patient_notes"),
    path("doctor/patient-notes/<int:pk>/read/", mark_note_read, name="mark_note_read"),

    # doctor: availability & appointments
    path("doctor/availability/", DoctorAvailabilityManageView.as_view(), name="doctor_availability"),
    path("doctor/availability/add/", AddAvailabilitySlotView.as_view(), name="add_availability_slot"),
    path("doctor/availability/<int:pk>/delete/", DeleteAvailabilitySlotView.as_view(), name="delete_availability_slot"),
    path("doctor/appointments/<int:pk>/<str:action>/", update_appointment_status, name="update_appointment_status"),

    # search
    path("doctor/search/", SearchCasesView.as_view(), name="search_cases"),

    # doctor profile
    path("doctor/profile/", DoctorProfileView.as_view(), name="doctor_profile"),
    path("doctor/profile/edit/", UpdateDoctorProfileView.as_view(), name="update_doctor_profile"),

    # patient: dashboard and cases
    path("patient/", PatientDashboardView.as_view(), name="patient_dashboard"),
    path("patient/cases/", PatientCaseListView.as_view(), name="patient_case_list"),
    path("patient/cases/<int:pk>/", CaseDetailPatientView.as_view(), name="case_detail_patient"),
    path("patient/profile/", PatientProfileView.as_view(), name="patient_profile"),
    path("patient/profile/edit/", UpdatePatientProfileView.as_view(), name="update_patient_profile"),

    # patient: notes to doctor
    path("patient/notes/", PatientNoteListView.as_view(), name="patient_notes_list"),
    path("patient/notes/add/", AddPatientNoteView.as_view(), name="add_patient_note"),

    # patient: symptom self-check
    path("patient/symptoms/check/", patient_symptom_check, name="patient_symptom_check"),

    # patient: booking
    path("patient/book/", PatientBookingView.as_view(), name="patient_booking"),
    path("patient/book/<int:slot_pk>/", request_appointment, name="request_appointment"),
    path("patient/appointments/", PatientAppointmentListView.as_view(), name="patient_appointments"),

    # reference data — conditions and symptoms (accessible to all)
    path("conditions/", ConditionListView.as_view(), name="condition_list"),
    path("conditions/<int:pk>/", ConditionDetailView.as_view(), name="condition_detail"),
    path("symptoms/", SymptomListView.as_view(), name="symptom_list"),
    path("symptoms/<int:pk>/", SymptomDetailView.as_view(), name="symptom_detail"),
]
