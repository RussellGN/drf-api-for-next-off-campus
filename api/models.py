from django.db import models
from django.contrib.auth.models import AbstractUser

class Lister(AbstractUser):
   username = models.CharField(unique=True, max_length=30)
   email = models.EmailField(unique=True, max_length=100)
   contact_details = models.CharField(max_length=100)
   lister_type_choices = (
      ('A', 'Agent'),
      ('L', 'Landlord'),
   )
   lister_type = models.CharField(max_length=1, choices=lister_type_choices, default='A')

   def __str__(self):
      return self.username

class Listing(models.Model):
   lister = models.ForeignKey(Lister, related_name='listings', on_delete=models.CASCADE, null=True, blank=True)
   title = models.CharField(max_length=30)
   slug = models.SlugField(unique=True, blank=True, null=True)
   rent = models.DecimalField(max_digits=6, decimal_places=2)
   location = models.CharField(max_length=50)
   nearest_to = models.CharField(max_length=50)
   patents_needed = models.PositiveIntegerField(default=0)
   view_count = models.PositiveIntegerField(default=0)
   distance = models.PositiveIntegerField()
   description = models.TextField(max_length=500, null=True, blank=True)
   date = models.DateTimeField(auto_now=True)
   accomodation_type_choices = (
      ('boarding', 'Boarding House'),
      ('cottage', 'Cottage'),
      ('apartment', 'Apartment'),
      ('house', 'House'),
      ('room', 'Room'),
      ('other', 'Other'),
   )
   accomodation_type = models.CharField(max_length=15, choices=accomodation_type_choices, default='boarding')

   def __str__(self):
      return self.title

class Image(models.Model):
   listing = models.ForeignKey(Listing, related_name='images', on_delete=models.CASCADE, null=True, blank=True)
   image = models.ImageField(upload_to='listing_images')