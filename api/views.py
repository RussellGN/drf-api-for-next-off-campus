from django.utils.text import slugify
from django.shortcuts import get_object_or_404 
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status 
from rest_framework.authtoken.models import Token
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from .models import Lister, Listing, Image
from .serializers import ListerSerializer, ListingSerializer, ListingCreationSerializer, ListerCreationSerializer

@api_view(['GET'])
def index(request):
   endpoints = [
      {
         'route': 'api/',
         'method': 'GET',
         'data': None,
         'query_params': None,
         'authorisation': None,
         'response': 'a list of all api endpoints',
         'response_format': '{endpoint}',
      },
      {
         'route': 'api/listings/',
         'method': 'GET',
         'data': None,
         'query_params': 'query, sort, page, rent, city, type',
         'authorisation': None,
         'response': 'a list of accomodation listings',
         'response_format': '{listings, query_params}',
      },
      {
         'route': 'api/listings/',
         'method': 'POST',
         'data': '{title, rent, location, nearest_to, distance, accomodation_type, description, images}',
         'query_params': None,
         'authorisation': 'authenticated',
         'response': 'listing details',
         'response_format': '{message, listing}',
      },
      {
         'route': 'api/listings/<slug>',
         'method': 'GET',
         'data': None,
         'query_params': None,
         'authorisation': None,
         'response': 'listing details',
         'response_format': '{listing, related_listings}',
      },
      {
         'route': 'api/listings/<slug>',
         'method': 'PATCH',
         'data': '{title, rent, location, nearest_to, distance, accomodation_type, description, images, deleted_image_ids}',
         'query_params': None,
         'authorisation': 'authenticated',
         'response': 'listing details',
         'response_format': '{message, listing}',
      },
      {
         'route': 'api/listings/<slug>',
         'method': 'DELETE',
         'data': None, 
         'query_params': None,
         'authorisation': 'authenticated',
         'response': 'success message',
         'response_format': '{message}',
      },
      {
         'route': 'api/auth/signup/',
         'method': 'POST',
         'data': '{username, email, password, contact_details, lister_type}', 
         'query_params': None,
         'authorisation': None,
         'response': 'user details',
         'response_format': '{message, token, user}',
      },
      {
         'route': 'api/auth/login/',
         'method': 'POST',
         'data': '{email, password}', 
         'query_params': None,
         'authorisation': None,
         'response': 'user details',
         'response_format': '{message, token, lister}',
      },
      {
         'route': 'api/auth/<id>',
         'method': 'GET',
         'data': None, 
         'query_params': None,
         'authorisation': 'authenticated',
         'response': 'user details',
         'response_format': '{lister, lister_listings}',
      },
      {
         'route': 'api/auth/<id>',
         'method': 'PATCH',
         'data': '{username, contact_details, lister_type}', 
         'query_params': None,
         'authorisation': 'authenticated',
         'response': 'user details',
         'response_format': '{message, lister}',
      },
   ]
   return Response(endpoints)

# ________________AUTH CRUD_________________

@api_view(['POST'])
def signup(request):
   serializer = ListerCreationSerializer(data=request.data)
   if not request.data['password']:
      return Response({'detail': 'registration failed',}, status=status.HTTP_400_BAD_REQUEST)

   if serializer.is_valid():
      serializer.save()
      lister = Lister.objects.get(email=request.data['email']) 
      lister.set_password(request.data['password'])
      lister.save()
      token = Token.objects.create(user=lister)
      return Response({'message': 'registration successful', 'token': token.key, 'lister': serializer.data}, status=status.HTTP_201_CREATED)
   return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def signup_old(request):
   serializer = ListerSerializer(data=request.data)
   if not request.data['password']:
      return Response({'detail': 'registration failed',}, status=status.HTTP_400_BAD_REQUEST)

   if serializer.is_valid():
      serializer.save()
      lister = Lister.objects.get(username=request.data['username']) 
      lister.set_password(request.data['password'])
      lister.save()
      token = Token.objects.create(user=lister)
      return Response({'message': 'registration successful', 'token': token.key, 'lister': serializer.data}, status=status.HTTP_201_CREATED)
   return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
   
@api_view(['POST'])
def login(request):
   lister = get_object_or_404(Lister, email=request.data['email'])
   correctPassword = lister.check_password(request.data['password'])   

   if (correctPassword):
      (token, created) = Token.objects.get_or_create(user=lister)
      serializer = ListerSerializer(instance=lister)
      return Response({'message': 'login successful', 'token': token.key, 'lister': serializer.data})
   else:
      return Response({'detail': 'not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET', 'PATCH'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def profile(request):
   lister = request.user
   if (request.method == 'GET'):
      lister_serializer = ListerSerializer(instance=lister)
      listings = Listing.objects.filter(lister=lister).order_by('-date')
      listings_serializer = ListingSerializer(instance=listings, many=True)
      return Response({'lister': lister_serializer.data, 'lister_listings': listings_serializer.data})
   else:
      data = {
         'contact_details': request.data.get('contact_details') if request.data.get('contact_details') else lister.contact_details,
         'lister_type': request.data.get('lister_type') if request.data.get('lister_type') else lister.lister_type,
         'username': request.data.get('username') if request.data.get('username') else lister.username,
         'email': lister.email,
      }
      lister_serializer = ListerSerializer(instance=lister, data=data, )
      if lister_serializer.is_valid():
         lister_serializer.save()
         return Response({'message': 'details updated successfully', 'lister': lister_serializer.data})
      return Response({'error': lister_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


# ________________listings CRUD_________________

@api_view(['GET', 'POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticatedOrReadOnly])
def listings(request):
   if request.method == 'GET':
         query_params = request.GET
         print(query_params)
         listings = Listing.objects.all().order_by('-date')
         serializer = ListingSerializer(instance=listings, many=True)
         return Response({'listings': serializer.data})
   else:
      data = {
         'lister': request.user,
         'title': request.data.get('title'),
         'rent': request.data.get('rent'),
         'location': request.data.get('location'),
         'nearest_to': request.data.get('nearest_to'),
         'distance': request.data.get('distance'),
         'description': request.data.get('description'),
         'accomodation_type': request.data.get('accomodation_type'),
      }

      images = request.FILES.getlist('images')

      print(data, images)

      serializer = ListingCreationSerializer(data=data)
      if serializer.is_valid():
         # serializer.save()
         listing = Listing.objects.create(
            lister=request.user,
            title=request.data.get('title'),
            rent=request.data.get('rent'),
            location=request.data.get('location'),
            nearest_to=request.data.get('nearest_to'),
            distance=request.data.get('distance'),
            description=request.data.get('description'),
            accomodation_type=request.data.get('accomodation_type'),
         )
         listing.slug = slugify(listing.title + '-' + str(listing.id))
         listing.save()
         for image in images:
            Image.objects.create(listing=listing, image=image)

         listing = Listing.objects.get(slug=listing.slug)
         serializer = ListingSerializer(instance=listing)
         return Response({'message': 'listing creation successful', 'listing': serializer.data}, status=status.HTTP_201_CREATED)
      return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'DELETE', 'PATCH' ])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticatedOrReadOnly])
def listing(request, slug):
   listing = get_object_or_404(Listing, slug=slug)

   if request.method == 'GET':
      related_listings = Listing.objects.filter(lister=listing.lister).exclude(id=listing.id).order_by('-date')
      related_listings_serializer = ListingSerializer(instance=related_listings, many=True)
      serializer = ListingSerializer(instance=listing)

      return Response({'listing': serializer.data, 'related_listings': related_listings_serializer.data})

   elif request.method == 'DELETE':
      listing.delete()
      return Response({'message': 'listing deleted successfully'})

   else:
      data = {
         'title': request.data.get('title') if request.data.get('title') else listing.title,
         'rent': request.data.get('rent') if request.data.get('rent') else listing.rent,
         'location': request.data.get('location') if request.data.get('location') else listing.location,
         'nearest_to': request.data.get('nearest_to') if request.data.get('nearest_to') else listing.nearest_to,
         'distance': request.data.get('distance') if request.data.get('distance') else listing.distance,
         'description': request.data.get('description') if request.data.get('description') else listing.description,
         'accomodation_type': request.data.get('accomodation_type') if request.data.get('accomodation_type') else listing.accomodation_type,
      }

      # deleted_image_ids = request.FILES.get('deleted_image_ids', [])
      deleted_image_ids = request.data.get('deleted_image_ids')
      new_images = request.FILES.getlist('images')

      print(data, deleted_image_ids, new_images)


      serializer = ListingCreationSerializer(instance=listing, data=data)
      if serializer.is_valid():
         serializer.save()
         listing = Listing.objects.get(slug=slug)
         listing.slug = slugify(listing.title + '-' + str(listing.id))
         listing.save()

         for new_image in new_images:
            Image.objects.create(listing=listing, image=new_image)

         if deleted_image_ids:
            deleted_image_ids = deleted_image_ids.strip().split(',')
            for id in deleted_image_ids:
               # Image.objects.delete(id= int(id)) 
               Image.objects.get(id= int(id)).delete() 

         listing = Listing.objects.get(slug=listing.slug)
         serializer = ListingSerializer(instance=listing)
         return Response({'message': 'listing updated successfully', 'listing': serializer.data})
      return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


