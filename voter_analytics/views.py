from django.shortcuts import render
from django.views.generic import ListView, DetailView, TemplateView
from django.db.models import Count
import plotly
import plotly.graph_objs as go

from .models import Voter

"""
voter_analytics/views.py
blaise Scileppi
Views for voter analytics listing, detail pages, and graphs.
"""
# Create your views here.

def apply_filters(request, qs):
    """Apply GET-based filters to a voter queryset."""

    party = request.GET.get("party")
    min_year = request.GET.get("min_year")
    max_year = request.GET.get("max_year")
    score = request.GET.get("score")

    if party:
        qs = qs.filter(party_affiliation=party)

    if min_year:
        qs = qs.filter(date_of_birth__year__gte=min_year)

    if max_year:
        qs = qs.filter(date_of_birth__year__lte=max_year)

    if score:
        qs = qs.filter(voter_score=score)

    election_fields = ["v20state", "v21town", "v21primary", "v22general", "v23town"]
    for field in election_fields:
        if request.GET.get(field):
            qs = qs.filter(**{field: True})

    return qs


class VoterListView(ListView):
    """Display and filter voters."""

    model = Voter
    template_name = "voter_analytics/voter_list.html"
    context_object_name = "voters"
    paginate_by = 100

    def get_queryset(self):
        qs = Voter.objects.all().order_by("last_name", "first_name")
        return apply_filters(self.request, qs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["parties"] = (
            Voter.objects.values_list("party_affiliation", flat=True)
            .distinct()
            .order_by("party_affiliation")
        )
        context["years"] = list(range(1920, 2006))
        context["scores"] = [0, 1, 2, 3, 4, 5]
        context["current_filters"] = self.request.GET
        return context


class VoterDetailView(DetailView):
    """Show details for one voter."""

    model = Voter
    template_name = "voter_analytics/voter_detail.html"
    context_object_name = "voter"


class GraphsView(TemplateView):
    """Display graphs for filtered voter data."""

    template_name = "voter_analytics/graphs.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        qs = apply_filters(self.request, Voter.objects.all())

        context["parties"] = (
            Voter.objects.values_list("party_affiliation", flat=True)
            .distinct()
            .order_by("party_affiliation")
        )
        context["years"] = list(range(1920, 2006))
        context["scores"] = [0, 1, 2, 3, 4, 5]
        context["current_filters"] = self.request.GET
        context["result_count"] = qs.count()

        # Graph 1: births by year
        births = (
            qs.values("date_of_birth__year")
            .annotate(total=Count("id"))
            .order_by("date_of_birth__year")
        )
        x1 = [row["date_of_birth__year"] for row in births]
        y1 = [row["total"] for row in births]

        fig1 = go.Bar(x=x1, y=y1)
        context["birth_year_graph"] = plotly.offline.plot(
            {"data": [fig1], "layout_title_text": "Voters by Birth Year"},
            auto_open=False,
            output_type="div",
        )

        # Graph 2: party distribution
        parties = (
            qs.values("party_affiliation")
            .annotate(total=Count("id"))
            .order_by("party_affiliation")
        )
        x2 = [row["party_affiliation"] for row in parties]
        y2 = [row["total"] for row in parties]

        fig2 = go.Pie(labels=x2, values=y2)
        context["party_graph"] = plotly.offline.plot(
            {"data": [fig2], "layout_title_text": "Party Affiliation Distribution"},
            auto_open=False,
            output_type="div",
        )

        # Graph 3: election participation counts
        election_labels = ["v20state", "v21town", "v21primary", "v22general", "v23town"]
        election_counts = [
            qs.filter(v20state=True).count(),
            qs.filter(v21town=True).count(),
            qs.filter(v21primary=True).count(),
            qs.filter(v22general=True).count(),
            qs.filter(v23town=True).count(),
        ]

        fig3 = go.Bar(x=election_labels, y=election_counts)
        context["election_graph"] = plotly.offline.plot(
            {"data": [fig3], "layout_title_text": "Election Participation Counts"},
            auto_open=False,
            output_type="div",
        )

        return context


def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context["parties"] = (
        Voter.objects.values_list("party_affiliation", flat=True)
        .distinct()
        .order_by("party_affiliation")
    )
    context["years"] = list(range(1920, 2006))
    context["scores"] = [0, 1, 2, 3, 4, 5]
    context["current_filters"] = self.request.GET.copy()

    params = self.request.GET.copy()
    if "page" in params:
        params.pop("page")
    context["query_string"] = params.urlencode()

    return context