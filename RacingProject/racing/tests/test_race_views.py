import pytest
from django.urls import reverse
from datetime import date, timedelta
from racing.models import Race, Driver
from django.test import TestCase
from django.contrib.messages import get_messages



@pytest.fixture
def driver(db):
    return Driver.objects.create(
        first_name="Lewis",
        last_name="Hamilton",
        dob=date(1985, 1, 7)
    )

@pytest.fixture
def race(db):
    return Race.objects.create(
        race_track_name="Silverstone",
        track_location="UK",
        race_date=date.today() + timedelta(days=10),
        registration_closure_date=date.today() + timedelta(days=5)
    )

@pytest.mark.django_db
def test_race_list_view(client):
    url = reverse('race_list')
    response = client.get(url)
    assert response.status_code == 200
    assert 'races' in response.context

@pytest.mark.django_db
def test_race_create_view_get(client):
    url = reverse('race_create')
    response = client.get(url)
    assert response.status_code == 200
    assert 'form' in response.context

@pytest.mark.django_db
def test_race_create_view_post_valid(client):
    url = reverse('race_create')
    data = {
        'race_track_name': 'Monza',
        'track_location': 'Italy',
        'race_date': (date.today() + timedelta(days=15)).isoformat(),
        'registration_closure_date': (date.today() + timedelta(days=10)).isoformat()
    }
    response = client.post(url, data)
    assert response.status_code == 302
    assert Race.objects.filter(race_track_name='Monza').exists()

@pytest.mark.django_db
def test_race_edit_view_post_valid(client, race):
    url = reverse('race_edit', args=[race.pk])
    data = {
        'race_track_name': 'Updated Track',
        'track_location': 'Updated Location',
        'race_date': (date.today() + timedelta(days=20)).isoformat(),
        'registration_closure_date': (date.today() + timedelta(days=15)).isoformat()
    }
    response = client.post(url, data)
    assert response.status_code == 302
    race.refresh_from_db()
    assert race.race_track_name == 'Updated Track'

@pytest.mark.django_db
def test_race_delete_view_post(client, race):
    url = reverse('race_delete', args=[race.pk])
    response = client.post(url)
    assert response.status_code == 302
    assert not Race.objects.filter(pk=race.pk).exists()

@pytest.fixture
def driver(db):
    return Driver.objects.create(
        first_name="Charles",
        last_name="Leclerc",
        dob=date(1997, 10, 16)
    )

@pytest.fixture
def races(db):
    return [
        Race.objects.create(
            race_track_name=f"Track {i}",
            track_location="Location",
            race_date=date.today() + timedelta(days=10 + i),
            registration_closure_date=date.today() + timedelta(days=5 + i)
        )
        for i in range(2)
    ]

@pytest.mark.django_db
def test_register_driver_to_race_get(client, driver, races):
    url = reverse('register_driver_to_race', args=[driver.pk])
    response = client.get(url)
    assert response.status_code == 200
    assert 'form' in response.context
    assert 'driver' in response.context

@pytest.mark.django_db
def test_register_driver_to_race_post(client, driver, races):
    url = reverse('register_driver_to_race', args=[driver.pk])
    data = {
        'races': [race.pk for race in races]
    }
    response = client.post(url, data)
    assert response.status_code == 302  # Redirect to driver_list
    driver.refresh_from_db()
    assert set(driver.registered_races.all()) == set(races)

@pytest.fixture
def drivers(db):
    return [
        Driver.objects.create(
            first_name=f"Driver{i}",
            last_name="Test",
            dob=date(1990, 1, i + 1)
        )
        for i in range(2)
    ]

@pytest.fixture
def race(db):
    return Race.objects.create(
        race_track_name="Spa-Francorchamps",
        track_location="Belgium",
        race_date=date.today() + timedelta(days=10),
        registration_closure_date=date.today() + timedelta(days=5)
    )

@pytest.mark.django_db
def test_edit_race_drivers_get(client, race, drivers):
    url = reverse('edit_race_drivers', args=[race.pk])
    response = client.get(url)
    assert response.status_code == 200
    assert 'form' in response.context

@pytest.mark.django_db
def test_edit_race_drivers_post(client, race, drivers):
    url = reverse('edit_race_drivers', args=[race.pk])
    data = {
        'drivers': [driver.pk for driver in drivers]
    }
    response = client.post(url, data)
    assert response.status_code == 302  # Redirect to race_list
    race.refresh_from_db()
    assert set(race.registered_drivers.all()) == set(drivers)


class RaceDeleteViewTests(TestCase):
    def setUp(self):
        self.race = Race.objects.create(race_track_name="Monaco GP", race_date="2025-06-15", track_location= "Race location")
        self.url = reverse('race_delete', args=[self.race.id])  

    def test_delete_race_without_registered_drivers(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('race_list'))
        self.assertFalse(Race.objects.filter(id=self.race.id).exists())


    def test_delete_race_with_registered_driver(self):
        driver = Driver.objects.create(
            first_name="Pierre",
            last_name="Gasly",
            dob="1996-02-07"
        )
        driver.registered_races.add(self.race)

        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, reverse('race_list'))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Cannot delete Race" in str(m) for m in messages))
        self.assertTrue(Race.objects.filter(id=self.race.id).exists())
