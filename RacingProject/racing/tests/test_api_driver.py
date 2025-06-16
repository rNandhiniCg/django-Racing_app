
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import date
from racing.models import Driver, Team
from django.core.files.uploadedfile import SimpleUploadedFile
import tempfile
from PIL import Image

class DriverAPITestCase(APITestCase):

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
        self.driver_data = {
            "first_name": "Max",
            "last_name": "Verstappen",
            "dob": "1997-09-30",
            "team": self.team.name  # Use name for API requests
        }

    def test_create_driver(self):
        url = reverse('driver-create')
        response = self.client.post(url, self.driver_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_drivers(self):
        Driver.objects.create(
            first_name="Max",
            last_name="Verstappen",
            dob="1997-09-30",
            team=self.team  # Use instance for model creation
        )
        url = reverse('driver-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_retrieve_driver(self):
        driver = Driver.objects.create(
            first_name="Max",
            last_name="Verstappen",
            dob="1997-09-30",
            team=self.team  # Use instance for model creation
        )
        url = reverse('driver-detail', args=[driver.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], "Max")

    def test_update_driver(self):
        driver = Driver.objects.create(
            first_name="Max",
            last_name="Verstappen",
            dob="1997-09-30",
            team=self.team  # Use instance for model creation
        )
        url = reverse('driver-update', args=[driver.id])
        updated_data = {
            "first_name": "Lewis",
            "last_name": "Hamilton",
            "dob": "1985-01-07",
            "team": self.team.name  # Use name for API requests
        }
        response = self.client.put(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], "Lewis")

    def test_delete_driver(self):
        driver = Driver.objects.create(
            first_name="Max",
            last_name="Verstappen",
            dob="1997-09-30",
            team=self.team  # Use instance for model creation
        )
        url = reverse('driver-delete', args=[driver.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_create_driver_with_invalid_dob(self):
        invalid_data = self.driver_data.copy()
        invalid_data['dob'] = "2025-01-01"  # Future date
        url = reverse('driver-create')
        response = self.client.post(url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('dob', response.data)
