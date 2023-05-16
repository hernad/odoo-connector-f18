from odoo.addons.component.core import component


class F18Adapter(Component):
    _name = "f18.database.adapter"
    _inherit = ["base.backend.adapter.crud"]


    def __init__(self, work_context):
        super().__init__(work_context)

    def _get_response(self, data=None):
        return {}