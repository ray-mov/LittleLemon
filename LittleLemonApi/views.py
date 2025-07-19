from django.shortcuts import render
from rest_framework.decorators import api_view,APIView, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User, Group
from . import models
from . import serializers
# Create your views here.


# Class Based View For Catergory

class CategoryList(APIView):
    def get(self, request):
        categories = models.Category.objects.all() 
        serialized_category = serializers.CategorySerializer(categories, many = True)
        return Response(serialized_category.data)
    
    def post(self, request):
        serialized_category = serializers.CategorySerializer(data = request.data)
        if serialized_category.is_valid():
            serialized_category.save()
            return Response(serialized_category.data, status= status.HTTP_201_CREATED)
        return Response(serialized_category.errors, status= status.HTTP_400_BAD_REQUEST)


#views for manager

@api_view(['POST','GET','DELETE'])
@permission_classes([IsAdminUser])
def ManagerView(request):
    try:
        manager = Group.objects.get(name="Manager")
    except Group.DoesNotExist:
        return Response({"error": "Manager group does not exist"}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':      
        users = manager.user_set.all()
        serialized_users =  serializers.UserGroupSerializer(users, many=True)
        return Response(serialized_users.data)
    
    username = request.data.get('username')
    if username:
        user = get_object_or_404(User, username = username)
        
        if request.method == 'POST':
            manager.user_set.add(user)
            message = "User added to group"
        elif request.method == 'DELETE':
            manager.user_set.remove(user)
            message = "User deleted"
        return Response({"message": message })
    return Response({"message ": "error"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST','GET','DELETE'])
@permission_classes([IsAdminUser])
def DeliveyCrewView(request):
    try:
        delivery_crew = Group.objects.get(name="Delivery-Crew")
    except Group.DoesNotExist:
        return Response({"error": "Delivery-Crew group does not exist"}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':      
        users = delivery_crew.user_set.all()
        serialized_users =  serializers.UserGroupSerializer(users, many=True)
        return Response(serialized_users.data)
    
    username = request.data.get('username')
    if username:
        user = get_object_or_404(User, username = username)
        
        if request.method == 'POST':
            delivery_crew.user_set.add(user)
            message = "User added to group"
        elif request.method == 'DELETE':
            delivery_crew.user_set.remove(user)
            message = "User deleted"
        return Response({"message": message })
    return Response({"message ": "error"}, status=status.HTTP_400_BAD_REQUEST)

# @api_view()
# @permission_classes([IsAuthenticated])
# def ManagerView(request):
#     if request.user.groups.filter(name="Manager").exists():
#         return Response('only manager', status=status.HTTP_200_OK)
#     else:
#         return Response('not manager', status=status.HTTP_200_OK)




# You are serializing a list (queryset) of items, not just one object.
# many = True

@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def menu_items(request):
    
    
    if request.method == 'GET':
        items = models.MenuItem.objects.select_related('category').all()
        serialized_items = serializers.MenuItemSerializer(items, many = True)
        return Response(serialized_items.data, status= status.HTTP_200_OK)
    
    
    if request.method == 'POST':
        # only manager
        manager = Group.objects.get(name="Manager")
        if not manager:
             return Response({'message':'access denied'}, status= status.HTTP_403_FORBIDDEN)

        serialized_items = serializers.MenuItemSerializer(data = request.data)
        serialized_items.is_valid(raise_exception=True)
        serialized_items.save()
        return Response(serialized_items.data, status= status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def menu_item_single(request,id):

    user_role = request.user.role
    item =get_object_or_404(models.MenuItem.objects.get(pk=id))

    if request.method == 'GET':
        serialized_items = serializers.MenuItemSerializer(item)
        return Response(serialized_items.data, status=status.HTTP_200_OK)
    
    if request.method in ['PUT', 'PATCH', 'DELETE']:
         if user_role != 'Manager':
            return Response({'message': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
         
         if request.method in ['PUT', 'PATCH']:
            serializer =serializers.MenuItemSerializer(item, data=request.data, partial=(request.method == 'PATCH'))
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
         
         if request.method == 'DELETE':
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)