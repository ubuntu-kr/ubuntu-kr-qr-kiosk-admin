"""
URL configuration for kioskadmin project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import include
from kiosksvc import views, pdfview

urlpatterns = [
    path('admin/', admin.site.urls),
    path('oidc/', include('mozilla_django_oidc.urls')),
    path("participants/", views.search_participants),
    path("participant/", views.get_participant),
    path("checkin/", views.CheckInParticipant.as_view()),
    path("checkin_passcode/", views.CheckInByCode.as_view()),
    path("call_staff/", views.CallStaffView.as_view()),
    path("request_cert/", pdfview.attendee_cert_request)
]
