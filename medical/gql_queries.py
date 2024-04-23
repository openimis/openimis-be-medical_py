import graphene
from core import prefix_filterset, ExtendedConnection, filter_validity
from graphene.utils.deduplicator import deflate
from graphene_django import DjangoObjectType
from .models import Service, ServiceItem, ServiceService


class ServiceGQLType(DjangoObjectType):
    attachments_count = graphene.Int()
    client_mutation_id = graphene.String()

    class Meta:
        model = Service
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            'uuid': ['exact'],
            'code': ['exact', 'icontains', 'istartswith'],
            'name': ['exact', 'icontains', 'istartswith'],
            'type': ['exact'],
            'packagetype': ['exact', 'in'],
            'care_type': ['exact'],
            'category': ['exact'],
        }
        connection_class = ExtendedConnection

    # @classmethod
    # def get_queryset(cls, queryset, info):
    #     service_ids = Service.get_queryset(queryset, info).values('uuid').all()
    #     return Service.objects.filter(uuid__in=service_ids)


class ServiceItemGQLType(DjangoObjectType):
    class Meta:
        model = ServiceItem


class ServiceServiceGQLType(DjangoObjectType):
    class Meta:
        model = ServiceService
