from django.shortcuts import render
from app.models import User
from app.serializer import UserEditSerializer, UserPasswordSerializer
from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet
from app.permissions import UserPermission
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import UpdateAPIView




from django.dispatch import receiver
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import send_mail 





class UserViewSet(ModelViewSet):
    serializer_class = UserEditSerializer
    queryset = User.objects.all()
    permission_classes = [UserPermission]


class UserPassword(UpdateAPIView):
    serializer_class = UserPasswordSerializer
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
                'data': []
            }
            return Response(response)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    email_plaintext_message = "{}?token={}".format(reverse('password_reset:reset-password-request'), reset_password_token.key)
    send_mail(
            "Password Reset for {title}".format(title="Some website title"),
            email_plaintext_message,
            "noreply@somehost.local",
            [reset_password_token.user.email]
             )