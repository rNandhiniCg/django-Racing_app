import pytest
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from racing.models import Team, Driver, Race

from django.test import TestCase
from io import BytesIO
import os
from PIL import Image
from django.test import Client
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest


def generate_test_logo():
    image = Image.new('RGB', (100, 100), color='blue')
    buffer = BytesIO()
    image.save(buffer, format='PNG')
    buffer.seek(0)
    return SimpleUploadedFile('team_logo.png', buffer.read(), content_type='image/png')




def get_logo_file():
    path = os.path.join(os.path.dirname(__file__), 'assets', 'test_logo.png')
    with open(path, 'rb') as f:
        return SimpleUploadedFile('test_logo.png', f.read(), content_type='image/png')

@pytest.fixture
def logo_file():
    return SimpleUploadedFile("logo.png", b"file_content", content_type="image/png")

@pytest.fixture
def team(db, logo_file):
    return Team.objects.create(
        name="Test Team",
        location="Test City",
        logo=logo_file,
        description="A test team"
    )


@pytest.mark.django_db
def test_team_list_view(client):
    url = reverse('team_list')
    response = client.get(url)
    assert response.status_code == 200
    assert 'teams' in response.context


@pytest.mark.django_db
def test_team_create_view_get(client):
    url = reverse('team_create')
    response = client.get(url)
    assert response.status_code == 200
    assert 'form' in response.context



def test_team_edit_view_get(client, team):
    url = reverse('team_edit', args=[team.pk])
    response = client.get(url)
    assert response.status_code == 200
    assert 'form' in response.context


def test_team_delete_view_post(client, team):
    url = reverse('team_delete', args=[team.pk])
    response = client.post(url)
    assert response.status_code == 302
    assert not Team.objects.filter(pk=team.pk).exists()

@pytest.mark.django_db
def test_team_delete_with_registered_driver_raises_error(team):
    driver = Driver.objects.create(first_name="Test",last_name= "Driver" ,dob="1992-06-10", team=team)
    race = Race.objects.create(race_track_name="Test Race", race_date="2025-06-10", track_location="Test Track")

    driver.registered_races.add(race)

    with pytest.raises(ValidationError):
        team.delete()


class TeamViewTests(TestCase):
    def setUp(self):
        self.team = Team.objects.create(name="Mercedes", logo="logo.png")

    def test_team_edit_valid_post(self):
        data = {'name': 'Mercedes-AMG'}
        response = self.client.post(reverse('team_edit', args=[self.team.pk]), data)
        self.assertRedirects(response, reverse('team_list'))
        self.team.refresh_from_db()
        self.assertEqual(self.team.name, 'Mercedes-AMG')


class TeamViewTests(TestCase):
    def setUp(self):
        self.team = Team.objects.create(name="Ferrari", logo="logo.png")

    def test_team_create_invalid_post(self):
        response = self.client.post(reverse('team_create'), data={})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'team/team_form.html')
        self.assertContains(response, 'form')

    def test_team_edit_get(self):
        response = self.client.get(reverse('team_edit', args=[self.team.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'team/team_form.html')
        self.assertContains(response, 'form')

from django.test import TestCase
from django.urls import reverse
from racing.models import Team, Driver
from django.contrib.messages import get_messages

class TeamDeleteViewTests(TestCase):
    def setUp(self):
        self.team = Team.objects.create(name="AlphaTauri", logo="logo.png")

    def test_team_delete_get_calls_delete(self):
        response = self.client.get(reverse('team_delete', args=[self.team.pk]))
        self.assertRedirects(response, reverse('team_list'))
        self.assertFalse(Team.objects.filter(pk=self.team.pk).exists())

    def test_team_delete_successful_if_no_registered_races(self):
        team = Team.objects.create(name="Williams", logo="logo.png")
        Driver.objects.create(
            first_name="Alex",
            last_name="Albon",
            dob="1996-03-23",
            team=team
        )
        response = self.client.get(reverse('team_delete', args=[team.pk]))
        self.assertRedirects(response, reverse('team_list'))
        self.assertFalse(Team.objects.filter(pk=team.pk).exists())


class TeamDeleteViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.team = Team.objects.create(name="McLaren", logo="logo.png")

    def test_team_delete_blocked_if_driver_has_registered_races(self):
        driver = Driver.objects.create(
            first_name="Lando",
            last_name="Norris",
            dob="1999-11-13",
            team=self.team
        )
        # Create a mock race and assign it
        race = Race.objects.create( track_location="Test Track", race_track_name="Test GP", race_date="2025-07-01")
        driver.registered_races.add(race)

        response = self.client.get(reverse('team_delete', args=[self.team.pk]), follow=True)
        messages = list(get_messages(response.wsgi_request))
        print([str(m) for m in messages])  # Debug print
        self.assertTrue(any("Cannot delete Team" in str(m) for m in messages))

    

    





