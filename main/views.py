from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q
import json

from .models import House, Booking, Review, GalleryImage, Contact
from django.db.utils import OperationalError, ProgrammingError


def get_contact_safe():
    try:
        return Contact.objects.first()
    except (OperationalError, ProgrammingError):
        return None


def safe_list(queryset_fn, limit=None):
    try:
        qs = queryset_fn()
        return qs[:limit] if limit else qs
    except (OperationalError, ProgrammingError):
        return []
from .forms import BookingForm, ContactForm


def home(request):
    """Главная страница"""
    context = {
        'houses': safe_list(lambda: House.objects.filter(is_available=True), limit=3),
        'reviews': safe_list(lambda: Review.objects.filter(is_approved=True), limit=3),
        'gallery_images': safe_list(lambda: GalleryImage.objects.filter(is_featured=True), limit=6),
        'contact': get_contact_safe(),
    }
    return render(request, 'main/home.html', context)


def houses_list(request):
    """Список всех домиков"""
    houses = safe_list(lambda: House.objects.filter(is_available=True))
    
    # Фильтрация по цене
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        houses = houses.filter(price_per_night__gte=min_price)
    if max_price:
        houses = houses.filter(price_per_night__lte=max_price)
    
    # Фильтрация по вместимости
    capacity = request.GET.get('capacity')
    if capacity:
        houses = houses.filter(capacity__gte=capacity)
    
    # Поиск по названию
    search = request.GET.get('search')
    if search:
        houses = houses.filter(
            Q(name__icontains=search) | Q(description__icontains=search)
        )
    
    # Сортировка
    sort_by = request.GET.get('sort', 'name')
    if sort_by == 'price_low':
        houses = houses.order_by('price_per_night')
    elif sort_by == 'price_high':
        houses = houses.order_by('-price_per_night')
    elif sort_by == 'capacity':
        houses = houses.order_by('capacity')
    else:
        houses = houses.order_by('name')
    
    # Пагинация
    paginator = Paginator(houses, 6) if houses else Paginator([], 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'houses': page_obj,
        'contact': get_contact_safe(),
    }
    return render(request, 'main/houses_list.html', context)


def house_detail(request, house_id):
    """Детальная страница домика"""
    try:
        house = get_object_or_404(House, id=house_id, is_available=True)
    except (OperationalError, ProgrammingError):
        return redirect('main:houses_list')
    
    # Проверяем доступность дат
    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')
    
    if check_in and check_out:
        # Здесь можно добавить логику проверки доступности дат
        pass
    
    context = {
        'house': house,
        'contact': get_contact_safe(),
    }
    return render(request, 'main/house_detail.html', context)


def gallery(request):
    """Страница галереи"""
    images = safe_list(lambda: GalleryImage.objects.all().order_by('order', '-created_at'))
    
    # Пагинация
    paginator = Paginator(images, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'images': page_obj,
        'contact': get_contact_safe(),
    }
    return render(request, 'main/gallery.html', context)


def reviews(request):
    """Страница отзывов"""
    reviews_qs = safe_list(lambda: Review.objects.filter(is_approved=True).order_by('-created_at'))
    
    # Пагинация
    paginator = Paginator(reviews_qs, 10) if reviews_qs else Paginator([], 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'reviews': page_obj,
        'contact': get_contact_safe(),
    }
    return render(request, 'main/reviews.html', context)


def booking(request):
    """Страница бронирования"""
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save()
            messages.success(request, 'Ваша заявка успешно отправлена! Мы свяжемся с вами в ближайшее время.')
            return redirect('booking_success', booking_id=booking.id)
    else:
        form = BookingForm()
    
    context = {
        'form': form,
        'houses': House.objects.filter(is_available=True),
        'contact': get_contact_safe(),
    }
    return render(request, 'main/booking.html', context)


def booking_success(request, booking_id):
    """Страница успешного бронирования"""
    booking = get_object_or_404(Booking, id=booking_id)
    context = {
        'booking': booking,
        'contact': get_contact_safe(),
    }
    return render(request, 'main/booking_success.html', context)


def contact(request):
    """Страница контактов"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Здесь можно добавить отправку email или сохранение в базу
            messages.success(request, 'Ваше сообщение отправлено! Мы ответим вам в ближайшее время.')
            return redirect('contact')
    else:
        form = ContactForm()
    
    context = {
        'form': form,
        'contact': get_contact_safe(),
    }
    return render(request, 'main/contact.html', context)


def about(request):
    """Страница о базе отдыха"""
    context = {
        'contact': get_contact_safe(),
    }
    return render(request, 'main/about.html', context)


# API views для AJAX запросов
@csrf_exempt
@require_http_methods(["POST"])
def check_availability(request):
    """Проверка доступности дат для бронирования"""
    try:
        data = json.loads(request.body)
        house_id = data.get('house_id')
        check_in = data.get('check_in')
        check_out = data.get('check_out')
        
        if not all([house_id, check_in, check_out]):
            return JsonResponse({'error': 'Не все данные предоставлены'}, status=400)
        
        # Проверяем, есть ли пересечения с существующими бронированиями
        conflicting_bookings = Booking.objects.filter(
            house_id=house_id,
            status__in=['pending', 'confirmed'],
            check_in_date__lt=check_out,
            check_out_date__gt=check_in
        )
        
        is_available = not conflicting_bookings.exists()
        
        return JsonResponse({
            'available': is_available,
            'message': 'Даты доступны' if is_available else 'Даты заняты'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Неверный формат данных'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def calculate_price(request):
    """Расчет стоимости бронирования"""
    try:
        data = json.loads(request.body)
        house_id = data.get('house_id')
        check_in = data.get('check_in')
        check_out = data.get('check_out')
        
        if not all([house_id, check_in, check_out]):
            return JsonResponse({'error': 'Не все данные предоставлены'}, status=400)
        
        house = get_object_or_404(House, id=house_id)
        
        # Парсим даты
        from datetime import datetime
        check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
        check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
        
        # Рассчитываем количество ночей
        nights = (check_out_date - check_in_date).days
        total_price = house.price_per_night * nights
        
        return JsonResponse({
            'nights': nights,
            'price_per_night': float(house.price_per_night),
            'total_price': float(total_price)
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Неверный формат данных'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
