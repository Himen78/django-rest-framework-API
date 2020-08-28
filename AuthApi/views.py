from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from .models import *
from .serializers import RegisterSerializer, UserSerializer, UserGetSerializer
from rest_framework.decorators import APIView
from AuthApi.AuthenticationClass import AuthenticationToken
from .models import UserToken
from rest_framework.permissions import AllowAny
from rest_framework.decorators import authentication_classes, permission_classes
import datetime
import os, configparser
from datetime import date
from django.utils import timezone

# Create your views here.
class UserGetView(APIView):
    serializer_class = UserGetSerializer
    authentication_classes = (AuthenticationToken,)
    queryset = User.objects.all()
    lookup_field = 'id'

    def getData(self, id):
        try:
            return User.objects.get(id=id)
        except User.DoesNotExist:
            response = {"message":"User is not found", "status":status.HTTP_404_NOT_FOUND}
            return Response(response, status=status.HTTP_404_NOT_FOUND)

    def get(self, request, id):
        user = self.getData(id)
        serializer = RegisterSerializer(user)

        data = {
            'id' : serializer.data['id'],
            'username' : serializer.data['username'],
            'email' : serializer.data['email'],
        }
        
        return Response({"message": "User is retrieved successfully.", "data":data ,"status": status.HTTP_200_OK}, status.HTTP_200_OK)

@authentication_classes([])
class CreatedView(APIView):
    permission_classes = [AllowAny,]

    def post(self, request, *args, **kwargs):

        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        if not username:
            return Response({"message":"Username is required", "status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)
        
        if not email:
            return Response({"message":"Email is required", "status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)
        
        if not password:
            return Response({"message":"Password is required", "status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)

        data = {"username":username, "email":email, "password":password}
        serializer = RegisterSerializer(data=request.data)

        if not serializer.is_valid(raise_exception=False):
            error_msg = serializer.errors

            if serializer.errors.get('email'):
                user = User.objects.filter(email = email)
                if user:
                    error_msg = "Email address is alreeady registered."
                else:
                    error_msg = "Email is not valid."
            
            return Response({"message":error_msg, "status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)
        serializer.save()

        user_id = serializer.data['id']
        user = User.objects.get(id = user_id)

        token = UserToken.objects.create(user=user)
        data = serializer.data

        data['token'] = "Token " + token.key
            
        return Response({"message": "Registered successfully.", "data": data, "status":status.HTTP_201_CREATED}, status=status.HTTP_201_CREATED)

class UpdateView(APIView):

    def getData(self, id):
        try:
            return User.objects.get(id=id)
        except User.DoesNotExist:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)

    def get(self, request, id):
        user = self.getData(id)
        serializer = RegisterSerializer(user)
        return Response(serializer.data)

    def put(self, request, id):
        user = self.getData(id)
        serializer = RegisterSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()

            return Response({"message":"User is updated successfully", "data":serializer.data, "status":status.HTTP_200_OK}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([])
class LoginUser(APIView):

    permission_classes = [AllowAny,]
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):

        data = request.data
        if not data:
            return Response({"message":"Data is required.", "status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)

        email = data.get('email')
        password = data.get('password')

        if not email:
            return Response({"message":"Email is required.", "status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)

        if not password:
            return Response({"message":"Password is required.", "status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)

        # user = User.objects.filter(password = password).first()
        user = User.objects.filter(email = email).first()

        if not user:
            return Response({"message":"Entered email address is not registered.", "status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)

        serializer = UserSerializer(data=data)

        user = User.objects.get(email=email)

        token = UserToken.objects.create(user=user) # Create & genearte new token while login.
        user.last_login = datetime.datetime.now(tz=timezone.utc)

        if serializer.is_valid():
            user.save()
        new_data = serializer.data

        new_data['token'] = "Token " + token.key
        new_data['id'] = user.id
        new_data['username'] = user.username

        return Response({"message": "Login Successfully.", "data":new_data ,"status": status.HTTP_200_OK}, status.HTTP_200_OK)

class LogoutUser(APIView):

    authentication_classes = (AuthenticationToken,)

    def delete(self, request):

        return self.destroy(request)

    def destroy(self, request):
        
        auth_token = request.META.get("HTTP_AUTHORIZATION")
        auth_token = auth_token.split(' ')[1]

        token = UserToken.objects.filter(key = auth_token).first()

        if token:
            token.delete()
        
        return Response({"message" : "Logout successfully.", "status": status.HTTP_200_OK}, status.HTTP_200_OK)