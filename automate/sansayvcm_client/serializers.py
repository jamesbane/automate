from rest_framework import serializers

class VcmRouteMetadataSerializer(serializers.Serializer):
    inventory_item_id = serializers.IntegerField(required=True, min_value=0)
    status = serializers.CharField(required=True, max_length=32)
    inventory_type_id = serializers.IntegerField(required=True, min_value=0)
    identifier = serializers.CharField(required=True, max_length=64)
    customer_id = serializers.IntegerField(required=True, min_value=1)

class VcmRouteSerializer(serializers.Serializer):
    event_id = serializers.IntegerField(required=True, min_value=0)
    event_type = serializers.CharField(required=True, max_length=32)
    created_date = serializers.CharField(required=True, max_length=32)
    object_id = serializers.IntegerField(required=True, min_value=0)
    metadata = serializers.DictField(child=serializers.CharField())
