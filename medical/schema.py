import re
from django.db.models import Q
import graphene
from graphene_django import DjangoObjectType
from .models import Item, Service


class ItemGraphQLType(DjangoObjectType):
    class Meta:
        model = Item


class ServiceGraphQLType(DjangoObjectType):
    class Meta:
        model = Service


class Query(graphene.ObjectType):
    medical_items = graphene.List(
        ItemGraphQLType,
        qry=graphene.String()
    )

    medical_services = graphene.List(
        ServiceGraphQLType,
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
