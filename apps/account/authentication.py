from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed


class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user = super().get_user(validated_token)

        token_issued_at = validated_token['iat']
        if user.token_last_issued and token_issued_at < int(user.token_last_issued.timestamp()):
            raise AuthenticationFailed("This token has been invalidated due to a new login.")

        return user
