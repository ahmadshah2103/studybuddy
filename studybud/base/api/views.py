from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from base.models import Room
from .serializers import RoomSerializer


@api_view(['GET'])
def getRooms(request):
    rooms = Room.objects.all()
    serializer = RoomSerializer(rooms, many=True)
    return Response(serializer.data)


class RoomView(ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer


def apiView(request):
    urls = {
        'base': '',
        'FBV': 'rooms/',
        'CBV': 'rooms-class/',
    }
    return JsonResponse(urls)
