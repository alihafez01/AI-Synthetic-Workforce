from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Workspace

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'full_name')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            full_name=validated_data.get('full_name', '')
        )
        return user

class WorkspaceSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Workspace
        fields = '__all__'
        read_only_fields = ('invite_code', 'created_at', 'updated_at', 'members')

class JoinWorkspaceSerializer(serializers.Serializer):
    invite_code = serializers.CharField(required=True)
