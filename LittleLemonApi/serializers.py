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
    class Meta:
        medel = models.MenuItem
        category = CategorySerializer(read_only =True)
        category_id = serializers.IntegerField(write_only = True)
        fields = ['id','title','price','featured','category','category_id']


class UserGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ['id','username','email']