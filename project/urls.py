# project/urls.py
# holds the urls for the final project app
from django.urls import path
from .views import CaseListView, CaseDetailView, ConditionListView, SymptomListView

urlpatterns = [
    path("", CaseListView.as_view(), name="case_list"),
    path("cases/", CaseListView.as_view(), name="case_list"),
    path("cases/<int:pk>/", CaseDetailView.as_view(), name="case_detail"),
    path("conditions/", ConditionListView.as_view(), name="condition_list"),
    path("symptoms/", SymptomListView.as_view(), name="symptom_list"),
]