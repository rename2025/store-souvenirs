from django.shortcuts import render, get_object_or_404, redirect
from .models import Review
from products.models import Product

def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        Review.objects.create(
            product=product,
            user=request.user,
            rating=request.POST['rating'],
            text=request.POST['text']
        )
        return redirect('product_detail', slug=product.slug)
    return render(request, 'reviews/add_review.html')
