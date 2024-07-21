from django.db import models
from django.http import JsonResponse
from django.conf import settings
from django.utils import timezone
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
import requests
from rest_framework.decorators import api_view, authentication_classes
from .tasks import send_checkin_confirm


public_webhook_url = settings.WEBHOOK_URLS["public"]
organizer_webhook_url = settings.WEBHOOK_URLS["organizer"]
# Create your views here.


class CallStaffView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    def get(self, request):
        webhook_payload = {
            "text": "누군가가 리셉션 키오스크로 관계자를 호출 했습니다."
        }
        requests.post(organizer_webhook_url, json=webhook_payload)
        return JsonResponse({
            "result":"success"
        })

@api_view(['GET'])
@authentication_classes([authentication.TokenAuthentication])
def search_participants(request):
    participants = Participant.objects.filter(email__contains=request.query_params['keyword'])
    serializer = ParticipantSerializer(participants, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@authentication_classes([authentication.TokenAuthentication])
def get_participant(request):
    participant = Participant.objects.get(id=request.query_params['id'])
    serializer = ParticipantSerializer(participant, many=True)
    return Response(serializer.data)


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
        dupcheck = CheckInLog.objects.filter(participant=int(participantId)).first()
        if(dupcheck is not None):
            return JsonResponse({
                "result":"이미 체크인 한 참가자 입니다. Participant already checked in."
            }, status=401)
        
        passCodeData = PasscodeCheckInSerializer(data=request.data)
        passCodeData.is_valid()
        participant = Participant.objects.get(id=int(participantId))
        
        passcodeCheck = bcrypt.checkpw(passCodeData.validated_data['passcode'].encode(), participant.passCode)
        if (not passcodeCheck):
            return JsonResponse({
                "result":"틀린 인증코드 입니다. Passcode not matches."
            }, status=401)

        CheckInLog.objects.create(
            tokenId=f"PASSCODE_{datetime.datetime.now().timestamp()}",
            checkedInAt=timezone.now(),
            participant=participant
        )
        send_checkin_confirm.delay(participantId)
        return JsonResponse({
                "result":"Participant successfully checked in"
            }, status=200)