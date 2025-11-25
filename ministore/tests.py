from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse


class ProfileViewTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(username='testuser', password='pass1234', email='test@example.com', first_name='Test', last_name='User')
		# profile should be auto-created by signals
		self.user.profile.phone_number = '0123456789'
		self.user.profile.address = '123 Test St'
		self.user.profile.save()

	def test_profile_view_shows_user_info_for_authenticated(self):
		self.client.login(username='testuser', password='pass1234')
		url = reverse('profile')
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 200)
		content = resp.content.decode()
		# ensure user info appears in rendered template
		self.assertIn('Test User', content)
		self.assertIn('@testuser', content)
		self.assertIn('test@example.com', content)
		self.assertIn('0123456789', content)
