from rest_framework import serializers
from django.urls import reverse
from ..cart import Cart
from product.models import Product, Option
from product.api.serializers import OptionSerialzer, ProductSerializer
import logging

logger = logging.getLogger(__name__)

class CartListSerializer(serializers.ListSerializer):
    """custome update for cart using ListSerializer as child for CartDetailSerializer

    Args:
        serializers (MODULE): DRF built-in module to serialize data
    """    
    def update(self, instance, validated_data):
        # the_cart = Cart(self.context['request'])
        cart_product_id = {item.get("product_id"): item for item in instance}
        validate_product_id = {item.get('product_id'): item for item in validated_data}
        for product_id, data in validate_product_id.items():
            product = cart_product_id.get(product_id)

            # create new data from entered data
            try:
                data_c = {}
                data_c["amount"] = data.get('amount')
                data_c["option_title"] = [k for k in data.get('customization').keys()]
                data_c["option_custom"] =[int(v) for v in data.get('customization').values()]
                # check if the product id changed get the new one
                prod_id = data.get('product_id') if product is None else product.get('product_id')
                serializer = CartSerializer(data=data_c ,context={"request":self.context['request'], 
                                                                "product_id": prod_id})
                if serializer.is_valid():
                    serializer.save()
                else:
                    serializer.is_valid(raise_exception=True)
                    logger.error(str(serializer.errors))
            except (KeyError, AttributeError) as e:
                logger.warning(str(e))


        # remove products from cart that are not in the entered data
        for product_id, cart in cart_product_id.items():
            if not product_id in validate_product_id:
                serializer = CartDeleteSerializer(data=cart, context={"request":self.context['request'], 
                                                                "product_id": product_id})
                if serializer.is_valid():
                    serializer.delete()
                else:
                    serializer.is_valid(raise_exception=True)
                    logger.error(str(serializer.errors))

        return self.data



class CartDetailSerializer(serializers.Serializer):
    """only to show specific data in the Cart

    Args:
        serializers (MODULE): DRF built-in module to serialize data

    """    
    product_id = serializers.IntegerField(required=False)
    product_title = serializers.CharField(required=False)
    amount = serializers.IntegerField(required=False)
    product_price = serializers.IntegerField(required=False)
    total_price = serializers.IntegerField(required=False)
    customization = serializers.DictField(child=serializers.CharField(), required=False)

    class Meta:
        list_serializer_classe = CartListSerializer

    @classmethod
    def many_init(cls, *args, **kwargs):
        # Instantiate the child serializer.
        kwargs['child'] = cls()
        # Instantiate the parent list serializer.
        return CartListSerializer(*args, **kwargs)




class CartSerializer(serializers.Serializer):
    amount = serializers.IntegerField(required=False)
    option_title = serializers.ListField(child=serializers.CharField(), required=False)
    option_custom = serializers.ListField(child=serializers.IntegerField(), required=False)



    def validate(self, value):
        try:
            self._product = Product.objects.get(id=int(self.context['product_id']))
        except Product.DoesNotExist:
            raise serializers.ValidationError("There is no Product with this id")
        if value.get('option_title'):
            options = Option.objects.filter(product=self._product, title__in=value['option_title'])
            if not options.exists():
                raise serializers.ValidationError("There is no Title-Option with this title")

        if value.get("option_custom"):
            for option in options:
                if not option.customazition.filter(id__in=value['option_custom']):
                    raise serializers.ValidationError("There is no Option with this id")

        return value


    def create(self, validated_data):
        cart = Cart(self.context['request'])
        title = validated_data.get('option_title')
        custom = validated_data.get('option_custom')
        customization = {}
        if title and custom:
            for k, v in zip(title, custom):
                customization[str(k)] = v
        cart.add(self._product, customization, validated_data.get('amount'))
        return validated_data


class CartDeleteSerializer(serializers.Serializer):
    def validate(self, value):
        cart = Cart(self.context['request'])
        try:
            self._product = Product.objects.get(id=int(self.context['product_id']))
            if not self._product.id in [item['product']['id'] for item in cart]:
                raise serializers.ValidationError("This product is not in your cart")

        except Product.DoesNotExist:
            raise serializers.ValidationError("There is no Product with this id")

        return value
    
    def delete(self):
        cart = Cart(self.context['request'])
        cart.remove([self._product.id,])
        return cart
