from django.shortcuts import render
from rest_framework.decorators import api_view,APIView, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User, Group
from django.db import transaction
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

    manager = Group.objects.get(name="Manager")

    item =get_object_or_404(models.MenuItem,pk=id)

    if request.method == 'GET':
        serialized_items = serializers.MenuItemSerializer(item)
        return Response(serialized_items.data, status=status.HTTP_200_OK)
    
    if request.method in ['PUT', 'PATCH', 'DELETE']:
         if not manager:
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
         

@api_view(['GET','POST','DELETE'])
@permission_classes([IsAuthenticated])
def cart_view(request):

    customer = request.user.groups.filter(name = "Customer").exists()
    
    # only for customers
    if not customer:
        return Response({'message': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
    
    user_id = request.user.id
    # cart_items = get_object_or_404(models.Cart,user = user_id)
    cart_items = models.Cart.objects.filter(user = user_id)

    if request.method == "GET":
        serialized_cart = serializers.CartSerializer(cart_items, many=True)
        return Response(serialized_cart.data, status= status.HTTP_200_OK)

    
    elif request.method == "POST":
        serialized_items = serializers.CartSerializer(data = request.data, context={'request': request})
        serialized_items.is_valid(raise_exception=True)
        serialized_items.save()
        return Response(serialized_items.data, status= status.HTTP_201_CREATED)
    
    elif request.method == 'DELETE':

        delete_count, _ = models.Cart.objects.filter(user = user_id).delete()
        if delete_count == 0:
            return Response(
                {"message": "No items were found in your cart."},
                status=status.HTTP_200_OK
            )
        return Response(
            {"message": f"{delete_count} items deleted from your cart."},
            status=status.HTTP_200_OK
        )
         



@api_view(['GET','POST','PUT','PATCH','DELETE'])
@permission_classes([IsAuthenticated])
def orders_view(request):
    
    group = Group.objects.get(user = request.user.id).name

    if group == "Manager":
        orders = models.Order.objects.all()
    elif group == "Delivery-Crew":
        orders = models.Order.objects.filter(delivery_crew = request.user.id)
        
    else:
        orders = models.Order.objects.filter(user = request.user.id)


    if request.method == 'GET':
        serializered_item = serializers.OrderSerializer(orders, many = True)
        return Response(serializered_item.data, status= status.HTTP_200_OK)


    
    if request.method == 'POST':
       
        if group != 'Customer':
            return Response({"message": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        
        cart_items = models.Cart.objects.filter(user = request.user.id)

        if not cart_items.exists():
                return Response({"message":"No item in cart" }, status= status.HTTP_404_NOT_FOUND)
        
        total_price = 0
            
        for item in cart_items:
                total_price += item.price

        with transaction.atomic():
            # new order
            order = models.Order.objects.create( user = request.user, total = total_price)

            # orderItems

            order_item = []
            for cart_item in cart_items:
                order_item.append(models.OrderItem(
                    order = order,
                    menuitem = cart_item.menuitem,
                    quantity = cart_item.quantity,
                    unit_price = cart_item.menuitem.price,
                    price = cart_item.price
                ))
            
            models.OrderItem.objects.bulk_create(order_item)

            #clear cart

            cart_items.delete()

        serializer = serializers.OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED) 
             


@api_view(['GET','DELETE','PUT','PATCH'])
@permission_classes([IsAuthenticated])
def order_view_single(request, orderId = None):
    user = request.user
    order = get_object_or_404(models.Order, pk = orderId)

    group = Group.objects.get(user = request.user.id).name

    if request.method == 'GET':

        if group == 'Customer':
            serialized_order = serializers.OrderSerializer(order)
            return Response(serialized_order.data, status= status.HTTP_200_OK)

    if request.method == 'DELETE':

        if group != "Manager":
            return Response({"message" : "Not Allowed"}, status= status.HTTP_401_UNAUTHORIZED)
        order.delete()
        return Response({"message":"Order deleted"}, status= status.HTTP_204_NO_CONTENT)
    
    if request.method in ["PUT","PATCH"]:
        if group == "Manager":
            serialized_order = serializers.OrderSerializer(order, data = request.data , partial = True) 
            if serialized_order.is_valid():
                serialized_order.save()
                return Response(serialized_order.data,status=status.HTTP_201_CREATED)
            return Response(serialized_order.errors, status=status.HTTP_400_BAD_REQUEST)
        elif group == "Delivery-Crew":
            status_value = request.data.get("status")
            if status_value not in [0, 1]:
                return Response({"message": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)
            order.status = status_value
            order.save()
            return Response({"status": order.status})
        else:
            return Response({"message": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
