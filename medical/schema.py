import graphene
from graphene_django import DjangoObjectType
from .models import Item, Service


class ItemType(DjangoObjectType):
    class Meta:
        model = Item
        exclude_fields = ('row_id',)


class ServiceType(DjangoObjectType):
    class Meta:
        model = Service
        exclude_fields = ('row_id',)


class Query(graphene.ObjectType):
    all_items = graphene.List(ItemType)
    all_services = graphene.List(ServiceType)

    def resolve_all_items(self, info, **kwargs):
        return Item.objects.all()

    def resolve_all_services(self, info, **kwargs):
        return Service.objects.all()
