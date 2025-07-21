from rest_framework import serializers
from . import models

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = ['id','slug','title']

    def validate(self, data):
        slug = data.get('slug')
        title = data.get('title')

        if models.Category.objects.filter(slug=slug).exists():
            raise serializers.ValidationError({"slug": "This slug is already exist"})

        if models.Category.objects.filter(title=title).exists():
            raise serializers.ValidationError({"title":"This title is already exists"})
        
        return data

# class MenuItemSerializer(serializers.Serializer):
#     id =serializers.IntegerField()
#     title = serializers.CharField(max_length = 255)
#     price = serializers.DecimalField(max_digits=6, decimal_places=2)
#     featured = serializers.BooleanField()  
#     category = CategorySerializer()


class MenuItemSerializer(serializers.ModelSerializer):

    # Show category name in GET response
    category = serializers.CharField(source='category.title', read_only=True)
    
    # Allow setting category by ID in POST/PUT
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=models.Category.objects.all(),
        source='category',
        write_only=True
    )

    class Meta:
        model = models.MenuItem
        # category = CategorySerializer(read_only =True)
        # category_id = serializers.IntegerField(write_only = True)
        fields = ['id','title','price','featured','category','category_id']


class UserGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ['id','username','email']


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Cart
        fields = ['id','user','menuitem','quantity','price']
        read_only_fields = ['id','user','price']

    def create(self, validated_data):
            user = self.context['request'].user
            validated_data['user'] = user
            menuitem = validated_data['menuitem']
            quantity = validated_data['quantity']
            validated_data['price'] = menuitem.price * quantity
            return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'quantity' in validated_data:               
            instance.quantity = validated_data['quantity']
            instance.price = instance.menuitem.price * instance.quantity
        instance.save()
        return instance
        
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        return value
    





class OrderItemSerializer(serializers.ModelSerializer):
    menuitem = serializers.StringRelatedField()

    class Meta:
        model = models.OrderItem
        fields = ['order','menuitem','quantity','unit_price','price']


class OrderSerializer(serializers.ModelSerializer):
    
    order_items = OrderItemSerializer(source='orderitem_set',many= True, read_only =True)
    delivery_crew = UserGroupSerializer(read_only = True)

    delivery_crew_id = serializers.PrimaryKeyRelatedField(
        source='delivery_crew',
        queryset= models.User.objects.all(),
        required=False,
        allow_null=True,
        write_only=True
    )

    class Meta:
        model = models.Order
        fields = ['id','user','delivery_crew','delivery_crew_id','status','total','date','order_items']
        read_only_fields = ['id','user','total','date','order_items']