from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.home, name='home'),
    path('houses/', views.houses_list, name='houses_list'),
    path('houses/<int:house_id>/', views.house_detail, name='house_detail'),
    path('gallery/', views.gallery, name='gallery'),
    path('reviews/', views.reviews, name='reviews'),
    path('booking/', views.booking, name='booking'),
    path('booking/success/<int:booking_id>/', views.booking_success, name='booking_success'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    
    # API endpoints
    path('api/check-availability/', views.check_availability, name='check_availability'),
    path('api/calculate-price/', views.calculate_price, name='calculate_price'),
]

