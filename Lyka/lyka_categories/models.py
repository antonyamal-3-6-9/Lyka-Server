from django.db import models
from django.utils.text import slugify



class Root(models.Model):
    root_id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=50)
    root_slug = models.SlugField(max_length=50, unique=True)

    
    def __str__(self):
        return self.name
    

class Main(models.Model):
    main_id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=50)
    main_slug = models.SlugField(max_length=50,unique=True)
    root = models.ForeignKey(Root, on_delete=models.CASCADE)
    def __str__(self):
        return self.name
    


class Sub(models.Model):
    sub_id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=50)
    sub_slug = models.SlugField(max_length=50, unique=True)
    main = models.ForeignKey(Main, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
