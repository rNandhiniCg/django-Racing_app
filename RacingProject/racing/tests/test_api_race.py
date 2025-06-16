
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import date
from racing.models import Race, Driver, Team
from django.core.files.uploadedfile import SimpleUploadedFile
import tempfile
from PIL import Image

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from racing.models import Race, Driver




class RaceAPITestCase(APITestCase):

    def generate_logo(self):
        image = Image.new('RGB', (100, 100))
        tmp_file = tempfile.NamedTemporaryFile(suffix='.png')
        image.save(tmp_file, format='PNG')
        tmp_file.seek(0)
        return SimpleUploadedFile("logo.png", tmp_file.read(), content_type='image/png')

    def setUp(self):
        self.team = Team.objects.create(
            name="Red Bull Racing",
            location="Milton Keynes",
            logo=self.generate_logo(),
            description="F1 team"
        )
        self.driver = Driver.objects.create(
            first_name="Max",
            last_name="Verstappen",
            dob="1997-09-30",
            team=self.team
        )
        self.race_data = {
            "race_track_name": "Test Track",
            "track_location": "Test Location",
            "race_date": "2025-12-31",
            "registration_closure_date": "2025-12-01",
            "registered_drivers": [f"{self.driver.first_name} {self.driver.last_name}"]
        }
        self.race = Race.objects.create(
            race_track_name="Test Track",
            track_location="Test Location",
            race_date="2025-12-31",
            registration_closure_date="2025-12-01"
        )
        self.race.registered_drivers.add(self.driver)

    def test_list_races(self):
        url = reverse('race-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_race(self):
        url = reverse('race-create')
        data = {
            "race_track_name": "New Track",
            "track_location": "New Location",
            "race_date": "2025-11-15",
            "registration_closure_date": None,
            "registered_drivers": [f"{self.driver.first_name} {self.driver.last_name}"]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_retrieve_race(self):
        url = reverse('race-detail', args=[self.race.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_race(self):
        url = reverse('race-update', args=[self.race.id])
        updated_data = {
            'race_track_name': 'Updated Track',
            'track_location': 'Updated Location',
            'race_date': '2025-10-20',
            'registration_closure_date': None,
            'registered_drivers': [f"{self.driver.first_name} {self.driver.last_name}"]
        }
        response = self.client.put(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['race_track_name'], 'Updated Track')

    def test_delete_race_with_registered_drivers(self):
        driver = Driver.objects.create(
            first_name="Test",
            last_name="Driver",
            dob=date(2000, 1, 1)  # Ensure this passes your `validate_dob`
        )
        self.race.registered_drivers.add(driver)

        response = self.client.delete(reverse("race-delete", args=[self.race.id]))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Cannot delete race", response.data["error"])


    def test_create_race_with_invalid_date(self):
        url = reverse('race-create')
        invalid_data = self.race_data.copy()
        invalid_data['race_date'] = "2020-01-01"  # Past date
        response = self.client.post(url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('race_date', response.data)

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from racing.models import Race, Driver
from datetime import date

class AddDriversToRaceAPITests(APITestCase):
    def setUp(self):
        self.race = Race.objects.create(race_track_name="Monaco GP", race_date="2025-06-15", track_location= "Race location")
        self.driver1 = Driver.objects.create(first_name="Charles", last_name="Leclerc", dob="1997-10-16")
        self.driver2 = Driver.objects.create(first_name="Carlos", last_name="Sainz", dob="1994-09-01")
        self.url = reverse('add-drivers-to-race', args=[self.race.id])

    def test_add_valid_drivers_to_race(self):
        data = {'drivers': [self.driver1.id, self.driver2.id]}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.driver1, self.race.registered_drivers.all())
        self.assertIn(self.driver2, self.race.registered_drivers.all())

    def test_add_invalid_driver_id(self):
        data = {'drivers': [999]}  # Non-existent driver ID
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('drivers', response.data)

    def test_add_drivers_to_nonexistent_race(self):
        url = reverse('add-drivers-to-race', args=[999])  # Non-existent race
        data = {'drivers': [self.driver1.id]}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class RaceDeleteViewAPITests(APITestCase):
    def setUp(self):
        self.race = Race.objects.create(race_track_name="Monaco GP", race_date="2025-06-15", track_location= "Race location")
        self.driver = Driver.objects.create(
            first_name="George",
            last_name="Russell",
            dob="1998-02-15"
        )
        self.race.registered_drivers.add(self.driver)
        self.url = reverse('race-delete', args=[self.race.id])  # Ensure this name matches your urls.py

    def test_delete_race_with_registered_drivers_returns_400(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "Cannot delete race with registered drivers.")