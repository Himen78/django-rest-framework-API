from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.serializers import ValidationError, EmailField
from AuthApi.models import *

class UserSerializer(serializers.ModelSerializer):

    email = EmailField(label = 'Email')
    
    class Meta:
        model = User
        fields = ('id', 'email', 'password')
        extra_kwargs = {
                        'password': {'write_only':True}
                        }

class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True, required=True,)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

    def create(self, validated_data):
        user = super(RegisterSerializer, self).create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

class UserGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = {'id','username','email'}

# class UserUpdateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = {'id','username','email'}