
from medical.models import ServiceItem, ServiceService, Item

def process_child_relation(user, data_children, service_id, children, create_hook):
    claimed = 0
    from core.utils import TimeUtils
    for data_elt in data_children:
        elt_id = data_elt.pop('id') if 'id' in data_elt else None

        if elt_id:
            elt = children.get(id=elt_id)
            [setattr(elt, k, v) for k, v in data_elt.items()]
            elt.audit_user_id = user.id_for_audit
            elt.service_id = service_id
            elt.validity_to = None
            elt.save()
        else:
            data_elt['audit_user_id'] = user.id_for_audit
            #data_elt.pop('service_id', None)
            create_hook(children, data_elt)
    return claimed

def item_create_hook(service_id, item):
    item.item_id = Item.objects.get(id=item.item_id)
    ServiceItem.objects.create(
        servicelinkedItem=service_id,
        item_id = item.item_id,
        price_asked = item.price_asked,
        qty_provided = item.qty_provided)


def service_create_hook(service_id, service):
    service.service = Item.objects.get(id=service.service_id)
    ServiceService.objects.create(
        servicelinkedService=service_id,
        service_id = service.service_id,
        price_asked = service.price_asked,
        qty_provided = service.qty_provided
    )

def process_items_relations(user, Service, items):
    return process_child_relation(user, items, Service.id, Service, item_create_hook)


def process_services_relations(user, Service, services):
    return process_child_relation(user, services, Service.id, Service, service_create_hook)