from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken


class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # access_token을 쿠키에서 가져오기
        raw_token = request.COOKIES.get('access')

        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token


def verify_token(token):
    try:
        validated_token = JWTAuthentication().get_validated_token(token)
        user = JWTAuthentication().get_user(validated_token)
        return user.id
    except Exception as e:
        raise InvalidToken("Token invalid: " + str(e))