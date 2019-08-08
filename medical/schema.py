import re
from django.db.models import Q
import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from .models import Item, Service


class ItemGQLType(DjangoObjectType):
    class Meta:
        model = Item
        filter_fields = {
            'id': ['exact'],
            'code': ['exact', 'icontains', 'istartswith'],
            'name': ['exact', 'icontains', 'istartswith'],
        }
        filter_fields = ()
        interfaces = (graphene.relay.Node,)


class ServiceGQLType(DjangoObjectType):
    class Meta:
        model = Service
        filter_fields = {
            'id': ['exact'],
            'code': ['exact', 'icontains', 'istartswith'],
            'name': ['exact', 'icontains', 'istartswith'],
        }
        interfaces = (graphene.relay.Node,)


class Query(graphene.ObjectType):
    medical_items = DjangoFilterConnectionField(
        ItemGQLType,
        qry=graphene.String()
    )

    medical_services = DjangoFilterConnectionField(
        ServiceGQLType,
        qry=graphene.String()
    )

    def resolve_medical_items(self, info, **kwargs):
        qry = kwargs.get('qry')
        if qry is not None:
            return Item.objects.filter(
                Q(code__icontains=qry) | Q(name__icontains=qry)
            )
        else:
            # TODO: pagination
            return Item.objects.all()

    def resolve_medical_services(self, info, **kwargs):
        qry = kwargs.get('qry')
        if qry is not None:
            return Service.objects.filter(
                Q(code__icontains=qry) | Q(name__icontains=qry)
            )
        else:
            # TODO: pagination
            return Service.objects.all()
