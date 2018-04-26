from django.db import models
from django.db.models import Q
import random
import os
from django.urls import reverse

# Create your models here.
from restaurant_website.utils import unique_slug_generator
from django.db.models.signals import pre_save,post_save

def get_filename_ext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name,ext

def upload_image_path(instance,filename):
    print(instance)
    print(filename)
    new_filename = random.randint(1,100000)
    name, ext = get_filename_ext(filename)
    final_filename = '{new_filename}{ext}'.format(new_filename = new_filename, ext = ext)
    return "products/{new_filename}/{final_filename}".format(
        new_filename = new_filename,
        final_filename = final_filename)

class ProductQuerySetFeatured(models.query.QuerySet):
    # this is mentioned as ProductQuerySet in the website
    def featured(self):
        return self.filter(featured= True)

    def available(self):
        return self.filter(available = True)

    def search(self,query):
        lookups = (Q(title__icontains=query) |
                  Q(description__icontains=query) |
                  Q(price__icontains=query) |
                  Q(tag__title__icontains=query))
        # Q(tag__name__icontains=query)
        # veg-manchuria vegmanchuria or veg manchuria or manchuria or veg or some related search items all the different forms for an item should work
        return self.filter(lookups).distinct()

class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySetFeatured(self.model, using= self._db)

    def avail(self):
        return self.get_queryset().available()

    def featured(self):
        return self.get_queryset().featured()
        #the above line calls the ProductQuerySetFeatured class featured function

    def get_by_id(self,id):
        qs      = self.get_queryset().filter(id=id)
        if (qs.count()==1):
            return qs.first()
        return None
        # return self.get_queryset().filter(id=id)  #Product.objects self.get_queryset()

    def search(self,query):
        #lookups = Q(title__icontains=query) | Q(description__icontains=query)
        #return self.get_queryset().available().filter(lookups).distinct()
        #To send only the available items
        #return self.get_queryset().available().search(query)
        return self.get_queryset().search(query)

class Product(models.Model):
    title           = models.CharField(max_length=120)
    slug            = models.SlugField(blank=True, unique= True)
    description     = models.TextField()
    price           = models.DecimalField(decimal_places=2, max_digits=10,default = 999.99)
    #this image thing creates a folder 'products' in media_root folder
    image           = models.ImageField(upload_to=upload_image_path,null=True,blank=False)
    featured        = models.BooleanField(default = False)
    available       = models.BooleanField(default = False)
    timestamp      = models.DateTimeField(auto_now_add=True)
    # available thing is same as active in the example

    objects = ProductManager()

    def get_absolute_url(self):
        #in the website it is given as /products/{slug}/ but the '/products/' has to be removed in order to work here
        #return "{slug}/".format(slug = self.slug)
        return reverse("products:detail", kwargs={"slug":self.slug})


    def __str__(self):
        return self.title

    #from django 2.0 onwards __str__ is used not __unicode__ just mentioning the below one for practice
    def __unicode__(self):
        return self.title

    @property
    def name(self):
        return self.title

def product_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)

pre_save.connect(product_pre_save_receiver, Product)