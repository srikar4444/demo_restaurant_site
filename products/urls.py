
from django.contrib import admin
from django.urls import path

from .views import (ProductListView,
                            #product_list_view,
                            #ProductDetailView,
                            #product_detail_view,
                            #ProductFeaturedListView,
                            #ProductFeaturedDetailView,
                            ProductDetailSlugView
                            )

urlpatterns = [

    path('',ProductListView.as_view(),name='list'),
    #path('products-fbv/',product_list_view,name='product-fbv'),
    #path('products/<pk>/',ProductDetailView.as_view()),
    #path('products-fbv/<pk>/', product_detail_view, name='product-fbv-detail'),
    #path('featured/',ProductFeaturedListView.as_view()),
    #path('featured/<pk>/',ProductFeaturedDetailView.as_view()),
    path('<slug>/',ProductDetailSlugView.as_view(),name='detail'),

]
