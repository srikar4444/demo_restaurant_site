from django.shortcuts import render, get_object_or_404
#from django.views import ListView
from django.views.generic import ListView, DetailView
from .models import Product
from django.http import Http404
from carts.models import Cart
#from analytics.signals import object_viewed_signal
from analytics.mixins import ObjectViewedMixin
# Create your views here.

# for signal sending in DetailView functions we have get_object method and we can use that but
# for list view we don't have get_object function


# this is the class that is used finally to display all the product items on a single page
class ProductListView(ListView):
    queryset = Product.objects.all()
    template_name = "products/list.html"

    #def get_context_data(self, *args, **kwargs):
    #    context = super(ProductListView,self).get_context_data(*args,**kwargs)
    #    print(context)
    #    return context

    def get_context_data(self,*args, **kwargs):
        context = super(ProductListView,self).get_context_data(*args, **kwargs)
        request = self.request
        cart_obj, new_obj = Cart.objects.new_or_get(request)
        # the 'cart' in context is actually used in the html pages of detail and update-cart
        context['cart'] = cart_obj
        return context

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.all()


#the above view class (ProductListView) is same as this function view
def product_list_view(request):
    queryset = Product.objects.all()
    context = {
        'object_list' : queryset
    }
    return render(request,'products/list.html',context)



class ProductDetailView(ObjectViewedMixin, DetailView):
    queryset = Product.objects.all()
    template_name = "products/detail.html"

    def get_context_data(self, *args, **kwargs):
        context = super(ProductDetailView,self).get_context_data(*args,**kwargs)
        print(context)
        return context

    def get_object (self, *args, **kwargs):
        request = self.request
        pk = self.kwargs.get('pk')
        instance = Product.objects.get_by_id(pk)
        print(instance)
        if(instance is None):
            return Http404("Product doesnot exist")
        return instance

    #def get_queryset(self, *args, **kwargs):
    #    request = self.request
    #    pk = self.kwargs.get('pk')
    #    return Product.objects.filter(pk=pk)

# the above class ProductDetailView is same as the below function
def product_detail_view(request, pk=None,*args,**kwargs):
    #instance = Product.objects.get(pk= pk) #id
    #instance = get_object_or_404(Product,pk=pk)
    """
    try:
        instance = Product.objects.get(id=pk)
    except Product.DoesNotExist:
        print('No product here')
        raise Http404("Product doesn't exist")
    except:
        print("huh?")

    context = {
        'object' : instance
    }
    """
    #qs = Product.objects.filter = (id == pk)
    #print(qs)
    #if (qs.exists() and qs.count() ==1):
    #    install = qs.front
    #else :
    #    raise HTTP("product doesnot exist")

    instance = Product.objects.get_by_id(pk)
    if instance is None:
        return Http404("Product doesnot exist")

    context = {
        'object' : instance
    }
    return render(request, "products/detail.html",context)

    #return render(request,"products/detail.html",context)


class ProductFeaturedListView(ListView):

    template_name = "products/list.html"

    def get_queryset(self,*args,**kwargs):
        request = self.request
        #return Product.objects.featured()
        return Product.objects.all().featured()


class ProductFeaturedDetailView(ObjectViewedMixin, DetailView):
    template_name = "products/featured_detail.html"

    def get_queryset(self,*args,**kwargs):
        request = self.request
        return Product.objects.all().featured()

# this is the class or function that is finally used in this for a single product view
# all are designed for time being
class ProductDetailSlugView(ObjectViewedMixin, DetailView):
    queryset = Product.objects.all()
    template_name = "products/detail.html"

    def get_context_data(self,*args, **kwargs):
        context = super(ProductDetailSlugView,self).get_context_data(*args, **kwargs)
        request = self.request
        cart_obj, new_obj = Cart.objects.new_or_get(request)
        # the 'cart' in context is actually used in the html pages of detail and update-cart
        context['cart'] = cart_obj
        return context

    def get_object(self, *args, **kwargs):
        request = self.request
        slug = self.kwargs.get('slug')

        #instance = get_object_or_404(Product, slug=slug,available= True )
        try:
            instance = Product.objects.get(slug = slug, available= True)
        except Product.DoesNotExist:
            raise Http404 ("Not found..How was your day?")
        except Product.MultipleObjectsReturned:
            qs = Product.objects.filter(slug= slug,available = True)
            instance = qs.first()
        except:
            raise Http404("What's on your mind currently? ")

        # as this is a signal we need to have a sender so here the sender is the instance of the class
        # as instance is created before this we are using this
        # if this is a function it has to be designed again and again
        # but as this is a class based view we can use ObjectMixin
        # object_viewed_signal.send(instance.__class__, instance= instance, request= request)
        return instance