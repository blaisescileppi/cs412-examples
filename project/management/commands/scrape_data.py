# File: project/management/commands/scrape_data.py
# Author: Blaise Scileppi (blaises@bu.edu), April 2026
# Description: Management command to populate Condition and Symptom tables
# with real medical data pulled from the web. Two different sources are used:
#
#   Conditions: The NLM Clinical Tables API (clinicaltables.nlm.nih.gov)
#               returns condition names as JSON for a given search term.
#               No API key required. This is the National Library of Medicine's
#               public autocomplete service used by many health applications.
#
#   Symptoms:   The Wikipedia REST API (en.wikipedia.org/api/rest_v1) returns
#               plain-text article summaries as JSON given an article title.
#               Also public, no key required.
#
# For each condition name returned by the NLM API, we make a second call to
# Wikipedia to get a real plain-English description before saving to the DB.
# This shows two different API integrations in one command.
#
# Run with: python manage.py scrape_data
# Options:
#   --conditions-only   only scrape conditions
#   --symptoms-only     only populate symptoms
#   --limit N           max new condition records to create (default 30)

import time
import requests
from django.core.management.base import BaseCommand
from project.models import Condition, Symptom


# ── search terms fed to the NLM Clinical Tables API ───────────────────────────
# Each term returns up to 10 matching condition names. Using multiple terms
# gives us a varied set that covers the app's focus (hormonal, metabolic,
# reproductive, autoimmune, nutritional, etc.).

NLM_SEARCH_TERMS = [
    "thyroid",
    "diabetes",
    "polycystic",
    "anemia",
    "autoimmune",
    "endometriosis",
    "vitamin deficiency",
    "lupus",
    "irritable",
    "celiac",
    "fibromyalgia",
    "cushing",
    "addison",
    "hypertension",
    "osteoporosis",
    "pcos",
    "menstrual",
    "crohn",
    "graves",
    "hashimoto",
]

# ── keyword-based category and red-flag guessing ──────────────────────────────

CATEGORY_KEYWORDS = {
    "Hormonal":     ["thyroid", "hypothyroid", "hyperthyroid", "cortisol", "adrenal",
                     "diabetes insipidus", "goiter", "pituitary", "hormone", "cushing",
                     "addison", "graves", "hashimoto"],
    "Metabolic":    ["diabetes", "metabolic", "obesity", "lipid", "cholesterol",
                     "gout", "hypoglycemia", "phenylketonuria"],
    "Reproductive": ["polycystic", "endometriosis", "ovarian", "menstrual",
                     "uterine", "fertility", "pelvic", "premenstrual", "pcos"],
    "Autoimmune":   ["lupus", "hashimoto", "graves", "rheumatoid", "sjogren",
                     "celiac", "psoriasis", "autoimmune", "myasthenia"],
    "Nutritional":  ["vitamin", "iron deficiency", "anemia", "malnutrition",
                     "deficiency", "scurvy", "rickets", "osteoporosis"],
    "Infectious":   ["infection", "virus", "bacterial", "hiv", "hepatitis",
                     "tuberculosis", "pneumonia", "influenza"],
}

HIGH_FLAG_KEYWORDS   = ["cancer", "tumor", "acute", "meningitis", "sepsis",
                         "embolism", "infarction", "stroke", "hemorrhage"]
MEDIUM_FLAG_KEYWORDS = ["diabetes", "hypertension", "lupus", "multiple sclerosis",
                         "epilepsy", "heart disease", "graves", "hashimoto",
                         "polycystic", "endometriosis", "cushing", "addison",
                         "crohn", "celiac", "fibromyalgia"]


def guess_category(name):
    """
    Returns a Condition category based on keywords in the condition name.
    Falls back to 'Other' if nothing matches.
    """
    lower = name.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in lower:
                return category
    return "Other"


def guess_red_flag(name):
    """
    Returns High / Medium / Low based on how serious the condition sounds.
    This is a rough heuristic — good enough for demo data.
    """
    lower = name.lower()
    for kw in HIGH_FLAG_KEYWORDS:
        if kw in lower:
            return "High"
    for kw in MEDIUM_FLAG_KEYWORDS:
        if kw in lower:
            return "Medium"
    return "Low"


# ── symptom data ──────────────────────────────────────────────────────────────
# Tuples of (display_name, body_system, is_common, wikipedia_article_title).
# Descriptions are fetched live from Wikipedia at runtime.

SYMPTOM_DATA = [
    ("Fatigue",                   "General",        True,  "Fatigue"),
    ("Headache",                  "Neurological",   True,  "Headache"),
    ("Weight gain",               "General",        True,  "Weight gain"),
    ("Weight loss",               "General",        True,  "Weight loss"),
    ("Nausea",                    "Digestive",      True,  "Nausea"),
    ("Brain fog",                 "Neurological",   True,  "Brain fog"),
    ("Hair loss",                 "Skin",           True,  "Hair loss"),
    ("Dry skin",                  "Skin",           True,  "Dry skin"),
    ("Bloating",                  "Digestive",      True,  "Bloating"),
    ("Constipation",              "Digestive",      True,  "Constipation"),
    ("Diarrhea",                  "Digestive",      True,  "Diarrhea"),
    ("Irregular menstrual cycle", "Reproductive",   True,  "Irregular menstruation"),
    ("Pelvic pain",               "Reproductive",   True,  "Pelvic pain"),
    ("Hot flashes",               "Endocrine",      True,  "Hot flash"),
    ("Cold intolerance",          "Endocrine",      True,  "Cold intolerance"),
    ("Heat intolerance",          "Endocrine",      True,  "Heat intolerance"),
    ("Excessive sweating",        "General",        True,  "Hyperhidrosis"),
    ("Heart palpitations",        "Cardiovascular", True,  "Palpitation"),
    ("High blood pressure",       "Cardiovascular", True,  "Hypertension"),
    ("Shortness of breath",       "Cardiovascular", True,  "Dyspnea"),
    ("Joint pain",                "General",        True,  "Arthralgia"),
    ("Muscle weakness",           "General",        True,  "Muscle weakness"),
    ("Acne",                      "Skin",           True,  "Acne"),
    ("Excessive thirst",          "Endocrine",      True,  "Polydipsia"),
    ("Frequent urination",        "Endocrine",      True,  "Polyuria"),
    ("Mood changes",              "Neurological",   True,  "Mood disorder"),
    ("Anxiety",                   "Neurological",   True,  "Anxiety"),
    ("Depression",                "Neurological",   True,  "Depression_(mood)"),
    ("Insomnia",                  "Neurological",   True,  "Insomnia"),
    ("Night sweats",              "General",        True,  "Night sweats"),
]


# ── the command ────────────────────────────────────────────────────────────────

class Command(BaseCommand):
    """
    Populates Condition and Symptom tables using data scraped from:
      - NLM Clinical Tables API (condition names)
      - Wikipedia REST API (descriptions for both conditions and symptoms)
    Safe to run multiple times — uses get_or_create to skip existing records.
    """

    help = "Populates Condition and Symptom tables using the NLM and Wikipedia APIs"

    def add_arguments(self, parser):
        parser.add_argument(
            "--conditions-only", action="store_true",
            help="Only scrape conditions, skip symptoms"
        )
        parser.add_argument(
            "--symptoms-only", action="store_true",
            help="Only populate symptoms, skip conditions"
        )
        parser.add_argument(
            "--limit", type=int, default=30,
            help="Max new Condition records to create (default 30)"
        )

    def handle(self, *args, **kwargs):
        conditions_only = kwargs["conditions_only"]
        symptoms_only   = kwargs["symptoms_only"]
        limit           = kwargs["limit"]

        if not symptoms_only:
            self.populate_conditions(limit)
        if not conditions_only:
            self.populate_symptoms()

        self.stdout.write(self.style.SUCCESS("\nAll done."))

    # ── network helpers ──────────────────────────────────────────────────────────

    def get_json(self, url, label=""):
        """
        Makes a GET request and returns the parsed JSON, or None on failure.
        Adds a small delay so we don't send too many requests per second.
        """
        try:
            headers = {"User-Agent": "Mozilla/5.0 (cs412 educational project)"}
            r = requests.get(url, headers=headers, timeout=8)
            time.sleep(0.7)
            if r.status_code == 200:
                return r.json()
            self.stdout.write(f"    HTTP {r.status_code}: {label or url}")
        except requests.RequestException as e:
            self.stdout.write(f"    request failed ({label}): {e}")
        return None

    def fetch_nlm_condition_names(self, term, max_list=10):
        """
        Calls the NLM Clinical Tables autocomplete API and returns a list of
        condition name strings matching the given search term.

        API endpoint:
            https://clinicaltables.nlm.nih.gov/api/conditions/v3/search
        Parameters:
            terms    — the search term
            maxList  — max results to return (up to 500)

        Response format: [total, id_list, null, [[name], [name], ...]]
        The condition names live in response[3], each wrapped in a single-item list.
        """
        url = (
            "https://clinicaltables.nlm.nih.gov/api/conditions/v3/search"
            f"?terms={requests.utils.quote(term)}&maxList={max_list}"
        )
        data = self.get_json(url, label=f"NLM/{term}")
        if not data or len(data) < 4 or not data[3]:
            return []
        # data[3] is a list of single-element lists: [["Condition Name"], ...]
        return [row[0] for row in data[3] if row and row[0]]

    def fetch_wikipedia_summary(self, title):
        """
        Calls the Wikipedia REST API to get a plain-English summary for an
        article. Returns up to 500 characters of the extract, or empty string.

        Endpoint: https://en.wikipedia.org/api/rest_v1/page/summary/{title}
        No authentication required. Returns JSON with an "extract" field.
        """
        safe_title = title.replace(" ", "_")
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{safe_title}"
        data = self.get_json(url, label=f"Wikipedia/{title}")
        if data:
            extract = data.get("extract", "")
            return extract[:500] if extract else ""
        return ""

    # ── conditions ───────────────────────────────────────────────────────────────

    def populate_conditions(self, limit):
        """
        For each search term in NLM_SEARCH_TERMS, queries the NLM Clinical
        Tables API to get matching condition names. For each unique name, calls
        Wikipedia to get a description before saving to the Condition table.
        Stops after `limit` new records are created.

        The NLM API is the National Library of Medicine's public service — the
        same one used by clinical intake forms and EHR systems. It has 2,400+
        conditions indexed and is free to use for non-commercial purposes.
        """
        self.stdout.write(self.style.HTTP_INFO(
            f"\nFetching conditions from NLM Clinical Tables API (limit={limit})..."
        ))

        seen = set()    # avoid duplicate names across different search terms
        saved = 0

        for term in NLM_SEARCH_TERMS:
            if saved >= limit:
                break

            names = self.fetch_nlm_condition_names(term, max_list=10)
            self.stdout.write(f"  NLM '{term}': {len(names)} results")

            for name in names:
                if saved >= limit:
                    break
                if name in seen:
                    continue
                seen.add(name)

                # Hit Wikipedia for a real description using the condition name
                # as the search title. May not always find an exact match.
                description = self.fetch_wikipedia_summary(name)
                if not description:
                    description = (
                        f"{name} is a medical condition. "
                        "Consult a healthcare provider for diagnosis and treatment."
                    )

                category = guess_category(name)
                red_flag = guess_red_flag(name)

                obj, created = Condition.objects.get_or_create(
                    name=name,
                    defaults={
                        "category":         category,
                        "description":      description,
                        "red_flag_level":   red_flag,
                        "common_age_group": "",
                        "typical_duration": "",
                    }
                )

                if created:
                    saved += 1
                    self.stdout.write(
                        f"    + [{category:<14}] [{red_flag:<6}]  {name}"
                    )
                else:
                    self.stdout.write(f"    ~ exists: {name}")

        self.stdout.write(
            self.style.SUCCESS(f"Conditions: {saved} new records saved.")
        )

    # ── symptoms ─────────────────────────────────────────────────────────────────

    def populate_symptoms(self):
        """
        Populates the Symptom table using the SYMPTOM_DATA list above.
        For each symptom, calls the Wikipedia REST API to get a real description.
        Falls back to a generic sentence if Wikipedia can't find the article.
        """
        self.stdout.write(self.style.HTTP_INFO(
            "\nPopulating symptoms (descriptions from Wikipedia REST API)..."
        ))
        saved = 0

        for name, body_system, is_common, wiki_title in SYMPTOM_DATA:
            description = self.fetch_wikipedia_summary(wiki_title)
            if not description:
                description = (
                    f"{name} is a clinical symptom that can appear alongside "
                    "various medical conditions. Frequency and severity vary by case."
                )

            obj, created = Symptom.objects.get_or_create(
                name=name,
                defaults={
                    "body_system": body_system,
                    "description": description,
                    "is_common":   is_common,
                }
            )

            if created:
                saved += 1
                self.stdout.write(f"  + [{body_system:<14}]  {name}")
            else:
                self.stdout.write(f"  ~ exists: {name}")

        self.stdout.write(
            self.style.SUCCESS(f"Symptoms: {saved} new records saved.")
        )
