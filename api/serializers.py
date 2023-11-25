from rest_framework import serializers
from api.models import *
#from api.utils import *
from django.core.exceptions import ValidationError


class vendorserializers(serializers.ModelSerializer):
    
    class Meta:
        model = Vendor
        fields = '__all__'

class PurchaseOrderTrackingSerializers(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrderTracking
        fields = '__all__'

# class LoginSerializer(serializers.HyperlinkedModelSerializer):
#     email = serializers.EmailField(max_length=255)
#     class Meta:
#         model = User
#         fields = ['id','email','password']