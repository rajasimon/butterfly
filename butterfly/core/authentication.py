from rest_framework.authentication import TokenAuthentication


class BearerAuthentication(TokenAuthentication):
    """
    Default token authentication in DRF expects "Token" in the Authorization
    header. But tools like Postman expects Bearer string int the header.
    """

    keyword = "Bearer"
