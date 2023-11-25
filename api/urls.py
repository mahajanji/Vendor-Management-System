"""vendor_management URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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

from api.views import *
from django.urls import include, path
# from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('vendors', vendorsViewSet, basename='vendors')
router.register('purchase_orders', PurchaseOrderTrackingViewSet, basename='purchase_orders')
#router.register('vendors/<int:id>/performance', vendorsPerformanceViewSet, basename='vendorsPerformanceViewSet')
router.register('purchase_orders/<int:id>/acknowledge', purchase_orders_acknowledge, basename='purchase_orders_acknowledge')

urlpatterns = router.urls
