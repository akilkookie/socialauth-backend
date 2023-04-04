import requests
from django.contrib.auth import login
from rest_framework.views import APIView
from rest_framework import status, viewsets, generics
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken

from rest_framework.generics import CreateAPIView, UpdateAPIView, ListAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import permissions
from rest_framework.response import Response

from .models import CustomUser

from accounts.serializers import CreateUserSerializer, UpdateUserSerializer, LoginSerializer, UserSerializer, \
    ImageSerializer, SocialRegistrationSerializer


class CreateUserAPI(CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CreateUserSerializer
    permission_classes = (permissions.AllowAny,)


class UpdateUserAPI(UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UpdateUserSerializer


class UserAvatarUpload(ListAPIView):
    queryset = CustomUser.objects.all()
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = ImageSerializer

    def post(self, request):
        first_name = request.data['first_name']
        file = request.data['image']
        user = CustomUser.objects.get(first_name=first_name)
        user.image = file
        user.save()
        return Response("Image updated!", status=status.HTTP_200_OK)


class CustomAuthToken(ObtainAuthToken):
    permission_classes = (permissions.AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        login(request, user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })


class CreateSocialAccount(APIView):
    permission_classes = (permissions.AllowAny,)

    # def post(self, request):
    #     reg_serializer = SocialRegistrationSerializer(data=request.data)
    #     if reg_serializer.is_valid():
    #         new_user = reg_serializer.save()
    #         if new_user:
    #             return Response(status=status.HTTP_201_CREATED)
    #     return Response(reg_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        reg_serializer = SocialRegistrationSerializer(data=request.data)
        if reg_serializer.is_valid():
            new_user = reg_serializer.save()
            if new_user:
                r = requests.post('http://127.0.0.1:8000/api-auth/token', data={
                    'username': new_user.email,
                    'password': request.data['password'],
                    'client_id': 'AG26DtBeOvoT3EKRjVXmLHgoh1k5lSvfmjJs2Kje',
                    'client_secret': 'vVmD5TdfE5rYzAwtxujlSlyk2gue09nECvf3TpqXIDL1sZhDZ8Ju72FhGaPKxFzGibOyd5pttYRYk48Dcm0fnPKC6v8cDl1ocArInlZemZC0PH7GBbdyGeaxji8yW9dI',
                    'grant_type': 'password'
                })
                return Response(r.json(), status=status.HTTP_201_CREATED)
        return Response(reg_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AllUsers(generics.ListAPIView):
    permission_classes = (permissions.AllowAny,)
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer




