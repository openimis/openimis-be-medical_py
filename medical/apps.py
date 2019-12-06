from django.apps import AppConfig

MODULE_NAME = "medical"

DEFAULT_CFG = {
    "gql_query_diagnosis_perms": [],
    "gql_query_medical_items_perms": [],
    "gql_query_medical_services_perms": []
}


class MedicalConfig(AppConfig):
    name = MODULE_NAME

    gql_query_insurees_perms = []
    gql_query_medical_items_perms = []
    gql_query_medical_services_perms = []

    def _configure_permissions(self, cfg):
        MedicalConfig.gql_query_diagnosis_perms = cfg[
            "gql_query_diagnosis_perms"]
        MedicalConfig.gql_query_medical_items_perms = cfg[
            "gql_query_medical_items_perms"]
        MedicalConfig.gql_query_medical_services_perms = cfg[
            "gql_query_medical_services_perms"]

    def ready(self):
        from core.models import ModuleConfiguration
        cfg = ModuleConfiguration.get_or_default(MODULE_NAME, DEFAULT_CFG)
        self._configure_permissions(cfg)
