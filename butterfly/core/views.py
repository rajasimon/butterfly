from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class LoginAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        return Response("got it")
        # user = authenticate(email=email, password=password)
        # if user is not None:
        #     login(request, user)
        #     return Response({"detail": "login successful"}, status=status.HTTP_200_OK)

        # else:
        #     return Response(
        #         {"detail": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST
        #     )
