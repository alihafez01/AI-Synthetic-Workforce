from django.shortcuts import render
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core.mail import send_mail
from django.conf import settings
from .serializers import UserRegistrationSerializer, WorkspaceSerializer, JoinWorkspaceSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer, MFASetupSerializer, MFAVerifySerializer, MFALoginSerializer
from .models import Workspace
import pyotp
import qrcode
import io
import base64
from datetime import timedelta
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserRegistrationSerializer

class WorkspaceViewSet(viewsets.ModelViewSet):
    queryset = Workspace.objects.all()
    serializer_class = WorkspaceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        workspace = serializer.save(owner=self.request.user)
        workspace.members.add(self.request.user)

    def get_queryset(self):
        # Return workspaces where user is owner or member
        return self.request.user.workspaces.all() | self.request.user.owned_workspaces.all()

    @action(detail=False, methods=['post'])
    def join(self, request):
        serializer = JoinWorkspaceSerializer(data=request.data)
        if serializer.is_valid():
            invite_code = serializer.validated_data['invite_code']
            try:
                workspace = Workspace.objects.get(invite_code=invite_code)
                if request.user in workspace.members.all():
                     return Response({'detail': 'Already a member'}, status=status.HTTP_400_BAD_REQUEST)
                
                workspace.members.add(request.user)
                return Response({'detail': 'Successfully joined workspace', 'workspace_id': workspace.id})
            except Workspace.DoesNotExist:
                return Response({'detail': 'Invalid invite code'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RequestPasswordResetView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = PasswordResetRequestSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.filter(email=email).first()
            if user:
                token = PasswordResetTokenGenerator().make_token(user)
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                # For now, printing link to console or sending real email
                reset_link = f"http://localhost:3000/reset-password?uid={uidb64}&token={token}"
                
                # Send Email
                try:
                    send_mail(
                        'Password Reset Request',
                        f'Click the link to reset your password: {reset_link}',
                        'noreply@aisyntheticworkforce.com',
                        [email],
                        fail_silently=False,
                    )
                except Exception as e:
                    return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # For security, always return success message 
            return Response({'detail': 'If an account exists, a reset link has been sent.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SetNewPasswordView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'detail': 'Password has been reset successfully.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MFASetupView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = MFASetupSerializer

    def get(self, request):
        # Generate Secret
        secret = pyotp.random_base32()
        
        # Generate QR Code
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(name=request.user.email, issuer_name="AI Synthetic Workforce")
        
        qr = qrcode.make(provisioning_uri)
        buffered = io.BytesIO()
        qr.save(buffered, format="PNG")
        qr_image_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        # Generate Backup Codes (10 codes of 8 digits)
        backup_codes = [pyotp.random_base32()[:8] for _ in range(10)]
        
        # Save secret temporarily? 
        # Actually standard practice: save secret but don't enable MFA yet.
        # Allow user to scan, then VERIFY to enable.
        request.user.mfa_secret = secret
        request.user.backup_codes = backup_codes
        request.user.save()

        return Response({
            'secret': secret,
            'qr_image': qr_image_base64,
            'backup_codes': backup_codes
        })

class MFAVerifyView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = MFAVerifySerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            code = serializer.validated_data['code']
            if not request.user.mfa_secret:
                 return Response({"detail": "MFA setup not initiated."}, status=status.HTTP_400_BAD_REQUEST)
            
            totp = pyotp.TOTP(request.user.mfa_secret)
            if totp.verify(code):
                request.user.mfa_enabled = True
                request.user.save()
                return Response({"detail": "MFA enabled successfully."})
            return Response({"detail": "Invalid code"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        # Allow standard login logic to check credentials first
        # SimpleJWT's TokenObtainPairView uses a serializer to validate credentials
        # We can inspect the serializer after validation
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
             return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
             
        user = serializer.user
        
        if user.mfa_enabled:
            # Issue a temporary token (subset of Access Token with specific scope/claim)
            # Or just a signed JWT meant for MFA exchange
            temp_token = AccessToken.for_user(user)
            # We can start the token with a short lifetime
            temp_token.set_exp(lifetime=timedelta(minutes=5))
            temp_token['mfa_pending'] = True
            
            return Response({
                'mfa_required': True,
                'temp_token': str(temp_token)
            })
            
        return super().post(request, *args, **kwargs)

class MFALoginConfirmView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = MFALoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            temp_token_str = serializer.validated_data['temp_token']
            try:
                # Verify temp token
                token = AccessToken(temp_token_str)
                if not token.get('mfa_pending'):
                     return Response({"detail": "Invalid token type."}, status=status.HTTP_400_BAD_REQUEST)
                
                user_id = token['user_id']
                user = User.objects.get(id=user_id)
            except Exception:
                return Response({"detail": "Invalid or expired session."}, status=status.HTTP_401_UNAUTHORIZED)

            # Check TOTP
            code = serializer.validated_data.get('code')
            backup_code = serializer.validated_data.get('backup_code')
            
            is_valid = False
            if code:
                totp = pyotp.TOTP(user.mfa_secret)
                if totp.verify(code):
                    is_valid = True
            elif backup_code:
                if backup_code in user.backup_codes:
                    # Remove used backup code
                    user.backup_codes.remove(backup_code)
                    user.save()
                    is_valid = True
            
            if is_valid:
                # Generate real tokens
                refresh = RefreshToken.for_user(user)
                return Response({
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                })
            
            return Response({"detail": "Invalid code"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
