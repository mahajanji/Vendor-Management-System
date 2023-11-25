from django.http import Http404
from rest_framework.permissions import IsAuthenticated
from api.models import *
from .serializers import *
from rest_framework.generics import ListAPIView
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import viewsets #imp
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
# from api.renderers import UserRenderer
# from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework.parsers import MultiPartParser, FormParser #file imag upload
#
from django.contrib.auth import authenticate,logout,login
from rest_framework.decorators import action
# Create your views here.

class vendorsViewSet(viewsets.ModelViewSet):
    queryset = Vendor.objects.all()
    serializer_class = vendorserializers

    #url - /api/vendors/<int:id>/performance/
    @action(detail=True, methods=['get','post'])
    def performance(self, request, pk=None):
        try:
            vendors = Vendor.objects.get(pk=pk)
            perfomance = HistoricalPerformance.objects.filter(vendor=vendors)
            per_serializer = PurchaseOrderTrackingSerializers(perfomance, many=True, context={'request':request})
            return Response(per_serializer.data)
        except Exception as e:
            return Response({'message':'Vendor id not exist.'})

class PurchaseOrderTrackingViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrderTracking.objects.all()
    serializer_class = PurchaseOrderTrackingSerializers

class vendorsPerformanceViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrderTracking.objects.all()
    serializer_class = PurchaseOrderTrackingSerializers

class purchase_orders_acknowledge(viewsets.ModelViewSet):
    queryset = PurchaseOrderTracking.objects.all()
    serializer_class = PurchaseOrderTrackingSerializers