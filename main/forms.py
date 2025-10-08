from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Booking


class BookingForm(forms.ModelForm):
    """Форма для бронирования домика"""
    
    class Meta:
        model = Booking
        fields = ['house', 'guest_name', 'guest_phone', 'guest_email', 
                 'check_in_date', 'check_out_date', 'guests_count', 'special_requests']
        widgets = {
            'check_in_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'min': timezone.now().date().isoformat()
            }),
            'check_out_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'min': timezone.now().date().isoformat()
            }),
            'guest_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите ваше имя'
            }),
            'guest_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+7 (999) 123-45-67'
            }),
            'guest_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your@email.com'
            }),
            'guests_count': forms.Select(attrs={
                'class': 'form-control'
            }),
            'special_requests': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Особые пожелания (необязательно)'
            }),
            'house': forms.Select(attrs={
                'class': 'form-control'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Фильтруем только доступные домики
        self.fields['house'].queryset = self.fields['house'].queryset.filter(is_available=True)
        
        # Добавляем CSS классы для валидации
        for field_name, field in self.fields.items():
            if field.required:
                field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' required'

    def clean(self):
        cleaned_data = super().clean()
        check_in_date = cleaned_data.get('check_in_date')
        check_out_date = cleaned_data.get('check_out_date')
        house = cleaned_data.get('house')
        guests_count = cleaned_data.get('guests_count')

        # Проверка дат
        if check_in_date and check_out_date:
            if check_in_date < timezone.now().date():
                raise ValidationError("Дата заезда не может быть в прошлом")
            
            if check_out_date <= check_in_date:
                raise ValidationError("Дата выезда должна быть позже даты заезда")

            # Проверка минимального периода (1 ночь)
            if (check_out_date - check_in_date).days < 1:
                raise ValidationError("Минимальный период бронирования - 1 ночь")

        # Проверка вместимости домика
        if house and guests_count:
            if guests_count > house.capacity:
                raise ValidationError(f"Домик '{house.name}' вмещает максимум {house.capacity} человек")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Автоматически рассчитываем общую стоимость
        if instance.check_in_date and instance.check_out_date and instance.house:
            nights = (instance.check_out_date - instance.check_in_date).days
            instance.total_price = instance.house.price_per_night * nights
        
        if commit:
            instance.save()
        return instance


class ContactForm(forms.Form):
    """Форма для обратной связи"""
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ваше имя'
        }),
        label='Имя'
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your@email.com'
        }),
        label='Email'
    )
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+7 (999) 123-45-67'
        }),
        label='Телефон'
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Ваше сообщение'
        }),
        label='Сообщение'
    )

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        # Простая валидация телефона
        import re
        phone_pattern = re.compile(r'^[\+]?[0-9\s\-\(\)]{10,}$')
        if not phone_pattern.match(phone):
            raise ValidationError("Введите корректный номер телефона")
        return phone

