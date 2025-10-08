from django.contrib import admin
from django.utils.html import format_html
from .models import House, Booking, Review, GalleryImage, Contact


@admin.register(House)
class HouseAdmin(admin.ModelAdmin):
    list_display = ['name', 'capacity', 'price_per_night', 'is_available', 'created_at']
    list_filter = ['is_available', 'capacity', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_available', 'price_per_night']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'capacity', 'price_per_night', 'image')
        }),
        ('Статус', {
            'fields': ('is_available',)
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['guest_name', 'house', 'check_in_date', 'check_out_date', 'guests_count', 'status', 'total_price']
    list_filter = ['status', 'check_in_date', 'house', 'created_at']
    search_fields = ['guest_name', 'guest_phone', 'guest_email']
    list_editable = ['status']
    readonly_fields = ['created_at', 'updated_at', 'total_price']
    date_hierarchy = 'check_in_date'
    
    fieldsets = (
        ('Информация о госте', {
            'fields': ('guest_name', 'guest_phone', 'guest_email')
        }),
        ('Детали бронирования', {
            'fields': ('house', 'check_in_date', 'check_out_date', 'guests_count', 'total_price')
        }),
        ('Дополнительно', {
            'fields': ('status', 'special_requests')
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['guest_name', 'rating', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_approved', 'created_at']
    search_fields = ['guest_name', 'text']
    list_editable = ['is_approved']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Информация об отзыве', {
            'fields': ('guest_name', 'rating', 'text', 'avatar')
        }),
        ('Статус', {
            'fields': ('is_approved',)
        }),
        ('Временные метки', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_featured', 'order', 'image_preview', 'created_at']
    list_filter = ['is_featured', 'created_at']
    search_fields = ['title', 'description']
    list_editable = ['is_featured', 'order']
    readonly_fields = ['created_at', 'image_preview']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'image', 'alt_text')
        }),
        ('Отображение', {
            'fields': ('is_featured', 'order')
        }),
        ('Временные метки', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px;" />',
                obj.image.url
            )
        return "Нет изображения"
    image_preview.short_description = 'Превью'


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['phone', 'email', 'working_hours', 'updated_at']
    readonly_fields = ['updated_at']
    
    fieldsets = (
        ('Контактная информация', {
            'fields': ('phone', 'email', 'address')
        }),
        ('Координаты', {
            'fields': ('coordinates_lat', 'coordinates_lng')
        }),
        ('Время работы и социальные сети', {
            'fields': ('working_hours', 'telegram', 'whatsapp')
        }),
        ('Временные метки', {
            'fields': ('updated_at',),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # Разрешаем создать только один экземпляр
        return not Contact.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Запрещаем удаление контактной информации
        return False
