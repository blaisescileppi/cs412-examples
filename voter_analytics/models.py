"""
voter_analytics/models.py
Blaise Scileppi
Model and data loader for Newton voter analytics.
"""
#imports
from django.db import models
from datetime import datetime
from urllib.parse import quote_plus

# models:

class Voter(models.Model):
    """Model representing one Newton voter record."""

    voter_id = models.TextField()
    last_name = models.TextField()
    first_name = models.TextField()

    street_number = models.TextField()
    street_name = models.TextField()
    apartment_number = models.TextField(blank=True)
    zip_code = models.TextField()

    date_of_birth = models.DateField()
    date_of_registration = models.DateField()

    party_affiliation = models.CharField(max_length=2)
    precinct_number = models.CharField(max_length=10)

    v20state = models.BooleanField(default=False)
    v21town = models.BooleanField(default=False)
    v21primary = models.BooleanField(default=False)
    v22general = models.BooleanField(default=False)
    v23town = models.BooleanField(default=False)

    voter_score = models.IntegerField()

    def __str__(self):
        """Return a readable string representation of this voter."""
        return f"{self.first_name} {self.last_name} ({self.party_affiliation})"

    def full_street_address(self):
        """Return a formatted street address."""
        if self.apartment_number:
            return f"{self.street_number} {self.street_name}, Apt {self.apartment_number}"
        return f"{self.street_number} {self.street_name}"

    def full_address(self):
        """Return the full mailing address."""
        return f"{self.full_street_address()}, Newton, MA {self.zip_code}"

    def google_maps_url(self):
        """Return a Google Maps search URL for this voter's address."""
        return f"https://www.google.com/maps/search/?api=1&query={quote_plus(self.full_address())}"

# function to load my data into
def load_data():
    """Load voter records from the Newton CSV file into the database."""

    filename = "/Users/blaisescileppi/Desktop/django/newton_voters.csv"

    # Prevent duplicates if load_data() is run more than once
    Voter.objects.all().delete()

    with open(filename, "r", encoding="utf-8-sig") as f:
        f.readline()  # discard header row

        for line in f:
            fields = line.strip().split(",")

            try:
                voter = Voter(
                    voter_id=fields[0],
                    last_name=fields[1],
                    first_name=fields[2],
                    street_number=fields[3],
                    street_name=fields[4],
                    apartment_number=fields[5],
                    zip_code=fields[6],
                    date_of_birth=datetime.strptime(fields[7], "%Y-%m-%d").date(),
                    date_of_registration=datetime.strptime(fields[8], "%Y-%m-%d").date(),
                    party_affiliation=fields[9].strip(),
                    precinct_number=fields[10].strip(),
                    v20state=(fields[11].strip().upper() == "TRUE"),
                    v21town=(fields[12].strip().upper() == "TRUE"),
                    v21primary=(fields[13].strip().upper() == "TRUE"),
                    v22general=(fields[14].strip().upper() == "TRUE"),
                    v23town=(fields[15].strip().upper() == "TRUE"),
                    voter_score=int(fields[16]),
                )
                voter.save()

            except Exception as e:
                print(f"Skipped: {fields}")
                print(f"Reason: {e}")

    print(f"Done. Created {Voter.objects.count()} voters.")
    