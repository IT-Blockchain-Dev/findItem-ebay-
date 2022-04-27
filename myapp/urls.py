from django.urls import path
from . import views
urlpatterns = [
    path('getCategory', views.getCategory),
    path('getSubCategory', views.getSubCategory),
    path('uploadData', views.uploadData),
    path('getApiInfo', views.getApiInfo),
    path('updateApiInfo', views.updateApiInfo),

]
