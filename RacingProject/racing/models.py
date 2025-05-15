from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.validators import FileExtensionValidator
import datetime

# Create your models here.
#Custom validations
def validate_image_size(image):
    if image.size > 50*1024:
        raise ValidationError("Image size should not exceed 50KB.")

def validate_dob(value):
    if value > timezone.datetime(2000, 12, 31).date():
        raise ValidationError("Driver must be born on or before 31/12/2000.")
 
def validate_future_date(value):
    if value <= timezone.now().date():
        raise ValidationError("Race date must be in the future.")
 
def validate_past_date(value):
    if value and value >= timezone.now().date():
        raise ValidationError("Registration closure date must be in the past.")

        
class Team(models.Model):
    name = models.CharField(max_length=256, unique=True )
    location = models.CharField(max_length=256)
    logo = models.ImageField(upload_to='logos/',validators=[validate_image_size],null=False,blank=False)
    description = models.TextField(max_length=1024, null=True, blank=True)

    def __str__(self):
        return self.name

   
class Driver(models.Model):
    first_name = models.CharField(max_length=96, null=False)
    last_name = models.CharField(max_length=96, null=False)
    dob = models.DateField(validators=[validate_dob])
    team = models.ForeignKey(Team,  null=True, blank=True, on_delete= models.CASCADE, related_name='drivers')
    
    def clean(self):
        if Driver.objects.exclude(pk=self.pk).filter(first_name= self.first_name, last_name=self.last_name, dob= self.dob).exists():
            raise ValidationError("Driver already exists")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Race(models.Model):
    race_track_name = models.CharField(max_length=256)
    track_location = models.CharField(max_length=100)
    race_date = models.DateField(validators=[validate_future_date]) 
    registration_closure_date = models.DateField(blank=True, null=True)
    registered_drivers = models.ManyToManyField(Driver, related_name='registered_races', blank=True, null=True)

 
    def __str__(self):
        return self.race_track_name

    def clean(self):
        if self.registration_closure_date and self.race_date:
            if self.registration_closure_date >= self.race_date:
                raise ValidationError("Registration Closure date must be before the Race date !")




