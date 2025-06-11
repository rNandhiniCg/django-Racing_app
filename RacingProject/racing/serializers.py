from rest_framework import serializers
from .models import Team, Driver, Race

class TeamSerializer(serializers.ModelSerializer):
    #drivers= DriversTeamSerializer( many=True, read_only=True)
    drivers = serializers.SerializerMethodField()  #field def'd using SerializerMtdField(w/c is inherently read-only).

    class Meta:
        model = Team
        fields = ['id' ,'name', 'location', 'logo', 'description', 'drivers']
    
    def get_drivers(self, obj):
        return [f"{driver.first_name} {driver.last_name}" for driver in obj.drivers.all()]


class DriverSerializer(serializers.ModelSerializer):
    team= serializers.CharField()  #show only team name, not entire team info &  # Accept team name as input
    #registered_races= RaceShortSerializer(many=True, read_only=True)
    registered_races= serializers.SerializerMethodField()
    
    class Meta:
        model = Driver
        fields = [ 'id', 'first_name', 'last_name', 'dob', 'team', 'registered_races']
        #extra_kwargs={ 'registered_races':{'required':False, 'allow_empty':True}   }

    def create(self, validated_data):
        print("before pop:", validated_data)
        team_name = validated_data.pop('team')
        print("after:", team_name)
        try:
            team = Team.objects.get(name=team_name)
        except Team.DoesNotExist:
            raise serializers.ValidationError({'team': 'Team with this name does not exist.'})
        driver = Driver.objects.create(team=team, **validated_data)
        return driver
    
    def validate_team(self, value):
        if not Team.objects.filter(name=value).exists():
            raise serializers.ValidationError("Team with this name does not exist.")
        return value

    
    def update(self, instance, validated_data):
        team_name = validated_data.pop('team', None)
        if team_name:
            try:
                team = Team.objects.get(name=team_name)
                instance.team = team
            except Team.DoesNotExist:
                raise serializers.ValidationError("Team with this name does not exist.")
        return super().update(instance, validated_data)
    
    
    def get_registered_races(self, obj):
        return [f"{race.race_track_name} on {race.race_date}" for race in obj.registered_races.all()]


class DriverNameListField(serializers.Field):      #to make reg_drivers both read & write field
    def to_representation(self, value):
        # Fixes the 500 error
        try:
            drivers = value.all()  # when it's a RelatedManager
        except AttributeError:
            drivers = value  # when it's already a list of Driver instances
        return [f"{driver.first_name} {driver.last_name}" for driver in drivers]
 
    def to_internal_value(self, data):
        # Convert list of names to driver instances
        if not isinstance(data, list):
            raise serializers.ValidationError("Expected a list of driver names.")
        
        driver_objs = []
        for full_name in data:
            try:
                first_name, last_name = full_name.split(' ', 1)
            except ValueError:
                raise serializers.ValidationError(
                    f"Invalid driver name format: '{full_name}'. Use 'First Last'."
                )
            try:
                driver = Driver.objects.get(first_name=first_name, last_name=last_name)
                driver_objs.append(driver)
            except Driver.DoesNotExist:
                raise serializers.ValidationError(f"Driver '{full_name}' not found.")
        return driver_objs

class RaceSerializer(serializers.ModelSerializer):   
    registered_drivers = DriverNameListField()
    
    
    class Meta:
        model = Race
        fields = ['id','race_track_name', 'track_location', 'race_date','registration_closure_date','registered_drivers'
        ]
   
#When using ModelSerializer, need to add Meta cls with model name & fields
#Here, use  'serializers.Serializer' , as taking a list of names

#Serializers - To pass driver IDs, race IDs in POST data      
class AddDriversToRaceSerializer1(serializers.Serializer):      
    drivers= serializers.PrimaryKeyRelatedField(many= True, queryset= Driver.objects.all()) 


#To accept names as i/p - resolve them to actual model instances
class AddDriversToRaceSerializer2(serializers.Serializer):      #Using driver names
    drivers= serializers.ListField(child= serializers.CharField())

    def validate_drivers(self, value):
        driver_objs= []
        existing_drivers= []         # already_registered
        race= self.context.get('race')     #race s/d b passed via Serializer context

        for name in value:
            try:
                first_name, last_name= name.split(' ',1)    #Assume first_name + last_name is unique
                driver= Driver.objects.get(first_name= first_name, last_name= last_name)

                if race and driver in race.registered_drivers.all():
                    existing_drivers.append(name)
                else:
                    driver_objs.append(driver)

            except(Driver.DoesNotExist, ValueError):
                raise serializers.ValidationError( f"Driver '{name}' not found or invalid format : Use 'first last'")

        if existing_drivers:
            raise serializers.ValidationError( f" Driver(s) {', '.join(existing_drivers)} already registered for the race !")
        else:
            return driver_objs
'''
#Allow only valid drivers in .save()
    def save(self, **kwargs):
        race= self.context.get('race')
        drivers= self.validated_data['drivers']
        race.drivers.add(*drivers)
        return race
'''

