from odoo.addons.component.core import AbstractComponent

class F18BaseImportMapper(AbstractComponent):
    """Base Import Mapper for F18"""

    _name = "f18.import.mapper"
    _inherit = ["base.import.mapper", "f18.base"]

    @mapping
    def f18_updated_at(self, record):
        if self.options.external_updated_at:
            return {"f18_updated_at": self.options.external_updated_at}
