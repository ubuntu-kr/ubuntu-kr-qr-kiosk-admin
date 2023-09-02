from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from kiosksvc.models import CheckInLog, Participant
from kiosksvc.serializers import ParticipantSerializer, PasscodeCheckInSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from cryptography.hazmat.primitives import serialization
import jwt
import datetime
import bcrypt
from django.core.mail import EmailMessage


jwt_public_key_raw = open(settings.CHECKIN_QR_CONFIG["public_key_path"], 'r').read()
jwt_public_key = serialization.load_pem_public_key(jwt_public_key_raw.encode())
jwt_key_algo = settings.CHECKIN_QR_CONFIG["key_algo"]
# Create your views here.
def kiosk_config(request):
    return JsonResponse({
        "public_key": jwt_public_key_raw,
        "key_algo": jwt_key_algo,
    })

class ParticipantView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    def get(self, request):
        participants = Participant.objects.filter(email__contains=request.query_params['keyword'])
        serializer = ParticipantSerializer(participants, many=True)
        return Response(serializer.data)

class CheckInParticipant(APIView):
    """
    View to list all users in the system.

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [permissions.IsAdminUser]
    def post(self, request, format=None):
        if("ParticipantToken" not in request.headers):
            return JsonResponse({
                "result":"ParticipantToken not found in header"
            }, status=401)
        token = request.headers['ParticipantToken']
        try:
            payload = jwt.decode(token, jwt_public_key, algorithms=[jwt_key_algo], verify=True)
        except:
            return JsonResponse({
                "result":"Error decoding token"
            }, status=401)
        dupcheck = CheckInLog.objects.filter(tokenId=payload['tid']).first()
        if(dupcheck is not None):
            return JsonResponse({
                "result":"Participant already checked in"
            }, status=401)
        participant = Participant.objects.get(id=int(payload['sub']))
        CheckInLog.objects.create(
            tokenId=payload['tid'],
            checkedInAt=datetime.datetime.now(),
            participant=participant
        )

        subject = f"{settings.EMAIL_EVENT_NAME} 체크인 완료"
        message = f"""
        {participant.name}님 안녕하세요,
        {settings.EMAIL_EVENT_NAME} 체크인이 완료 되었습니다.

        {settings.EMAIL_SENDER_NAME} 드림.
        """
        email = EmailMessage(
            subject,
            message,
            settings.EMAIL_SENDER,
            [participant.email],
            [],
            reply_to=[settings.EMAIL_REPLY_TO],
            headers={},
        )
        email.send()

        return JsonResponse({
                "result":"Participant successfully checked in"
            }, status=200)

class CheckInByCode(APIView):
    """
    View to list all users in the system.

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [permissions.IsAdminUser]
    def post(self, request, format=None):
        if 'participantId' not in request.query_params:
            return JsonResponse({
                "result":"participantId not found in query params"
            }, status=401)
        participantId = request.query_params['participantId']
        dupcheck = CheckInLog.objects.filter(tokenId="PASSCODE", participant=int(participantId)).first()
        if(dupcheck is not None):
            return JsonResponse({
                "result":"이미 체크인 한 참가자 입니다. Participant already checked in."
            }, status=401)
        
        passCodeData = PasscodeCheckInSerializer(data=request.data)
        participant = Participant.objects.get(id=int(participantId))
        
        passcodeCheck = bcrypt.checkpw(passCodeData.passcode, participant.passCode)
        if (not passcodeCheck):
            return JsonResponse({
                "result":"틀린 인증코드 입니다. Passcode not matches."
            }, status=401)

        CheckInLog.objects.create(
            tokenId="PASSCODE",
            checkedInAt=datetime.datetime.now(),
            participant=participant
        )

        subject = f"{settings.EMAIL_EVENT_NAME} 체크인 완료"
        message = f"""
        {participant.name}님 안녕하세요,
        {settings.EMAIL_EVENT_NAME} 체크인이 완료 되었습니다.

        {settings.EMAIL_SENDER_NAME} 드림.
        """
        email = EmailMessage(
            subject,
            message,
            settings.EMAIL_SENDER,
            [participant.email],
            [],
            reply_to=[settings.EMAIL_REPLY_TO],
            headers={},
        )
        email.send()

        return JsonResponse({
                "result":"Participant successfully checked in"
            }, status=200)