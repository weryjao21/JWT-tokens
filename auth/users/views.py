from django.http import response
from rest_framework.views import APIView
from.serializers import UserSerializer
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from.models import User
import jwt, datetime
class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class LoginView(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed('Пользователь не найден!')

        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow()+datetime.timedelta(minutes=300),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256').decode('utf-8')

        response = Response()
        response.set_cookie(key='jwt', value = token, httponly=True )
        response.data ={
            'jwt': token
        }
        
        return response

class UserView(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')


        if not token:
            raise AuthenticationFailed('Не прошедший проверку подлинности ')
        try:
            payload = jwt.decode(token, 'secret', algorithm=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Не прошедший проверку подлинности ')
        user = User.objects(id=payload['id']).first()
        serializer = UserSerializer(user)
        return Response(serializer.data)

class Logout (APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'Успешно!'
        }
        return response