import pytest 
from django.urls import reverse 
from django.core.files.uploadedfile import SimpleUploadedFile 
from datetime import date, timedelta 
from racing.models import Driver, Team, Race 
from django.test import TestCase 
from django.utils import timezone 
from django.test import TestCase
from django.contrib.messages import get_messages

 

@pytest.fixture 

def team(db): 

    return Team.objects.create( 

        name="Test Team", 

        location="Test City", 

        logo=SimpleUploadedFile("logo.png", b"file_content", content_type="image/png"), 

        description="Test team description" 

    ) 

 

@pytest.fixture 

def driver(db, team): 

    return Driver.objects.create( 

        first_name="John", 

        last_name="Doe", 

        dob=date(2000, 1, 1), 

        team=team 

    ) 

 

@pytest.mark.django_db 

def test_driver_list_view(client): 

    url = reverse('driver_list') 

    response = client.get(url) 

    assert response.status_code == 200 

    assert 'drivers' in response.context 

 

@pytest.mark.django_db 

def test_driver_create_view_get(client): 

    url = reverse('driver_create') 

    response = client.get(url) 

    assert response.status_code == 200 

    assert 'form' in response.context 

 

@pytest.mark.django_db 

def test_driver_create_view_post_valid(client, team): 

    url = reverse('driver_create') 

    data = { 

        'first_name': 'Alice', 

        'last_name': 'Smith', 

        'dob': '1995-05-15', 

        'team': team.id 

    } 

    response = client.post(url, data) 

    assert response.status_code == 302 

    assert Driver.objects.filter(first_name='Alice').exists() 

 

@pytest.mark.django_db 

def test_driver_edit_view_post_valid(client, driver): 

    url = reverse('driver_edit', args=[driver.pk]) 

    data = { 

        'first_name': 'Jane', 

        'last_name': 'Doe', 

        'dob': '2000-01-01', 

        'team': driver.team.id 

    } 

    response = client.post(url, data) 

    assert response.status_code == 302 

    driver.refresh_from_db() 

    assert driver.first_name == 'Jane' 

 

@pytest.mark.django_db 

def test_driver_delete_view_post(client, driver): 

    url = reverse('driver_delete', args=[driver.pk]) 

    response = client.post(url) 

    assert response.status_code == 302 

    assert not Driver.objects.filter(pk=driver.pk).exists() 

class DriverDeleteViewTests(TestCase):
    def setUp(self):
        self.driver = Driver.objects.create(
            first_name="Fernando",
            last_name="Alonso",
            dob="1981-07-29"
        )
        self.url = reverse('driver_delete', args=[self.driver.id])  # Ensure this matches your urls.py

    def test_delete_driver_without_registered_races(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('driver_list'))
        self.assertFalse(Driver.objects.filter(id=self.driver.id).exists())

    def test_delete_driver_with_registered_races(self):
        race = Race.objects.create(race_track_name="Monaco GP", race_date="2025-06-15", track_location= "Race location")
        self.driver.registered_races.add(race)

        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, reverse('driver_list'))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Cannot delete Driver" in str(m) for m in messages))
        self.assertTrue(Driver.objects.filter(id=self.driver.id).exists())


 

 

