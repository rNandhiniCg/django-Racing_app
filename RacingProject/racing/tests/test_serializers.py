import pytest
from datetime import date, timedelta
from django.utils import timezone
from rest_framework.exceptions import ErrorDetail
from racing.models import Team, Driver, Race
from racing.serializers import (
    TeamSerializer,
    DriverSerializer,
    RaceSerializer,
    AddDriversToRaceSerializer2
)

from rest_framework.test import APITestCase
from rest_framework.exceptions import ValidationError
from datetime import date

@pytest.mark.django_db
def test_team_serializer():
    team = Team.objects.create(
        name="SpeedX",
        location="Berlin, Germany",
        logo="logos/speedx.png",
        description="Top racing team"
    )
    serializer = TeamSerializer(team)
    assert serializer.data['name'] == "SpeedX"
    assert 'drivers' in serializer.data

@pytest.mark.django_db
def test_driver_serializer_create():
    team = Team.objects.create(name="SpeedX", location="Berlin", logo="logos/logo.png")
    data = {
        'first_name': 'Max',
        'last_name': 'Verstappen',
        'dob': '1995-05-05',
        'team': 'SpeedX'
    }
    serializer = DriverSerializer(data=data)
    assert serializer.is_valid()
    driver = serializer.save()
    assert driver.team == team

@pytest.mark.django_db
def test_driver_serializer_update():
    team = Team.objects.create(name="SpeedX", location="Berlin", logo="logos/logo.png")
    driver = Driver.objects.create(first_name="Max", last_name="Verstappen", dob=date(1995, 5, 5), team=team)
    new_team = Team.objects.create(name="FastTrack", location="Munich", logo="logos/fasttrack.png")
    data = {
        'first_name': 'Max',
        'last_name': 'Verstappen',
        'dob': '1995-05-05',
        'team': 'FastTrack'
    }
    serializer = DriverSerializer(driver, data=data)
    assert serializer.is_valid()
    updated_driver = serializer.save()
    assert updated_driver.team == new_team

@pytest.mark.django_db
def test_race_serializer():
    team = Team.objects.create(name="SpeedX", location="Berlin", logo="logos/logo.png")
    driver = Driver.objects.create(first_name="Lewis", last_name="Hamilton", dob=date(1985, 1, 7), team=team)
    race = Race.objects.create(
        race_track_name="Monaco GP",
        track_location="Monaco",
        race_date=timezone.now().date() + timedelta(days=10)
    )
    race.registered_drivers.add(driver)
    serializer = RaceSerializer(race)
    assert serializer.data['race_track_name'] == "Monaco GP"
    assert 'registered_drivers' in serializer.data

@pytest.mark.django_db
def test_add_drivers_to_race_serializer_valid():
    team = Team.objects.create(name="SpeedX", location="Berlin", logo="logos/logo.png")
    driver1 = Driver.objects.create(first_name="Lewis", last_name="Hamilton", dob=date(1985, 1, 7), team=team)
    driver2 = Driver.objects.create(first_name="Max", last_name="Verstappen", dob=date(1995, 5, 5), team=team)
    race = Race.objects.create(
        race_track_name="Monaco GP",
        track_location="Monaco",
        race_date=timezone.now().date() + timedelta(days=10)
    )
    data = {'drivers': ['Lewis Hamilton', 'Max Verstappen']}
    serializer = AddDriversToRaceSerializer2(data=data, context={'race': race})
    assert serializer.is_valid()
    validated_drivers = serializer.validated_data['drivers']
    assert driver1 in validated_drivers
    assert driver2 in validated_drivers

@pytest.mark.django_db
def test_add_drivers_to_race_serializer_duplicate():
    team = Team.objects.create(name="SpeedX", location="Berlin", logo="logos/logo.png")
    driver1 = Driver.objects.create(first_name="Lewis", last_name="Hamilton", dob=date(1985, 1, 7), team=team)
    driver2 = Driver.objects.create(first_name="Max", last_name="Verstappen", dob=date(1995, 5, 5), team=team)
    race = Race.objects.create(
        race_track_name="Monaco GP",
        track_location="Monaco",
        race_date=timezone.now().date() + timedelta(days=10)
    )
    race.registered_drivers.add(driver1)
    data = {'drivers': ['Lewis Hamilton', 'Max Verstappen']}
    serializer = AddDriversToRaceSerializer2(data=data, context={'race': race})
    assert not serializer.is_valid()
    assert 'drivers' in serializer.errors
    assert "already registered" in str(serializer.errors['drivers'][0])



@pytest.mark.django_db
def test_driver_serializer_create_invalid_team():
    data = {
        'first_name': 'Charles',
        'last_name': 'Leclerc',
        'dob': '1997-10-16',
        'team': 'NonExistentTeam'
    }
    serializer = DriverSerializer(data=data)
    assert not serializer.is_valid()
    assert 'team' in serializer.errors
    assert serializer.errors['team'][0] == 'Team with this name does not exist.'

class DriverSerializerTest(APITestCase):
    def setUp(self):
        self.team = Team.objects.create(name="Red Bull Racing")

    def test_valid_driver_creation(self):
        data = {
            "first_name": "Max",
            "last_name": "Verstappen",
            "dob": "1997-09-30",
            "team": "Red Bull Racing",
            "registered_races": []
        }
        serializer = DriverSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        driver = serializer.save()
        self.assertEqual(driver.team.name, "Red Bull Racing")
        self.assertEqual(driver.first_name, "Max")

    def test_invalid_team_name(self):
        data = {
            "first_name": "Lewis",
            "last_name": "Hamilton",
            "dob": "1985-01-07",
            "team": "Unknown Team",
            "registered_races": []
        }
        serializer = DriverSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("team", serializer.errors)

