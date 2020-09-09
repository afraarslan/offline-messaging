from rest_framework import response, decorators, permissions, status
from authentication.models import UserBlacklist
from user_logging.serializers import UserLogSerializer
from .models import UserMessage
from .serializers import UserMessageSerializer
from django.contrib.auth.models import User


class IsOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


def response_validation_error(error):
    return response.Response(error, status.HTTP_400_BAD_REQUEST)


def response_created(data):
    return response.Response(data, status.HTTP_201_CREATED)


@decorators.api_view(["GET"])
@decorators.permission_classes([IsOwner, ])
def get_inbox_messages(request):
    user = request.user
    msgbox = UserMessage.objects.filter(to_user=user)
    serializer = UserMessageSerializer(msgbox, many=True)

    log = {
        'user': user.id,
        'action': "get_inbox"
    }
    log_serializer = UserLogSerializer(data=log)
    if not log_serializer.is_valid():
        return response_validation_error(log_serializer.errors)
    log_serializer.save()

    return response_created(serializer.data)


@decorators.api_view(["GET"])
@decorators.permission_classes([IsOwner, ])
def get_outbox_messages(request):
    user = request.user
    msgbox = UserMessage.objects.filter(from_user=user)
    serializer = UserMessageSerializer(msgbox, many=True)

    log = {
        'user': user.id,
        'action': "get_outbox"
    }
    log_serializer = UserLogSerializer(data=log)
    if not log_serializer.is_valid():
        return response_validation_error(log_serializer.errors)
    log_serializer.save()

    return response_created(serializer.data)


@decorators.api_view(["POST"])
@decorators.permission_classes([IsOwner, ])
def send_message(request):
    if request.method == 'POST':
        user = request.user

        to_user_id = request.POST.get('to_user_id')
        if not User.objects.filter(pk=to_user_id).exists():
            return response_validation_error({'to_user_id': ["not exists"]})

        if UserBlacklist.objects.filter(user=to_user_id, blocked_user=user.id).exists():
            return response_validation_error({'to_user_id': ["you are blocked. you cannot send a message"]})

        data = {
            'from_user': user.id,
            'to_user': to_user_id,
            'message': {
                'content': request.POST.get('text')
            }
        }
        user_msg_serializer = UserMessageSerializer(data=data)
        if not user_msg_serializer.is_valid():
            return response_validation_error(user_msg_serializer.errors)

        user_msg_serializer.save()

        log = {
            'user': user.id,
            'action': "send"
        }
        log_serializer = UserLogSerializer(data=log)
        if not log_serializer.is_valid():
            return response_validation_error(log_serializer.errors)
        log_serializer.save()

        return response_created({'userMessage'})