from rest_framework import serializers
from ..models import Product, Option, Customazition


class CustomeSerialzer(serializers.ModelSerializer):
    class Meta:
        model = Customazition
        fields = "__all__"

class OptionSerialzer(serializers.ModelSerializer):
    customazition = CustomeSerialzer(many=True)
    class Meta:
        model = Option
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='api:product-detail')
    option = OptionSerialzer(many=True, required=False)
    class Meta:
        model = Product
        fields = "__all__"