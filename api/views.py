from django.http import Http404
from rest_framework.permissions import IsAuthenticated
from api.models import *
from .serializers import *
from django.utils import timezone
from django.db.models import Count, Avg
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

#all crude operation work on this api view
class vendorsViewSet(viewsets.ModelViewSet):
    queryset = Vendor.objects.all()
    serializer_class = vendorserializers

    def perform_create(self, serializer):
        instance_a = serializer.save()
        #access the value of vendor model
        vendorid = instance_a.id
        vendors = Vendor.objects.get(pk=vendorid)
        on_time_delivery_rate = instance_a.on_time_delivery_rate
        quality_rating_avg = instance_a.quality_rating_avg
        average_response_time = instance_a.average_response_time
        fulfillment_rate = instance_a.fulfillment_rate
        perfomancehis = HistoricalPerformance(vendor=vendors,on_time_delivery_rate=on_time_delivery_rate,quality_rating_avg=quality_rating_avg,average_response_time=average_response_time,fulfillment_rate=fulfillment_rate)
        perfomancehis.save()



    #url - /api/vendors/{vendor_id}/performance/
    @action(detail=True, methods=['get'])
    def performance(self, request, pk=None):
        try:
            vendors = Vendor.objects.get(pk=pk)
            perfomance = HistoricalPerformance.objects.filter(vendor=vendors)
            per_serializer = HistoricalPerformanceSerializer(perfomance, many=True, context={'request':request})
            return Response(per_serializer.data)
        except Exception as e:
            return Response({'message':'Vendor id not exist.'})
        

#all crude operation work on this api view  
class PurchaseOrderTrackingViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrderTracking.objects.all()
    serializer_class = PurchaseOrderTrackingSerializers

    def perform_create(self, serializer):
        instance_a = serializer.save()
        #access the value of vendor model
        vendor_id = instance_a.vendor.id
        vendors = Vendor.objects.get(pk=vendor_id)

          # On-Time Delivery Rate
        completed_pos = PurchaseOrderTracking.objects.filter(vendor_id=vendor_id, status='completed')
        on_time_delivery_rate = calculate_on_time_delivery_rate(completed_pos)
        vendors.on_time_delivery_rate = on_time_delivery_rate

        # Quality Rating Average
        completed_pos_with_rating = PurchaseOrderTracking.objects.filter(vendor_id=vendor_id, quality_rating__isnull=False)
        quality_rating_avg = calculate_quality_rating_avg(completed_pos_with_rating)
        vendors.quality_rating_avg = quality_rating_avg

        # Average Response Time
        all_pos_acknowledged = PurchaseOrderTracking.objects.filter(vendor_id=vendor_id, acknowledgment_date__isnull=False)
        average_response_time = calculate_average_response_time(all_pos_acknowledged)
        vendors.average_response_time = average_response_time

        # Fulfilment Rate
        fulfillment_rate = calculate_fulfillment_rate(completed_pos)
        vendors.fulfillment_rate = fulfillment_rate

        vendors.save()
        perfomancehis = HistoricalPerformance(vendor=vendors,on_time_delivery_rate=on_time_delivery_rate,quality_rating_avg=quality_rating_avg,average_response_time=average_response_time,fulfillment_rate=fulfillment_rate)
        perfomancehis.save()

    #url- /api/purchase_orders/{po_id}/acknowledge/
    @action(detail=True, methods=['POST'])
    def acknowledge(self, request, pk=None):
        try:
            pos = PurchaseOrderTracking.objects.get(pk=pk)
            # Update acknowledgment_date with the submitted date
            acknowledgment_date = request.data.get('acknowledgment_date')
            if acknowledgment_date:
                pos.acknowledgment_date = acknowledgment_date
                pos.save()
                # Calculate and update average response time for the vendor
                self.update_vendor_average_response_time(pos.vendor.id)
                return Response({'message': 'Success'})
            else:
                return Response({'message': 'Please provide acknowledgment_date in the request data.'})

        except Exception as e:
            return Response({'message':'PO not exist.'})
        
    def update_vendor_average_response_time(self, vendor_id):
        # Calculate average response time for all POs of the vendor
        all_pos_acknowledged = PurchaseOrderTracking.objects.filter(vendor_id=vendor_id, acknowledgment_date__isnull=False)
        total_pos_acknowledged = all_pos_acknowledged.count()
        
        if total_pos_acknowledged > 0:
            total_response_time = sum([(pos.acknowledgment_date - pos.issue_date).total_seconds() for pos in all_pos_acknowledged])
            avg_response_time = total_response_time / total_pos_acknowledged
        else:
            avg_response_time = 0

        # Update the vendor's average_response_time field
        vendor = Vendor.objects.get(id=vendor_id)
        vendor.average_response_time = avg_response_time
        vendor.save()


def calculate_on_time_delivery_rate(completed_pos):
    total_completed_pos = completed_pos.count()
    on_time_pos = completed_pos.filter(delivery_date__lte=timezone.now())
    on_time_delivery_rate = (on_time_pos.count() / total_completed_pos) * 100 if total_completed_pos != 0 else 0
    return on_time_delivery_rate

def calculate_quality_rating_avg(completed_pos_with_rating):
    quality_rating_avg = completed_pos_with_rating.aggregate(Avg('quality_rating'))['quality_rating__avg'] or 0
    return quality_rating_avg

def calculate_average_response_time(all_pos_acknowledged):
    total_pos_acknowledged = all_pos_acknowledged.count()
    total_response_time = sum([(pos.acknowledgment_date - pos.issue_date).total_seconds() for pos in all_pos_acknowledged])
    avg_response_time = total_response_time / total_pos_acknowledged if total_pos_acknowledged != 0 else 0
    return avg_response_time

def calculate_fulfillment_rate(completed_pos):
    total_completed_pos = completed_pos.count()
    successful_fulfillments = completed_pos.filter(status='completed', issue_date__isnull=False, acknowledgment_date__isnull=False)
    fulfillment_rate = (successful_fulfillments.count() / total_completed_pos) * 100 if total_completed_pos != 0 else 0
    return fulfillment_rate