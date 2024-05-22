import logging
from medical.models import ServiceItem, ServiceService, Item, Service
logger = logging.getLogger(__name__)
def process_child_relation(user, data_children, service_id, children, create_hook):
    claimed = 0
    if isinstance(data_children, list):
        for data_elt in data_children:
            elt_id = data_elt.pop('id') if 'id' in data_elt else None
            if elt_id:
                if create_hook == item_create_hook:
                    elt = ServiceItem.objects.get(id=elt_id)
                else:
                    elt = ServiceService.objects.get(id=elt_id)
                [setattr(elt, k, v) for k, v in data_elt.items()]
                elt.save()
            else:
                logger.debug("Create Item or Service")
                data_elt['audit_user_id'] = user.id_for_audit
                create_hook(children, data_elt)
    return claimed


def item_create_hook(service, item):
    item_def = Item.objects.get(id=item['item_id'])
    ServiceItem.objects.create(
        parent=service,
        item=item_def,
        price_asked=item['price_asked'],
        qty_provided=item['qty_provided'])


def service_create_hook(service_id, service):
    service_def = Service.objects.get(id=service['service_id'])
    ServiceService.objects.create(
        parent=service_id,
        service=service_def,
        price_asked=service['price_asked'],
        qty_provided=service['qty_provided']
    )


def process_items_relations(user, Service, items):
    return process_child_relation(user, items, Service.id, Service, item_create_hook)


def process_services_relations(user, Service, services):
    return process_child_relation(user, services, Service.id, Service, service_create_hook)