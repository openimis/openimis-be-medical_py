import re

from core import ExtendedConnection
from django.db.models import Q
from django.core.exceptions import PermissionDenied
import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from .models import Diagnosis, Item, Service
from .apps import MedicalConfig
from django.utils.translation import gettext as _


class DiagnosisGQLType(DjangoObjectType):
    class Meta:
        model = Diagnosis
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            'id': ['exact'],
            'code': ['exact', 'icontains', 'istartswith'],
            'name': ['exact', 'icontains', 'istartswith'],
        }
        connection_class = ExtendedConnection


class ItemGQLType(DjangoObjectType):
    class Meta:
        model = Item
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            'uuid': ['exact'],
            'code': ['exact', 'icontains', 'istartswith'],
            'name': ['exact', 'icontains', 'istartswith'],
        }
        connection_class = ExtendedConnection


class ServiceGQLType(DjangoObjectType):
    class Meta:
        model = Service
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            'uuid': ['exact'],
            'code': ['exact', 'icontains', 'istartswith'],
            'name': ['exact', 'icontains', 'istartswith'],
        }
        connection_class = ExtendedConnection


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
        if not info.context.user.has_perms(MedicalConfig.gql_query_diagnosis_perms):
            raise PermissionDenied(_("unauthorized"))
        str = kwargs.get('str')
        if str is not None:
            return Diagnosis.objects.filter(
                Q(code__icontains=str) | Q(name__icontains=str)
            )
        else:
            return Diagnosis.objects.all()

    def resolve_medical_items_str(self, info, **kwargs):
        if not info.context.user.has_perms(MedicalConfig.gql_query_medical_items_perms):
            raise PermissionDenied(_("unauthorized"))
        str = kwargs.get('str')
        if str is not None:
            return Item.objects.filter(
                Q(code__icontains=str) | Q(name__icontains=str)
            )
        else:
            return Item.objects.all()

    def resolve_medical_services_str(self, info, **kwargs):
        if not info.context.user.has_perms(MedicalConfig.gql_query_medical_services_perms):
            raise PermissionDenied(_("unauthorized"))
        qry = kwargs.get('str')
        if qry is not None:
            return Service.objects.filter(
                Q(code__icontains=qry) | Q(name__icontains=qry)
            )
        else:
            return Service.objects.all()
