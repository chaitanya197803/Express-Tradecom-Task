from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from users.models.user_model import User
from users.services.user_service import UserService, UserValidationError, UserNotFoundError

class UserAPITestCase(TestCase):
    def setUp(self):
        self.user_data_1 = {
            "name": "John Doe",
            "email": "john@example.com",
            "role": "Admin"
        }
        self.user_data_2 = {
            "name": "Jane Smith",
            "email": "jane@example.com",
            "role": "User"
        }
        self.user1 = User.objects.create(**self.user_data_1)
        self.list_create_url = reverse('user-list-create')

    # --- Test Service Layer ---

    def test_service_create_user_success(self):
        data = {
            "name": "Bob Vance",
            "email": "bob@vancerefrigeration.com",
            "role": "Sales"
        }
        user = UserService.create_user(data)
        self.assertEqual(user.name, "Bob Vance")
        self.assertEqual(user.email, "bob@vancerefrigeration.com")
        self.assertEqual(user.role, "Sales")

    def test_service_create_user_duplicate_email(self):
        data = {
            "name": "John Clone",
            "email": "john@example.com",
            "role": "Admin"
        }
        with self.assertRaises(UserValidationError) as context:
            UserService.create_user(data)
        self.assertEqual(context.exception.status_code, 409)
        self.assertEqual(context.exception.message, "Email already exists")

    def test_service_create_user_invalid_email(self):
        data = {
            "name": "John Invalid",
            "email": "not-an-email",
            "role": "Admin"
        }
        with self.assertRaises(UserValidationError) as context:
            UserService.create_user(data)
        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.message, "Invalid email format")

    def test_service_create_user_missing_fields(self):
        data = {
            "name": "John Missing",
            "email": "missing@example.com"
            # role is missing
        }
        with self.assertRaises(UserValidationError) as context:
            UserService.create_user(data)
        self.assertEqual(context.exception.status_code, 400)

    def test_service_get_user_by_id_success(self):
        user = UserService.get_user_by_id(self.user1.id)
        self.assertEqual(user.email, self.user1.email)

    def test_service_get_user_by_id_not_found(self):
        with self.assertRaises(UserNotFoundError) as context:
            UserService.get_user_by_id(9999)
        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.message, "User not found")

    # --- Test API Views / Endpoints ---

    def test_get_all_users_api_no_pagination(self):
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['data'][0]['email'], self.user1.email)

    def test_create_user_api_success(self):
        data = {
            "name": "Alice Cooper",
            "email": "alice@cooper.com",
            "role": "Singer"
        }
        response = self.client.post(self.list_create_url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['message'], "User created successfully")
        self.assertEqual(response.data['data']['name'], "Alice Cooper")

    def test_create_user_api_duplicate_email(self):
        data = {
            "name": "John Doe Duplicate",
            "email": "john@example.com",
            "role": "Admin"
        }
        response = self.client.post(self.list_create_url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['error'], "Email already exists")

    def test_create_user_api_invalid_email(self):
        data = {
            "name": "Bad Email User",
            "email": "bademail@",
            "role": "User"
        }
        response = self.client.post(self.list_create_url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['error'], "Invalid email format")

    def test_get_user_by_id_api_success(self):
        url = reverse('user-detail', args=[self.user1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['email'], self.user1.email)

    def test_get_user_by_id_api_not_found(self):
        url = reverse('user-detail', args=[9999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['error'], "User not found")

    def test_search_users_api(self):
        # Create user 2
        User.objects.create(**self.user_data_2)

        # Search matching 'john' (case-insensitive name)
        response = self.client.get(f"{self.list_create_url}?search=john")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['name'], "John Doe")

        # Search matching 'jane' (case-insensitive name)
        response = self.client.get(f"{self.list_create_url}?search=jane")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['name'], "Jane Smith")

        # Search matching 'example' (matching all emails)
        response = self.client.get(f"{self.list_create_url}?search=example")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 2)

    def test_pagination_api(self):
        # Create 15 additional users to test pagination
        for i in range(15):
            User.objects.create(
                name=f"User {i}",
                email=f"user{i}@example.com",
                role="User"
            )

        # Total count = 1 (from setUp) + 15 = 16
        # Get page=1, limit=5
        response = self.client.get(f"{self.list_create_url}?page=1&limit=5")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['page'], 1)
        self.assertEqual(response.data['limit'], 5)
        self.assertEqual(response.data['total_records'], 16)
        self.assertEqual(response.data['total_pages'], 4)
        self.assertEqual(len(response.data['data']), 5)

        # Get page=4, limit=5 (last page should have 1 record)
        response = self.client.get(f"{self.list_create_url}?page=4&limit=5")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
