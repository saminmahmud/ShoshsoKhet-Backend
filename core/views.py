from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

class WelcomeView(APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request):
        return Response({"message": "Welcome to Shoshsokhet API"})