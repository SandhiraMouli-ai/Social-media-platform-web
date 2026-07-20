from django.test import TestCase
from django.contrib.auth.models import User
from core.models import Profile, Post, Comment, Message

class SocialUpTestCase(TestCase):
    def setUp(self):
        # Create users
        self.user1 = User.objects.create_user(username='test_alice', email='alice@test.com', password='password123')
        self.user2 = User.objects.create_user(username='test_bob', email='bob@test.com', password='password123')

    def test_profile_creation_on_signup(self):
        """Test that Profile is automatically created on user creation via signals."""
        self.assertIsNotNone(self.user1.profile)
        self.assertEqual(self.user1.profile.bio, '')
        self.assertEqual(self.user1.profile.user.username, 'test_alice')

    def test_follow_unfollow_system(self):
        """Test the follow and unfollow relationship logic."""
        profile1 = self.user1.profile
        profile2 = self.user2.profile
        
        # Initial state: not following
        self.assertFalse(profile1.is_following(profile2))
        self.assertFalse(profile2.is_following(profile1))
        
        # Follow
        profile1.follow(profile2)
        self.assertTrue(profile1.is_following(profile2))
        self.assertIn(profile1, profile2.followers.all())
        self.assertIn(profile2, profile1.following.all())
        
        # Unfollow
        profile1.unfollow(profile2)
        self.assertFalse(profile1.is_following(profile2))
        self.assertNotIn(profile1, profile2.followers.all())
        self.assertNotIn(profile2, profile1.following.all())

    def test_private_message_creation(self):
        """Test message creation between users."""
        message = Message.objects.create(
            sender=self.user1,
            recipient=self.user2,
            content="Hey Bob, did you see the new update?"
        )
        self.assertEqual(message.sender, self.user1)
        self.assertEqual(message.recipient, self.user2)
        self.assertEqual(message.content, "Hey Bob, did you see the new update?")
        self.assertFalse(message.is_read)
