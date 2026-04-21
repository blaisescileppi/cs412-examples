from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView, DetailView
from .models import Case, Condition, Symptom


class CaseListView(ListView):
    model = Case
    template_name = "project/case_list.html"
    context_object_name = "cases"


class CaseDetailView(DetailView):
    model = Case
    template_name = "project/case_detail.html"
    context_object_name = "case"


class ConditionListView(ListView):
    model = Condition
    template_name = "project/condition_list.html"
    context_object_name = "conditions"


class SymptomListView(ListView):
    model = Symptom
    template_name = "project/symptom_list.html"
    context_object_name = "symptoms"