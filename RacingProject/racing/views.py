from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import DeleteView
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.utils import timezone

from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from .models import *
from .forms import *
from .serializers import *

# Create your views here.

def home(request):
    return render(request,'home.html')

#Team Views***
#Team view (with drivers)
def team_list(request):
    teams = Team.objects.all().prefetch_related('drivers')
    return render(request, 'team/team_list.html', {'teams': teams})

def team_create(request):
    if request.method == 'POST':
        form = TeamForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('team_list')
        else:
            print(form.errors) # Print form errors to the console
    else:
        form = TeamForm()
    return render(request, 'team/team_form.html', {'form': form})

def team_edit(request, pk):
    team = Team.objects.get(pk=pk)
    if request.method == 'POST':
        form = TeamForm(request.POST, request.FILES, instance=team)
        if form.is_valid():
            form.save()
            return redirect('team_list')
    else:
        form = TeamForm(instance=team)
    return render(request, 'team/team_form.html', {'form': form})
  
class TeamDeleteView(DeleteView):
    model= Team
    success_url= reverse_lazy('team_list')
    def get(self, request, *args, **kwargs):
        return self.delete(self, request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object= self.get_object()
        if self.object.drivers.filter(registered_races__isnull=False).exists():
            messages.error(self.request, "Cannot delete Team: One or more Drivers have registered for races. ")
            return HttpResponseRedirect(self.success_url)
        
        return super().delete(request, *args, **kwargs)

''' 
def team_delete(request, pk):
1). team = get_object_or_404(Team, pk=pk) 
    drivers= team.drivers.all()

    for driver in drivers:
        if driver.registered_races.exists():
            messages.error(request, "Cannot delete team: One or more drivers have registered for races.")
            print("Cannot delete team: One or more drivers are registered for races.")
            return redirect('team_list')
    
    team.delete()
    messages.success(request, "Team deleted successfully.")
    return redirect('team_list')

    2). team = get_object_or_404(Team, pk=pk)
    try:
        team.delete()
        messages.success(request, "Team deleted successfully.")
    except ValidationError as e:
         messages.error(request, str(e.message))
    return redirect('team_list')
'''

#Driver Views***
def driver_list(request):
    drivers = Driver.objects.all()
    return render(request, 'driver/driver_list.html', {'drivers': drivers})  
'''
#Driver view (upcoming + Registered races)
def driver_detail(request, driver_id):
    driver = Driver.objects.get(id=driver_id)
    upcoming_races = Race.objects.filter(race_date__gt=timezone.now())
    return render(request, 'driver/driver_detail.html', {
        'driver': driver,
        'upcoming_races': upcoming_races,
    })
'''
def driver_create(request):
    form = DriverForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('driver_list')
    return render(request, 'driver/driver_form.html', {'form': form, 'title': 'Create Driver'})

def driver_edit(request, pk):
    driver = get_object_or_404(Driver, pk=pk)
    if request.method == 'POST':
        form = DriverForm(request.POST, instance=driver)
        if form.is_valid():
            form.save()
            return redirect('driver_list')
    else:
        form = DriverForm(instance=driver)
    return render(request, 'driver/driver_form.html', {'form': form})

class DriverDeleteView(DeleteView):
    model= Driver
    success_url= reverse_lazy('driver_list')
    def get(self, request, *args, **kwargs):
        return self.delete(self, request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object= self.get_object()
        if self.object.registered_races.exists():   # Prevent deletion if registered to at least one race
            messages.error(self.request, "Cannot delete Driver: Driver have registered for races. ")
            return HttpResponseRedirect(self.success_url)
        
        return super().delete(request, *args, **kwargs)
'''
def driver_delete(request, pk):
    driver = get_object_or_404(Driver, pk=pk)
    if driver.registered_races.exists(): # Prevent deletion if registered to at least one race
        print("Driver cannot be deleted - registered in one or more races")
        return redirect('driver_list')
    else:
        driver.delete()
        print("Driver deleted, Successfully ")
        return redirect('driver_list')
'''    

#Race Views***
def race_list(request):
    races = Race.objects.all()
    return render(request, 'race/race_list.html', {'races': races})

'''
#Race view (with Registered Drivers)
def race_detail(request, race_id):
    race = Race.objects.get(id=race_id)
    return render(request, 'race/race_detail.html', {'race': race})
'''

def race_create(request):
    form = RaceForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('race_list')
    return render(request, 'race/race_form.html', {'form': form, 'title': 'Create Race'})

def race_edit(request,pk):
    race = get_object_or_404(Race, pk=pk)
    if request.method == 'POST':
        form = RaceForm(request.POST, instance=race)
        if form.is_valid():
            form.save()
            return redirect('race_list')
    else:
        form = RaceForm(instance=race)
    return render(request, 'race/race_form.html', {'form': form})

class RaceDeleteView(DeleteView):
    model= Race
    success_url= reverse_lazy('race_list')
    def get(self, request, *args, **kwargs):
        return self.delete(self, request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object= self.get_object()
        if self.object.registered_drivers.filter(registered_races__isnull=False).exists():
            messages.error(self.request, "Cannot delete Race: One or more Drivers have registered for races. ")
            return HttpResponseRedirect(self.success_url)
        
        return super().delete(request, *args, **kwargs)

'''
def race_delete(request, pk):
    race = get_object_or_404(Race, pk=pk)
    drivers= race.registered_drivers.all()

    for driver in drivers:
        if driver.registered_races.exists():
            messages.error(request, "Cannot delete race: One or more drivers are registered for races.")
            print("Cannot delete race: One or more drivers are registered for races.")
            return redirect('race_list')
    
    race.delete() 
    messages.success(request, "Race deleted successfully.")
    return redirect('race_list')
'''

# Register driver to race
def register_driver_to_race(request, driver_id):
    
    driver= get_object_or_404(Driver, pk= driver_id)
    if request.method == 'POST':
        form = RegisterDriverToRaceForm(request.POST)
        if form.is_valid():
            #driver = form.cleaned_data['driver']
            selected_races = form.cleaned_data['races']


            #for race in selected_races:
            driver.registered_races.set(selected_races)
            return redirect('driver_list')
    else:
        form= RegisterDriverToRaceForm(initial={'races':driver.registered_races.all()})
        
    return render(request, 'register_driver.html', {'form': form, 'driver': driver, 'title': f'Add/Edit Races for  \'Driver_{driver}\''})

def edit_race_drivers(request, race_id):
    race= get_object_or_404(Race, pk= race_id)
    if request.method == 'POST':

        form = EditRaceDriversForm(request.POST)
        if form.is_valid():
            #race = form.cleaned_data['race']
            selected_drivers = form.cleaned_data['drivers']
           
            race.registered_drivers.set(selected_drivers)
            return redirect('race_list')
    else:
        #form=  EditRaceDriversForm
        form=  EditRaceDriversForm(initial={'drivers':race.registered_drivers.all()})
        
    return render(request, 'register_driver.html', {'form': form, 'title': f"Add/Edit Drivers for 'Race_{race}\'"})

#API Views***
# 1. modelViewSets, 2. generics API views
#TEAM API views - list, CRUD 
class TeamListView(generics.ListAPIView):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
 
 
class TeamCreateView(generics.CreateAPIView):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
 
 
class TeamRetrieveView(generics.RetrieveAPIView):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
 
 
class TeamUpdateView(generics.UpdateAPIView):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
 
 
class TeamDeleteViewAPI(generics.DestroyAPIView):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

    def delete(self, request, *args, **kwargs):
        team = self.get_object()

        drivers= team.drivers.all()
        for driver in drivers:
            if driver.registered_races.exists():
                return Response({"error": "Cannot delete team with registered drivers for races."},
                    status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)


#Driver API views
class DriverListView(generics.ListAPIView):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
  
class DriverCreateView(generics.CreateAPIView):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
 
class DriverRetrieveView(generics.RetrieveAPIView):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
 
class DriverUpdateView(generics.UpdateAPIView):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
 
class DriverDeleteViewAPI(generics.DestroyAPIView):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
 
    def delete(self, request, *args, **kwargs):
        driver = self.get_object()
        if driver.registered_races.exists():
            return Response({"error": "Cannot delete driver who is registered for races."},
                            status=status.HTTP_400_BAD_REQUEST)
        return super().delete(request, *args, **kwargs) 
    
#Race API views
class RaceListView(generics.ListAPIView):
    queryset = Race.objects.all()
    serializer_class = RaceSerializer

class RaceCreateView(generics.CreateAPIView):
    queryset = Race.objects.all()
    serializer_class = RaceSerializer

class RaceRetrieveView(generics.RetrieveAPIView):
    queryset = Race.objects.all()
    serializer_class = RaceSerializer
  
class RaceUpdateView(generics.UpdateAPIView):
    queryset = Race.objects.all()
    serializer_class = RaceSerializer
 
class RaceDeleteViewAPI(generics.DestroyAPIView):
    queryset = Race.objects.all()
    serializer_class = RaceSerializer
 
    def delete(self, request, *args, **kwargs):
        race = self.get_object()
        if race.registered_drivers.exists():
            return Response({"error": "Cannot delete race with registered drivers."},
                            status=status.HTTP_400_BAD_REQUEST)
        return super().delete(request, *args, **kwargs)


class AddDriversToRaceAPIView(APIView):
    def post(self, request, race_id):
        race = get_object_or_404(Race, id=race_id)
        serializer = AddDriversToRaceSerializer1(data=request.data, context= {'race':race})
        if serializer.is_valid():
            drivers = serializer.validated_data['drivers']
            race.registered_drivers.add(*drivers)
            return Response({'message': 'Drivers added to race successfully.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    


        

 
