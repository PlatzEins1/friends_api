import time
from collections import OrderedDict

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import User, FriendRequest
from rest_framework.response import Response

class UserAPIViewTestCase(APITestCase):
    def test_create_user(self):
        url = 'http://127.0.0.1:8000/api/users/'
        response = self.client.post(url, {"username": "user_create_test"})
        expected = {'id': 1, 'username': 'user_create_test'}
        self.assertEqual(response.data, expected)

class CreateFriendRequest(APITestCase):
    def setUp(self):
        self.User1 = User.objects.create(id=1, username='User1')
        self.User2 = User.objects.create(id=2, username='User2')

    def test_create_friend_request(self):
        url = reverse('create_friend_request')
        friend_request = {
            'from_user': self.User1.pk,
            'to_user': self.User2.pk,
        }
        response = self.client.post(url, friend_request)
        expected = {
            'id': 1,
            'from_user': OrderedDict([('id', 1), ('username', 'User1')]),
            'to_user': OrderedDict([('id', 2), ('username', 'User2')]),
            'accepted': False,
            'discarded': False
        }
        self.assertEqual(response.data, expected)

class AcceptFriendRequest(APITestCase):
    def setUp(self):
        self.User1 = User.objects.create(id=1, username='User1')
        self.User2 = User.objects.create(id=2, username='User2')
        friend_request = FriendRequest.objects.create(
            id=1,
            from_user_id=1,
            to_user_id=2,
            accepted=False,
            discarded=False
        )
        friend_request.save()
        self.friend_request = friend_request
    def test_accept(self):
        url = 'http://127.0.0.1:8000/api/manipulate_friend_request/1/'
        response = self.client.patch(url, {'accepted': 1})
        expected = {
            'id': 1,
            'from_user': OrderedDict([('id', 1), ('username', 'User1')]),
            'to_user': OrderedDict([('id', 2), ('username', 'User2')]),
            'accepted': 1,
            'discarded': 0
        }
        self.assertEqual(response.data, expected)


class ListFriendRequest(APITestCase):
    def setUp(self):
        self.User1 = User.objects.create(id=1, username='User1')
        self.User2 = User.objects.create(id=2, username='User2')
        self.User3 = User.objects.create(id=3, username='User3')

        friend_request1 = FriendRequest.objects.create(
            id=1,
            from_user_id=1,
            to_user_id=2,
            accepted=False,
            discarded=False
        )
        friend_request1.save()
        self.friend_request1 = friend_request1

        friend_request2 = FriendRequest.objects.create(
            id=2,
            from_user_id=3,
            to_user_id=1,
            accepted=True,
            discarded=False
        )
        friend_request2.save()
        self.friend_request2 = friend_request2
    def test_list(self):
        url = 'http://127.0.0.1:8000/api/friend_requests_list/1/'
        response = self.client.get(url)
        expected = [
            OrderedDict(
                [('id', 1),('from_user', OrderedDict([('id', 1), ('username', 'User1')])), ('to_user', OrderedDict([('id', 2), ('username', 'User2')])), ('accepted', False), ('discarded', False)])]
        self.assertEqual(response.data, expected)

    def test_status(self):
        url= 'http://127.0.0.1:8000/api/check_if_friends/1/2/'
        response = self.client.get(url)
        expected={'status': 'friend request sent by you'}
        self.assertEqual(response.data, expected)

        url = 'http://127.0.0.1:8000/api/check_if_friends/1/3/'
        response = self.client.get(url)
        expected = {'status': 'are friends'}
        self.assertEqual(response.data, expected)\

    def test_friends_list(self):
        url = 'http://127.0.0.1:8000/api/friend_list/1/'
        response = self.client.get(url)
        expected = {'friend_ids': [3]}
        self.assertEqual(response.data, expected)

    def test_delete_friend(self):
        url = 'http://127.0.0.1:8000/api/delete_friend/1/3/'
        response = self.client.delete(url)
        expected = {'success': 'friend deleted'}
        self.assertEqual(response.data, expected)

        url = 'http://127.0.0.1:8000/api/delete_friend/1/2/'
        response = self.client.delete(url)
        expected = {'error': 'these users are not friends'}
        self.assertEqual(response.data, expected)