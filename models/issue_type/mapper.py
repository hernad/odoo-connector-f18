
from odoo.addons.component.core import Component
#from odoo.addons.connector.components.mapper import mapping


class F18TypeMapper(Component):
    _name = "f18.issue.type.mapper"
    _inherit = ["f18.import.mapper"]
    _apply_on = "f18.issue.type"

    direct = [
        ("name", "name"),
        ("description", "description"),
    ]

    @mapping
    def backend_id(self, record):
        return {"backend_id": self.backend_record.id}

