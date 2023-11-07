from django.conf.urls import url, include
from django.contrib.auth.decorators import login_required
from rest_framework import routers
from apps.ruteo.views import *
router = routers.DefaultRouter()

urlpatterns = [
	#urls Para Apis
	url(r'^consultaRutas',(consultaRutas), name='consultaRutas'),
]