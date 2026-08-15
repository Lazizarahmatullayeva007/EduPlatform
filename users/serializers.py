from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'role', 'bio',
            'avatar', 'phone_number', 'is_phone_verified'
        ]
        read_only_fields = ['id', 'is_phone_verified']


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role', 'bio', 'phone_number']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class SendVerificationCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        max_length=20,
        required=True,
        help_text="SMS yuboriladigan telefon raqami (masalan, +998901234567)"
    )


class VerifyPhoneSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        max_length=20,
        required=True,
        help_text="Telefon raqami"
    )
    code = serializers.CharField(
        max_length=6,
        min_length=6,
        required=True,
        help_text="6 xonali SMS tasdiqlash kodi"
    )


class UserProfileSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'bio', 'avatar', 'avatar_url', 'phone_number', 'is_phone_verified'
        ]
        read_only_fields = ['id', 'username', 'role', 'is_phone_verified', 'avatar_url']

    def get_avatar_url(self, obj):
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None
