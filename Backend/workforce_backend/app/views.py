from django.shortcuts import render
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from .serializers import UserRegistrationSerializer, WorkspaceSerializer, JoinWorkspaceSerializer
from .models import Workspace

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
