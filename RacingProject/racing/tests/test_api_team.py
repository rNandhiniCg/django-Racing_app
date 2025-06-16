from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from racing.models import Team
import tempfile
from PIL import Image

class TeamAPITestCase(APITestCase):

    def generate_image_file(self, name='test_logo.png'):
        image = Image.new('RGB', (100, 100))
        tmp_file = tempfile.NamedTemporaryFile(suffix='.png')
        image.save(tmp_file, format='PNG')
        tmp_file.seek(0)
        return SimpleUploadedFile(name, tmp_file.read(), content_type='image/png')

    def setUp(self):
        self.team_data = {
            "name": "Chennai Super Kings",
            "location": "Chennai",
            "logo": self.generate_image_file(),
            "description": "A popular IPL team."
        }

    def test_create_team(self):
        url = reverse('team-create')  # Assuming you're using a router
        response = self.client.post(url, self.team_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Team.objects.count(), 1)

    def test_get_team_list(self):
        Team.objects.create(**self.team_data)
        url = reverse('team-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_get_team_detail(self):
        team = Team.objects.create(**self.team_data)
        url = reverse('team-detail', args=[team.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.team_data['name'])

    def test_update_team(self):
        team = Team.objects.create(**self.team_data)
        url = reverse('team-update', args=[team.id])
        updated_data = {
            "name": "Updated Team",
            "location": "Updated Location",
            "logo": self.generate_image_file(name='updated_logo.png'),
            "description": "Updated description"
        }
        response = self.client.put(url, updated_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Updated Team")

    def test_delete_team(self):
        team = Team.objects.create(**self.team_data)
        url = reverse('team-delete', args=[team.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Team.objects.count(), 0)

    def test_create_team_with_duplicate_name(self):
        Team.objects.create(**self.team_data)
        response = self.client.post(reverse('team-create'), self.team_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)

    def test_create_team_with_invalid_logo(self):
        invalid_logo = SimpleUploadedFile("file.txt", b"not an image", content_type="text/plain")
        self.team_data['logo'] = invalid_logo
        response = self.client.post(reverse('team-create'), self.team_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('logo', response.data)


