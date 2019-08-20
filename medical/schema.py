import re
from django.db.models import Q
import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from .models import Diagnosis, Item, Service


class DiagnosisGQLType(DjangoObjectType):
    class Meta:
        model = Diagnosis
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            'id': ['exact'],
            'code': ['exact', 'icontains', 'istartswith'],
            'name': ['exact', 'icontains', 'istartswith'],
        }


class ItemGQLType(DjangoObjectType):
    class Meta:
        model = Item
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            'id': ['exact'],
            'code': ['exact', 'icontains', 'istartswith'],
            'name': ['exact', 'icontains', 'istartswith'],
        }


class ServiceGQLType(DjangoObjectType):
    class Meta:
        model = Service
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            'id': ['exact'],
            'code': ['exact', 'icontains', 'istartswith'],
            'name': ['exact', 'icontains', 'istartswith'],
        }


class Query(graphene.ObjectType):
    diagnoses = DjangoFilterConnectionField(DiagnosisGQLType)
    diagnoses_str = DjangoFilterConnectionField(
        DiagnosisGQLType,
        str=graphene.String()
    )
    medical_items = DjangoFilterConnectionField(ItemGQLType)
    medical_items_str = DjangoFilterConnectionField(
        ItemGQLType,
        str=graphene.String()
    )

    medical_services = DjangoFilterConnectionField(ServiceGQLType)
    medical_services_str = DjangoFilterConnectionField(
        ServiceGQLType,
        str=graphene.String()
    )

    def resolve_diagnoses_str(self, info, **kwargs):
        str = kwargs.get('str')
        if str is not None:
            return Diagnosis.objects.filter(
                Q(code__icontains=str) | Q(name__icontains=str)
            )
        else:
            # TODO: pagination
            return Diagnosis.objects.all()

    def resolve_medical_items_str(self, info, **kwargs):
        str = kwargs.get('str')
        if str is not None:
            return Item.objects.filter(
                Q(code__icontains=str) | Q(name__icontains=str)
            )
        else:
            # TODO: pagination
            return Item.objects.all()

    def resolve_medical_services_str(self, info, **kwargs):
        str = kwargs.get('str')
        if str is not None:
            return Service.objects.filter(
                Q(code__icontains=str) | Q(name__icontains=str)
            )
        else:
            # TODO: pagination
            return Service.objects.all()
