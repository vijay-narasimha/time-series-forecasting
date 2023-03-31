from django.urls import path 

from . import views 

urlpatterns=[
    path('',views.index,name='index'),
    path('day/',views.dayanalysis,name='day'),
    path('predict/', views.prediction,name='predict')
]