from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Condition, Symptom, Case, CaseSymptom, Evidence, CaseCondition

admin.site.register(Condition)
admin.site.register(Symptom)
admin.site.register(Case)
admin.site.register(CaseSymptom)
admin.site.register(Evidence)
admin.site.register(CaseCondition)