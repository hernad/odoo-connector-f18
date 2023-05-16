from odoo.addons.component.core import AbstractComponent


class BaseF18ConnectorComponent(AbstractComponent):
    """Base F18 Connector Component

    All components of this connector should inherit from it.
    """

    _name = "f18.base"
    _inherit = "base.connector"
    _collection = "f18.backend"