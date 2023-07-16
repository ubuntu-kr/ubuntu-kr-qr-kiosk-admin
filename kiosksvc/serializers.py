from kiosksvc.models import CheckInLog
from rest_framework import serializers


class CheckInLogSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CheckInLog
        fields = ['tokenId', 'checkedInAt', 'participant']

