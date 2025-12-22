from django.urls import path
from . import views



urlpatterns = [

    path('', views.home, name='home'),
    path('catalog/', views.ProductListView.as_view(), name='catalog'),
    path('catalog/<slug:category_slug>/', views.ProductListView.as_view(), name='category'),
    path('product/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('search/', views.ProductListView.as_view(), name='search'),
    path('new/', views.new_arrivals, name='new_arrivals'),
    path('sales/', views.sales, name='sales'),
]

