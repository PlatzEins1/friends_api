from django.test import TestCase
from rest_framework import serializers
from friendService.models import User, FriendRequest
from friendService.serializers import UserSerializer, FriendRequestSerializer


class UserSerializerTestCase(TestCase):
    def test_user_serializer(self):
        user = User(username='User for api testing')
        serializer = UserSerializer(user)
        expected = {'id': None, 'username': 'User for api testing'}
        self.assertEqual(serializer.data, expected)

class FriendRequestSerializerTestCase(TestCase):
    def test_friend_request_serializer(self):
        from_user = User(id = 1, username = 'Test user 1')
        to_user = User(id = 2, username = 'Test user 2')
        friend_request = FriendRequest(id = 1, from_user=from_user, to_user=to_user, accepted=False, discarded=False)
        serializer = FriendRequestSerializer(friend_request)
        expected = {
            'id': 1,
            'from_user': {
                'id': 1,
                'username': 'Test user 1'
            },
            'to_user': {
                'id': 2,
                'username': 'Test user 2'
            },
            'accepted': False,
            'discarded': False,
        }
        self.assertEqual(serializer.data, expected)