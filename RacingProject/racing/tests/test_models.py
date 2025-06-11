import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from racing.models import validate_image_size, validate_dob
from django.utils import timezone
from racing.models import Team, Driver, Race
from datetime import date, timedelta

@pytest.mark.django_db
def test_team_creation():
    team = Team.objects.create(
        name="SpeedX",
        location="Berlin, Germany",
        logo="logos/speedx.png",
        description="Top racing team"
    )
    assert team.name == "SpeedX"
    assert team.logo.name.startswith("logos/")


def test_validate_image_size_exceeds_limit():
    large_image = SimpleUploadedFile("test.jpg", b"a" * (51 * 1024))    # 51KB
    with pytest.raises(ValidationError, match="Image size should not exceed 50KB."):
        validate_image_size(large_image)


@pytest.mark.django_db
def test_driver_dob_validation():
    with pytest.raises(ValidationError):
        driver = Driver(
            first_name="John",
            last_name="Doe",
            dob=date(2005, 1, 1)  # Invalid DOB
        )
        driver.full_clean()


@pytest.mark.django_db
def test_duplicate_driver_validation():
    team = Team.objects.create(name="SpeedX", location="Berlin", logo="logos/logo.png")
    Driver.objects.create(first_name="Max", last_name="Verstappen", dob=date(1995, 5, 5), team=team)
    with pytest.raises(ValidationError):
        duplicate_driver = Driver(first_name="Max", last_name="Verstappen", dob=date(1995, 5, 5), team=team)
        duplicate_driver.full_clean()


@pytest.mark.django_db
def test_driver_team_relationship():
    team = Team.objects.create(name="SpeedX", location="Berlin", logo="logos/logo.png")
    driver = Driver.objects.create(first_name="Max", last_name="Verstappen", dob=date(1995, 5, 5), team=team)
    assert driver.team == team
    assert team.drivers.count() == 1

@pytest.mark.django_db
def test_race_date_validation():
    with pytest.raises(ValidationError):
        race = Race(
            race_track_name="Silverstone",
            track_location="UK",
            race_date=date(2020, 1, 1)  # Past date
        )
        race.full_clean()


@pytest.mark.django_db
def test_registration_closure_date_validation():
    with pytest.raises(ValidationError):
        race = Race(
            race_track_name="Monaco GP",
            track_location="Monaco",
            race_date=timezone.now().date() + timedelta(days=10),
            registration_closure_date=timezone.now().date() + timedelta(days=15)    # Invalid
            )
        race.full_clean()


@pytest.mark.django_db
def test_race_driver_registration_and_delete_restriction():
    team = Team.objects.create(name="SpeedX", location="Berlin", logo="logos/logo.png")
    driver = Driver.objects.create(first_name="Lewis", last_name="Hamilton", dob=date(1985, 1, 7), team=team)
    race = Race.objects.create(
        race_track_name="Monaco GP",
        track_location="Monaco",
        race_date=timezone.now().date() + timedelta(days=10)
    )
    race.registered_drivers.add(driver)
    assert driver in race.registered_drivers.all()

    # Attempt to delete driver who is registered to a race
    with pytest.raises(Exception):
        driver.delete()

    # Attempt to delete team with a driver registered to a race
    with pytest.raises(Exception):
        team.delete()

    
    # Attempt to delete race with registered drivers
    with pytest.raises(ValidationError):
        race.delete()

@pytest.mark.django_db
def test_team_delete_without_registered_races():
    # Create a team
    team = Team.objects.create(
        name="Safe Delete Team",
        location="Testville",
        logo="logos/test_logo.png"
    )

    # Add a driver with no registered races
    Driver.objects.create(
        first_name="Alex",
        last_name="NoRace",
        dob="1990-01-01",
        team=team
    )

    # Attempt to delete the team (should succeed)
    team.delete()

    # Assert the team is deleted
    assert not Team.objects.filter(id=team.id).exists()

@pytest.mark.django_db
def test_driver_delete_without_registered_races():
    # Create a team
    team = Team.objects.create(
        name="Driverless Team",
        location="Nowhere",
        logo="logos/driverless_logo.png"
    )

    # Create a driver not registered to any races
    driver = Driver.objects.create(
        first_name="Chris",
        last_name="Free",
        dob="1992-03-03",
        team=team
    )

    # Attempt to delete the driver (should succeed)
    driver.delete()

    # Assert the driver is deleted
    assert not Driver.objects.filter(id=driver.id).exists()

@pytest.mark.django_db
def test_race_delete_without_registered_drivers():
    # Create a race with no registered drivers
    race = Race.objects.create(
        race_track_name="Desert Rally",
        track_location="Sahara",
        race_date="2025-12-01",
        registration_closure_date="2025-11-01"
    )

    # Attempt to delete the race (should succeed)
    race.delete()

    # Assert the race is deleted
    assert not Race.objects.filter(id=race.id).exists()

@pytest.mark.django_db
def test_team_str():
    team = Team.objects.create(
        name="Speed Demons",
        location="Fastville",
        logo="logos/speed_demons.png"
    )
    assert str(team) == "Speed Demons"

@pytest.mark.django_db
def test_driver_str():
    driver = Driver.objects.create(
        first_name="Lewis",
        last_name="Hamilton",
        dob="1985-01-07"
    )
    assert str(driver) == "Lewis Hamilton"

from racing.models import Race

@pytest.mark.django_db
def test_race_str():
    race = Race.objects.create(
        race_track_name="Monaco Grand Prix",
        track_location="Monaco",
        race_date="2025-06-01"
    )
    assert str(race) == "Monaco Grand Prix"


