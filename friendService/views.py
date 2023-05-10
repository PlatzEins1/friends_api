from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import User, FriendRequest
from .serializers import UserSerializer, FriendRequestSerializer
from rest_framework.decorators import api_view
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample


@extend_schema_view(
    create=extend_schema(
        summary='create user with a specified username',
        responses={
            status.HTTP_200_OK: UserSerializer,
        }
    )
)
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        username = request.data.get('username')
        if not username:
            return Response({'error': 'No username provided'}, status=status.HTTP_400_BAD_REQUEST)
        user = User(username=username)
        user.save()
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@extend_schema(
    summary="create friend request between two users",
    responses={
        201: {
            'description': 'request sent',
            'example':{
                "id": 4,
                "from_user":{
                "id": 4,
                "username": "test_user1"
                },
                "to_user":{
                "id": 5,
                "username": "test_user2"
                },
                "accepted": False,
                "discarded": False
            }
        },
        400:{
            'description': 'request errors will be specified in response',
            'example': {
                'error': 'Both from_user and to_user are required'
            }
        },
    },
    examples=[
        OpenApiExample(
            name = 'Send request',
            value=[
                {'fortnite': 'lord', }
            ]
        )
    ],
)
@api_view(['POST'])
def create_friend_request(request):
    from_user_id = request.data.get('from_user')
    to_user_id = request.data.get('to_user')
    if not from_user_id or not to_user_id:
        return Response({'error': 'Both from_user and to_user are required'}, status=status.HTTP_400_BAD_REQUEST)

    if from_user_id == to_user_id:
        return Response({'error': 'Cannot send friend request to yourself'}, status=status.HTTP_400_BAD_REQUEST)

    from_user = User.objects.get(pk=from_user_id)
    to_user = User.objects.get(pk=to_user_id)
    if FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
        return Response({'error': 'Friend request already sent'}, status=status.HTTP_400_BAD_REQUEST)

    # this code check is there rever request and if so, sets the accepted status of the opposing request to True
    if FriendRequest.objects.filter(Q(from_user=to_user) & Q(to_user=from_user)).exists():
        opposing_request = FriendRequest.objects.get(Q(from_user=to_user) & Q(to_user=from_user))
        opposing_request.accepted = True
        opposing_request.save()
        serializer = FriendRequestSerializer(opposing_request)
        return Response(serializer.data)

    friend_request = FriendRequest(from_user=from_user, to_user=to_user)
    friend_request.save()
    serializer = FriendRequestSerializer(friend_request)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(

    summary='list of friend requests of a user with specified id which was nor accepted nor discraded',
    responses={
        200: {
            'description': 'list of requests',
            'example':{
                "id": 4,
                "from_user":{
                "id": 4,
                "username": "test_user1"
                },
                "to_user":{
                "id": 5,
                "username": "test_user2"
                },
                "accepted": False,
                "discarded": False
            }
        },
    },

)
@api_view(['GET'])
def friend_requests_list(request, user_id):
    # user_id = request.user.pk #while there is no auth system, we assume user_id as 1

    query_set = FriendRequest.objects.filter(Q(Q(to_user_id=user_id) | Q(from_user_id=user_id)) & Q(Q(accepted=False)&Q(discarded=False)))
    serializer = FriendRequestSerializer(query_set, many=True)
    return Response(serializer.data)


@extend_schema(
    summary='accept or decline friend request',
    examples=[

        OpenApiExample(
            'Example of accept',
            value={
                'accepted': True
            }
        ),
        OpenApiExample(
            'Example of discard',
            value={
                'discarded': True
            }
        ),
    ],
    responses={
        206: {
            'description': 'request sent',
            'example':
                {
                    "id": 3,
                    "from_user":{
                    "id": 2,
                    "username": "test_user_2"
                    },
                    "to_user":{
                    "id": 1,
                    "username": "test_user_1"
                    },
                    "accepted": False,
                    "discarded": True
                }
        },
        400: {
            'description': 'request errors will be specified in response',
            'example': {
                'error': 'Cannot accept and discard invite at the same time'
            }
        }
    }
)
@api_view(['PATCH'])
def manipulate_friend_request(request, request_id):
    accepted = request.data.get('accepted')
    discarded = request.data.get('discarded')
    updated_friendship_request = FriendRequest.objects.get(pk=request_id)
    if accepted:
        updated_friendship_request.accepted = True
    if discarded:
        updated_friendship_request.discarded = True
    updated_friendship_request.save()
    serializer = FriendRequestSerializer(updated_friendship_request)

    return Response(serializer.data, status=status.HTTP_206_PARTIAL_CONTENT)


@extend_schema(
    summary='list of current user s friends',
    responses={200:{
           'description': 'list of friends ids',
           'example': {
                'friend_ids': [1, 2]
           }
       }
   }
)
@api_view(['GET'])
def friends_list(request, user_id):
    # user_id = request.user.pk #while there is no auth system, we assume user_id as 1

    query_text = f'''
            SELECT from_user_id as id
              FROM friendService_friendrequest
             WHERE to_user_id = {user_id} AND 
                   accepted = True AND
                   discarded = FALSE
            UNION
            SELECT to_user_id as id
              FROM friendService_friendrequest
             WHERE from_user_id = {user_id} AND 
                  accepted = True AND
                   discarded = FALSE;


            '''
    query_set = FriendRequest.objects.raw(query_text)
    friends = {'friend_ids': []}
    for item in list(query_set):
        friends['friend_ids'].append(item.id)

    return Response(friends)


@extend_schema(
    summary="checks friend status between current user and url-param user",
    responses={200:{
               'description': 'status of friendship',
               'example': {
                    'status': "friend request sent by you"
               }
           }
       }
    )
@api_view(['GET'])
def check_if_friends(request, user_1, user_2):
    # user_id = request.user.pk #while there is no auth system, we assume user_id as 1

    friend_request = FriendRequest.objects.get(
        Q(
            Q(from_user_id=user_1) & Q(to_user_id=user_2) |
            Q(from_user_id=user_2) & Q(to_user_id=user_1))

    )
    if not friend_request:
        return Response({'status': 'no friendship'}, status=status.HTTP_200_OK)
    if friend_request.discarded:
        return Response({'status': 'friend request discarded'}, status=status.HTTP_200_OK)
    if friend_request.accepted:
        return Response({'status': 'are friends'}, status=status.HTTP_200_OK)
    if friend_request.from_user.pk == user_1:
        return Response({'status': 'friend request sent by you'}, status=status.HTTP_200_OK)
    if friend_request.to_user.pk == user_1:
        return Response({'status': 'friend request sent to you'}, status=status.HTTP_200_OK)


@extend_schema(
    summary='Delete friend of a authenticated user',
    responses={
        200: {
        'description': 'Success',
        'example': {
                "success": "friend deleted"
            }
        },
        400: {
            'description': 'Bad request',
            'example': {
                'error': 'these users are not friends'
            }
        },
    }

)
@api_view(['DELETE'])
def delete_friend(request, user_1, user_2):
    # user_id = request.user.pk #while there is no auth system, we assume user_id as 1

    friend_request = FriendRequest.objects.filter(
        Q(
        Q(
            Q(from_user_id=user_1) & Q(to_user_id=user_2) |
            Q(from_user_id=user_2) & Q(to_user_id=user_1))
    ) & Q(
        Q(accepted=True) & Q(discarded=False)
    ))
    if friend_request:
        friend_request.delete()
        return Response({'success': 'friend deleted'}, status=status.HTTP_200_OK)
    return Response({'error': 'these users are not friends'}, status=status.HTTP_400_BAD_REQUEST)
