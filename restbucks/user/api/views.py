from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authentication import authenticate
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status
from .serializers import RegisterSerializer
import logging

logger = logging.getLogger(__name__)

@api_view(['POST','GET'])
def login_api_view(request):
    """logging view using DRF built-in Authtoken to genereate Token

    Args:
        request (HTTP REQUEST): to entered data

    Returns:
        JSON: generated token
    """    
    serializer = AuthTokenSerializer(data=request.data)
    if request.method == "POST":
        if serializer.is_valid():
            user = authenticate(**serializer.data)
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        else:
            logger.error(str(serializer.data))
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response(AuthTokenSerializer().data)


@api_view(['POST',])
def register_api_view(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        token, created = Token.objects.get_or_create(user=serializer.instance)
        return Response({'token': token.key, 'username': serializer.instance.username}, 
                        status=status.HTTP_201_CREATED)
    else:
        logger.error(str(serializer.data))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
