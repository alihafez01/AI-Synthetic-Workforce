from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
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

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        # We generally return validation even if user doesn't exist to prevent enumeration,
        # but in this internal context we can just ensure valid structure.
        # Actually, the view will handle the sending logic.
        return value

class PasswordResetConfirmSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
    token = serializers.CharField()
    uidb64 = serializers.CharField()

    def validate(self, attrs):
        try:
            uid = force_str(urlsafe_base64_decode(attrs['uidb64']))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError({"detail": "Invalid or expired token."})

        if not PasswordResetTokenGenerator().check_token(user, attrs['token']):
            raise serializers.ValidationError({"detail": "Invalid or expired token."})

        attrs['user'] = user
        return attrs

    def save(self):
        password = self.validated_data['password']
        user = self.validated_data['user']
        user.set_password(password)
        user.save()
        return user

class MFASetupSerializer(serializers.Serializer):
    # This serializer is mainly for response documentation/structure
    secret = serializers.CharField(read_only=True)
    qr_image = serializers.CharField(read_only=True)
    backup_codes = serializers.ListField(child=serializers.CharField(), read_only=True)

class MFAVerifySerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6, min_length=6)

class MFALoginSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6, min_length=6, required=False)
    backup_code = serializers.CharField(required=False)
    temp_token = serializers.CharField()

    def validate(self, attrs):
        if not attrs.get('code') and not attrs.get('backup_code'):
             raise serializers.ValidationError("Either 'code' or 'backup_code' is required.")
        return attrs
