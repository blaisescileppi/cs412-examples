from django.db import models

# Create your models here.
# Voter Model to represent a registered Voter
class Voter(models.Model):
    '''
    info about the model here
    '''

    # ID
    first_name = models.TextField()
    last_name = models.TextField()
    zip_code = models.TextField()
    street_name = models.TextField()
    dob = models.DateField()

    # poltical affiliation
    party = models.CharField(max_length=1)
    year_participation = models.BooleanField(default=False)

 
    def __str__(self):
        '''Return a string representation of this model instance.'''
        return f'{self.first_name} {self.last_name} {self.party} {self.dob} {self.zip_code}'



