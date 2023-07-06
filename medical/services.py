from gettext import gettext as _

def set_item_or_service_deleted(item_service, item_or_service_element):
    """
    Marks an Item or Service as deleted, cascading onto the pricelists
    :param item_service: the object to mark as deleted
    :param item_or_service_element: either "item" or "service", used for translation keys
    :return: an empty array is everything goes well, an array with errors if any
    """
    try:
        item_service.delete_history()
        [pld.delete_history() for pld in item_service.pricelist_details.filter(validity_to__isnull=True)]
        return []
    except Exception as exc:
        return {
            'title': item_service.uuid,
            'list': [{
                'message': _(f"medical.mutation.failed_to_delete_{item_or_service_element}")
                           % {'uuid': item_service.uuid},
                'detail': item_service.uuid}]
        }


def clear_item_dict(item):
    new_dict = {
        "code": item.code,
        "name": item.name,
        "type": item.type,
        "price": item.price,
        "care_type": item.care_type,
        "patient_category": item.patient_category,
        "package": item.package,
        "quantity": item.quantity,
        "frequency": item.frequency,
    }
    return new_dict


def check_unique_code_service(code):
    from .models import Service
    if Service.objects.filter(code=code, validity_to__isnull=True).exists():
        return [{"message": "Services code %s already exists" % code}]
    return []


def check_unique_code_item(code):
    from .models import Item
    if Item.objects.filter(code=code, validity_to__isnull=True).exists():
        return [{"message": "Items code %s already exists" % code}]
    return []
