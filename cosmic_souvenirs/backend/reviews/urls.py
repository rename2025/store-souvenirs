# reviews/urls.py (рабочая версия)
from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    # Основные пути
     #path('product/<slug:slug>/',views.ProductReviewsListView.as_view(),name='product_reviews'),

    path('add/<int:product_id>/', views.AddReviewView.as_view(), name='add_review'),


    path('edit/<int:pk>/',
         views.ReviewUpdateView.as_view(),
         name='update'),

    path('delete/<int:pk>/',
         views.ReviewDeleteView.as_view(),
         name='delete'),

    # API endpoints для AJAX
    path('api/like/<int:review_id>/',
         views.toggle_like,
         name='toggle_like'),

    path('api/vote/<int:review_id>/',
         views.add_vote,
         name='add_vote'),

    path('api/report/<int:review_id>/',
         views.report_review,
         name='report_review'),
]