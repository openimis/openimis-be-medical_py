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
