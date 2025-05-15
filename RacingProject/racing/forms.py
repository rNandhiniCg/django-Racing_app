from django import forms
from .models import Team, Driver, Race
 
class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'location','logo','description']
 
class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = ['first_name', 'last_name', 'dob', 'team']
 
class RaceForm(forms.ModelForm):
    class Meta:
        model = Race
        fields = ['race_track_name', 'track_location', 'race_date', 'registration_closure_date','registered_drivers']
 
class RegisterDriverToRaceForm(forms.Form):

    # driver = forms.ModelChoiceField(queryset=Driver.objects.all())
    races = forms.ModelMultipleChoiceField(queryset=Race.objects.all(), widget= forms.CheckboxSelectMultiple)

class EditRaceDriversForm(forms.Form):

    #race = forms.ModelChoiceField(queryset=Race.objects.all())
    drivers = forms.ModelMultipleChoiceField(queryset=Driver.objects.all(),  widget= forms.CheckboxSelectMultiple)
       

   
 