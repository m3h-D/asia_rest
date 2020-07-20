from rest_framework import serializers
from ..models import Order, OrderItems, LOCATION
from user.api.serializers import UserSerializer
from product.api.serializers import ProductSerializer
from product.models import Product
from cart.cart import Cart


class OrderItemSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField('api:orderitems-detail')
    product = serializers.IntegerField(source="product.id")

    class Meta:
        model = OrderItems
        fields = ('id', 'url', 'amount', 'product', 'customizations',)
        # read_only_fields = ('id', 'url', 'order', 'total_price',)

class OrderItemDetailSerializer(OrderItemSerializer):
    class Meta(OrderItemSerializer.Meta):
        fields = ('amount', 'order', 'product', 'customizations', 'total_price',)



class OrderSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField("api:order-detail")
    user = UserSerializer(read_only=True)
    orderitems = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        exclude = ("updated_date", )
        read_only_fields = ('id', 'orderitems', 'total_price', 'url', 'status', )

    def create(self, validated_data):
        order = Order.objects.get_or_create_order(self.context['request'], validated_data.get("consume_location"))
        return order



class OrderDetailSerializer(OrderSerializer):
    url = None
    orderitems = OrderItemSerializer(many=True)

    class Meta(OrderSerializer.Meta):
        read_only_fields = ('id', 'total_price', 'url', 'status', )

    def validate(self, value):
        if self.instance.status != 'waiting': # validate status
            raise serializers.ValidationError({"Update_condition": "You cannot update/edit your order now"})
        # if value.get('consume_location') not in [i[0] for i in LOCATION]: # validate consume location
        #     raise serializers.ValidationError({"Location": "Invalid consume location"})
        # print(value)
        if value.get('orderitems'):
            for i, item in enumerate(self.instance.orderitems.all()): # validate customazition
                custome = value['orderitems'][i].get('customizations')
                if custome and custome != {}:
                    for title, customazition in custome.items():
                        if not item.product.option.filter(title=title).exists():
                            raise serializers.ValidationError({"Option_title": "Invalid option title"})
                        if not item.product.option.filter(customazition__c_option=customazition).exists():
                            raise serializers.ValidationError({"Option_customazition": "Invalid customazition value"})

        return value

    def update(self, instance, validated_data):
        instance.consume_location = validated_data.get("consume_location", instance.consume_location)
        instance.canceled = validated_data.get('canceled')
        if validated_data.get('orderitems'):
            for i, item in enumerate(instance.orderitems.all()):
                item.product.id = validated_data['orderitems'][i]['product']['id']
                item.amount = validated_data['orderitems'][i]['amount']
                item.customizations = validated_data["orderitems"][i]["customizations"]
                item.save()
        instance.save()
        return instance