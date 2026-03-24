from django.views.generic import ListView, DetailView, TemplateView
from .models import FishProduct


class ProductListView(ListView):
    model = FishProduct
    template_name = 'catalog/product_list.html'
    context_object_name = 'products'


class ProductDetailView(DetailView):
    model = FishProduct
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'


class AboutView(TemplateView):
    template_name = 'catalog/about.html'
