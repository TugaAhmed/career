# users/views.py
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.conf import settings
from django.core.mail import send_mail
from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import SignupSerializer
from .models import User
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate




signer = TimestampSigner()

class SignupView(generics.CreateAPIView):
    serializer_class = SignupSerializer

    def perform_create(self, serializer):
        user = serializer.save()

        # Create signed token for email verification with expiration
        token = signer.sign(user.email)

        # Construct verification URL
        verification_url = f"http://example.com/api/verify-email?token={token}"

        # Send verification email
        send_mail(
            subject="Verify your email",
            message=f"Click the link to verify your email: {verification_url}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )



class VerifyEmailView(APIView):
    def get(self, request):
        token = request.query_params.get('token')
        if not token:
            return Response({
                "success": False,
                "message": "Token missing",
                "object": None,
                "errors": ["Token is required"]
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            email = signer.unsign(token, max_age=3600)  # 1-hour expiry
            user = User.objects.get(email=email)

            if user.is_active:
                return Response({
                    "success": True,
                    "message": "Email already verified",
                    "object": None,
                    "errors": None
                })

            user.is_active = True
            user.save()

            return Response({
                "success": True,
                "message": "Email verified successfully",
                "object": None,
                "errors": None
            })

        except SignatureExpired:
            # Token expired — resend verification email with new token
            try:
                # Find user by extracting email without validation (safer to parse token payload differently)
                # Here, fallback to user email extraction from expired token
                # Django's TimestampSigner does not expose payload if expired, so just resend by token's email param
                # We'll try to extract email by unsigning without age limit - risky but needed here:

                email = signer.unsign(token, max_age=None)  # ignoring expiration
                user = User.objects.get(email=email)

                if user.is_active:
                    return Response({
                        "success": True,
                        "message": "Email already verified",
                        "object": None,
                        "errors": None
                    })

                new_token = signer.sign(user.email)
                verification_url = f"http://example.com/api/verify-email?token={new_token}"

                send_mail(
                    subject="New verification link",
                    message=f"Your previous link expired. Click here to verify your email: {verification_url}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                )

                return Response({
                    "success": False,
                    "message": "Token expired. A new verification email has been sent.",
                    "object": None,
                    "errors": ["Token expired, new verification email sent"]
                }, status=status.HTTP_400_BAD_REQUEST)

            except (BadSignature, User.DoesNotExist):
                return Response({
                    "success": False,
                    "message": "Invalid token",
                    "object": None,
                    "errors": ["Invalid token"]
                }, status=status.HTTP_400_BAD_REQUEST)

        except (BadSignature, User.DoesNotExist):
            return Response({
                "success": False,
                "message": "Invalid token",
                "object": None,
                "errors": ["Invalid token"]
            }, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({
                "success": False,
                "message": "Email and password are required",
                "object": None,
                "errors": ["Email and password must be provided"]
            }, status=status.HTTP_400_BAD_REQUEST)

        # Authenticate user using Django's built-in authentication
        user = authenticate(request, username=email, password=password)

        if user is None:
            return Response({
                "success": False,
                "message": "Invalid credentials",
                "object": None,
                "errors": ["Email or password is incorrect"]
            }, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({
                "success": False,
                "message": "Email is not verified",
                "object": None,
                "errors": ["Please verify your email before logging in"]
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Create JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response({
            "success": True,
            "message": "Login successful",
            "object": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user_id": user.id,
                "role": user.role,
            },
            "errors": None
        })