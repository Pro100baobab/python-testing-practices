from django.contrib import admin
from .models import FishProduct

@admin.register(FishProduct)
class FishProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'kind', 'is_fresh', 'weight_grams', 'price_per_kg', 'country', 'quality_rating')
    list_filter = ('kind', 'is_fresh', 'country')
    search_fields = ('name', 'country')
    fieldsets = (
        (None, {
            'fields': ('name', 'kind', 'is_fresh', 'weight_grams', 'price_per_kg')
        }),
        ('Дополнительная информация', {
            'fields': ('country', 'quality_rating'),
            'classes': ('collapse',)
        }),
    )