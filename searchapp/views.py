from django.shortcuts import render
from django.db.models import Q
from products.models import Product
from django.views.generic import ListView, DetailView


# Create your views here.
class SearchProductView(ListView):
    template_name = "searchapp/view.html"

    def get_context_data(self, *args, **kwargs):
        context = super(SearchProductView,self).get_context_data(*args,**kwargs)
        query = self.request.GET.get('q')
        context['query'] = query
        # SearchQuery.objects.create(query = query)
        return context

    def get_queryset(self,*args,**kwargs):
        request = self.request
        #return Product.objects.all()
        print(request.GET)
        # request.GET actually gives a dict values and we need to search from that
        # the url sytle is "..../search/?q='veg' " so after the q= whatever gets in is the searching word
        # that will take the value and is passed in to check if it is present in dict
        # method_dict = request.GET
        # query = method_dict.get('q',None) #its basically method_dict['q']

        query = request.GET.get('q')
        if query is not None:
            #lookups = Q(title__icontains=query) | Q(description__icontains = query)
            #return Product.objects.filter(lookups).distinct()
            return Product.objects.search(query)
        return Product.objects.featured()
        #return Product.objects.filter(title_iexact="biry")