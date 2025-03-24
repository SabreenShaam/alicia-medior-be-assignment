from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import URL
from .exceptions import URLValidationError, ShortCodeExistsError, ShortCodeNotFoundError
import string


class URLModelTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.admin_user = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='adminpassword',
            is_staff=True
        )

        # Create some test URLs
        self.public_url = URL.objects.create(
            long_url='https://example.com/public',
            short_code='public',
            user=self.user,
            is_private=False
        )

        self.private_url = URL.objects.create(
            long_url='https://example.com/private',
            short_code='private',
            user=self.user,
            is_private=True
        )

        self.anon_url = URL.objects.create(
            long_url='https://example.com/anon',
            short_code='anon',
            user=None,
            is_private=False
        )

    # Test the short code generation method
    def test_generate_short_code(self):
        long_url = 'https://example.com/anon'
        short_code = URL.generate_short_code()
        self.assertEqual(len(short_code), 6)
        self.assertTrue(all(c in string.ascii_letters + string.digits for c in short_code))

        # Test with custom length
        short_code = URL.generate_short_code(length=10)
        self.assertEqual(len(short_code), 10)

    # Test creating a short URL without a user
    def test_create_short_url_basic(self):
        url_obj = URL.create_short_url('https://example.com/test')
        self.assertIsNotNone(url_obj)
        self.assertEqual(url_obj.long_url, 'https://example.com/test')
        self.assertIsNone(url_obj.user)
        self.assertFalse(url_obj.is_private)

    # Test creating a short URL with a user
    def test_create_short_url_with_user(self):
        url_obj = URL.create_short_url('https://example.com/usertest', user=self.user)
        self.assertIsNotNone(url_obj)
        self.assertEqual(url_obj.long_url, 'https://example.com/usertest')
        self.assertEqual(url_obj.user, self.user)
        self.assertFalse(url_obj.is_private)

    # Test creating a short URL with a custom code
    def test_create_short_url_with_custom_code(self):
        url_obj = URL.create_short_url(
            'https://example.com/customtest',
            user=self.user,
            custom_code='custom'
        )
        self.assertIsNotNone(url_obj)
        self.assertEqual(url_obj.short_code, 'custom')

    # Test that creating a URL with an existing custom code raises an error
    def test_create_short_url_duplicate_custom_code(self):
        with self.assertRaises(ShortCodeExistsError):
            URL.create_short_url(
                'https://example.com/duplicate',
                custom_code='public'  # This code already exists
            )

    # Test creating a private URL
    def test_create_private_url(self):
        url_obj = URL.create_short_url(
            'https://example.com/privatetest',
            user=self.user,
            is_private=True
        )
        self.assertIsNotNone(url_obj)
        self.assertTrue(url_obj.is_private)

    # Test that invalid URLs raise an error
    def test_invalid_url_validation(self):
        with self.assertRaises(URLValidationError):
            URL.create_short_url('not-a-valid-url')

    # Test that trying to create an existing URL returns the existing object
    def test_existing_url_reuse(self):
        # For a user with their own URL
        url_obj = URL.create_short_url('https://example.com/public', user=self.user)
        self.assertEqual(url_obj.id, self.public_url.id)

        # For anonymous with a public URL
        url_obj = URL.create_short_url('https://example.com/anon')
        self.assertEqual(url_obj.id, self.anon_url.id)


class URLAPITestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()

        # Create test users
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )

        self.another_user = User.objects.create_user(
            username='anotheruser',
            email='another@example.com',
            password='anotherpassword'
        )

        self.admin_user = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='adminpassword',
            is_staff=True
        )

        # Create some test URLs
        self.public_url = URL.objects.create(
            long_url='https://example.com/public',
            short_code='public',
            user=self.user,
            is_private=False
        )

        self.private_url = URL.objects.create(
            long_url='https://example.com/private',
            short_code='private',
            user=self.user,
            is_private=True
        )

        self.anon_url = URL.objects.create(
            long_url='https://example.com/anon',
            short_code='anon',
            user=None,
            is_private=False
        )

    # Test creating a URL as an anonymous user
    def test_create_url_anonymous(self):
        data = {
            'long_url': 'https://example.com/newanon'
        }
        response = self.client.post(reverse('url-list-create'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(response.data['is_private'])

        # Try to create a private URL as anonymous (should fail)
        data = {
            'long_url': 'https://example.com/newanon2',
            'is_private': True
        }
        response = self.client.post(reverse('url-list-create'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Test creating a URL as an authenticated user
    def test_create_url_authenticated(self):
        self.client.force_authenticate(user=self.user)

        # Create a public URL
        data = {
            'long_url': 'https://example.com/newuser'
        }
        response = self.client.post(reverse('url-list-create'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(response.data['is_private'])

        # Create a private URL
        data = {
            'long_url': 'https://example.com/newprivate',
            'is_private': True
        }
        response = self.client.post(reverse('url-list-create'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['is_private'])

    # Test creating a URL with a custom code
    def test_create_url_with_custom_code(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'long_url': 'https://example.com/customcode',
            'custom_code': 'mycode'
        }
        response = self.client.post(reverse('url-list-create'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('mycode', response.data['short_url'])

        # Try to use an existing code
        data = {
            'long_url': 'https://example.com/duplicatecode',
            'custom_code': 'mycode'
        }
        response = self.client.post(reverse('url-list-create'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    # Test listing URLs as an anonymous user
    def test_list_urls_anonymous(self):
        response = self.client.get(reverse('url-list-create'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Anonymous users should only see public URLs
        self.assertEqual(len(response.data), 2)  # public_url and anon_url

        # Verify no private URLs are included
        short_codes = [item['short_url'].split('/')[-1] for item in response.data]
        self.assertIn('public', short_codes)
        self.assertIn('anon', short_codes)
        self.assertNotIn('private', short_codes)

    # Test listing URLs as an authenticated user
    def test_list_urls_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('url-list-create'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # User should see their own URLs (public and private) and other public URLs
        self.assertEqual(len(response.data), 3)  # public_url, private_url, and anon_url

        short_codes = [item['short_url'].split('/')[-1] for item in response.data]
        self.assertIn('public', short_codes)
        self.assertIn('private', short_codes)
        self.assertIn('anon', short_codes)

    # Test URL redirection
    def test_url_redirect(self):
        # Anonymous user redirecting public URL
        response = self.client.get(reverse('short-redirect', args=['public']), follow=False)
        self.assertEqual(response.status_code, status.HTTP_301_MOVED_PERMANENTLY)

        # Check that access count was incremented
        self.public_url.refresh_from_db()
        self.assertEqual(self.public_url.access_count, 1)

        # Anonymous user redirecting private URL (should fail)
        response = self.client.get(reverse('short-redirect', args=['private']), follow=False)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Owner redirecting private URL
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('short-redirect', args=['private']), follow=False)
        self.assertEqual(response.status_code, status.HTTP_301_MOVED_PERMANENTLY)

        # Check that access count was incremented
        self.private_url.refresh_from_db()
        self.assertEqual(self.private_url.access_count, 1)

    # Test URL statistics
    def test_url_stats(self):
        # Increment access counts
        self.public_url.access_count = 5
        self.public_url.save()

        self.private_url.access_count = 10
        self.private_url.save()

        # Anonymous user checking public URL stats
        response = self.client.get(reverse('stats', args=['public']))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['access_count'], 5)

        # Anonymous user checking private URL stats (should fail)
        response = self.client.get(reverse('stats', args=['private']))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Owner checking private URL stats
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('stats', args=['private']))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['access_count'], 10)
