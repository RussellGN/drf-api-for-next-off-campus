from rest_framework.serializers import ModelSerializer
from .models import Lister, Listing, Image

class ListerSerializer(ModelSerializer):
   class Meta:
      model = Lister
      fields = ['id', 'username', 'email', 'contact_details', 'lister_type']

class ListerCreationSerializer(ModelSerializer):
   class Meta:
      model = Lister
      fields = ['id', 'email']

class ImageSerializer(ModelSerializer):
   class Meta:
      model = Image
      fields = ['id', 'image']
      
class ListingSerializer(ModelSerializer):
   lister = ListerSerializer(many=False, read_only=True)
   images = ImageSerializer(many=True, read_only=False)
   class Meta:
      model = Listing
      fields = [         
         'id',
         'lister',
         'title',
         'slug',
         'rent',
         'location',
         'nearest_to',
         'patents_needed',
         'view_count',
         'distance',
         'description',
         'date',
         'accomodation_type',
         'images',
         ]

class ListingCreationSerializer(ModelSerializer):
   lister = ListerSerializer(many=False, read_only=True)
   class Meta:
      model = Listing
      fields = [         
         'id',
         'lister',
         'title',
         'slug',
         'rent',
         'location',
         'nearest_to',
         'patents_needed',
         'view_count',
         'distance',
         'description',
         'date',
         'accomodation_type',
         ]

