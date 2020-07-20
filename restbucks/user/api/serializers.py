from rest_framework import serializers
from django.contrib.auth import get_user_model
import re

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class RegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['email', 'password',]
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate_password(self, value):
        regexp = re.compile(r'[A-Za-z]')
        regexp_num = re.compile(r'[0-9]')
        if value:
            if len(value) < 8:
                raise serializers.ValidationError("Pssword length should be atleast 8 characters")
            if not regexp.search(value) or not regexp_num.search(value):
                raise serializers.ValidationError("password should contains numbers and letters")
            return value
    
    def create(self, validated_data):
        user = User.objects.create(email=validated_data['email'])
        user.set_password(validated_data['password'])
        user.save()
        return user