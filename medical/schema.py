import graphene
from core import ExtendedConnection
from core import filter_validity
from core.schema import OrderedDjangoFilterConnectionField
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.utils.translation import gettext as _
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from medical.gql_mutations import CreateServiceMutation, UpdateServiceMutation, DeleteServiceMutation, \
    CreateItemMutation, UpdateItemMutation, DeleteItemMutation

from .apps import MedicalConfig
from .models import Diagnosis, Item, Service
import graphene_django_optimizer as gql_optimizer


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
            'package': ['exact', 'icontains', 'istartswith'],
            'type': ['exact'],
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
            'type': ['exact'],
            'care_type': ['exact'],
            'category': ['exact'],
        }
        connection_class = ExtendedConnection


class Query(graphene.ObjectType):
    diagnoses = DjangoFilterConnectionField(DiagnosisGQLType)
    diagnoses_str = DjangoFilterConnectionField(
        DiagnosisGQLType,
        str=graphene.String()
    )
    medical_items = OrderedDjangoFilterConnectionField(
        ItemGQLType,
        client_mutation_id=graphene.String(),
        show_history=graphene.Boolean(),
        orderBy=graphene.List(of_type=graphene.String))
    medical_items_str = OrderedDjangoFilterConnectionField(
        ItemGQLType,
        str=graphene.String(),
        date=graphene.Date(),
        orderBy=graphene.List(of_type=graphene.String)
    )

    medical_services = OrderedDjangoFilterConnectionField(
        ServiceGQLType,
        client_mutation_id=graphene.String(),
        show_history=graphene.Boolean(),
        orderBy=graphene.List(of_type=graphene.String))
    medical_services_str = OrderedDjangoFilterConnectionField(
        ServiceGQLType,
        str=graphene.String(),
        date=graphene.Date(),
        orderBy=graphene.List(of_type=graphene.String)
    )

    def resolve_diagnoses_str(self, info, **kwargs):
        if not info.context.user.has_perms(MedicalConfig.gql_query_diagnosis_perms):
            raise PermissionDenied(_("unauthorized"))
        search_str = kwargs.get('str')
        if search_str is not None:
            return Diagnosis.objects \
                .filter(*filter_validity()) \
                .filter(Q(code__icontains=search_str) | Q(name__icontains=search_str))
        else:
            return Diagnosis.objects.filter(*filter_validity())

    def resolve_medical_items_str(self, info, **kwargs):
        if not info.context.user.has_perms(MedicalConfig.gql_query_medical_items_perms):
            raise PermissionDenied(_("unauthorized"))
        search_str = kwargs.get('str')
        date = kwargs.get('date')
        if search_str is not None:
            return Item.objects \
                .filter(*filter_validity(date)) \
                .filter(Q(code__icontains=search_str) | Q(name__icontains=search_str))
        else:
            return Item.objects.filter(*filter_validity(date))

    def resolve_medical_items(self, info, show_history=False, client_mutation_id=None,
                                 **kwargs):
        if not info.context.user.has_perms(MedicalConfig.gql_query_medical_items_perms):
            raise PermissionDenied(_("unauthorized"))
        queryset = Item.get_queryset(None, user=info.context.user)
        if client_mutation_id:
            queryset = queryset.filter(mutations__mutation__client_mutation_id=client_mutation_id)
        if not show_history:
            queryset = queryset.filter(*filter_validity(**kwargs))
        return gql_optimizer.query(queryset, info)

    def resolve_medical_services_str(self, info, **kwargs):
        if not info.context.user.has_perms(MedicalConfig.gql_query_medical_services_perms):
            raise PermissionDenied(_("unauthorized"))
        search_str = kwargs.get('str')
        date = kwargs.get('date')
        if search_str is not None:
            return Service.objects \
                .filter(*filter_validity(date)) \
                .filter(Q(code__icontains=search_str) | Q(name__icontains=search_str))
        else:
            return Service.objects.filter(*filter_validity(date))

    def resolve_medical_services(self, info, show_history=False, client_mutation_id=None,
                                 **kwargs):
        if not info.context.user.has_perms(MedicalConfig.gql_query_medical_services_perms):
            raise PermissionDenied(_("unauthorized"))
        queryset = Service.get_queryset(None, user=info.context.user)
        if client_mutation_id:
            queryset = queryset.filter(mutations__mutation__client_mutation_id=client_mutation_id)
        if not show_history:
            queryset = queryset.filter(*filter_validity(**kwargs))
        return gql_optimizer.query(queryset, info)


class Mutation(graphene.ObjectType):
    create_service = CreateServiceMutation.Field()
    update_service = UpdateServiceMutation.Field()
    delete_service = DeleteServiceMutation.Field()
    create_item = CreateItemMutation.Field()
    update_item = UpdateItemMutation.Field()
    delete_item = DeleteItemMutation.Field()
