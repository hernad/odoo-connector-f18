from odoo.addons.component.core import Component

class F18Binder(Component):
    """Binder for Odoo models
    """

    _name = "f18.binder"
    _inherit = ["base.binder", "f18.base"]



class F18ModelBinder(Component):
    """Binder for standalone models

    When we synchronize a model that has no equivalent
    in Odoo, we create a model that hold the Jira records
    without `_inherits`.

    """

    _name = "f18.model.binder"
    _inherit = ["base.binder", "f18.base"]

    _apply_on = [
        "f18.issue.type",
    ]

    _odoo_field = "id"

    def to_internal(self, external_id, unwrap=False):
        if unwrap:
            _logger.warning(
                "unwrap has no effect when the "
                "binding is not an inherits "
                "(model %s)",
                self.model._name,
            )
        return super().to_internal(external_id, unwrap=False)

    def unwrap_binding(self, binding):
        if isinstance(binding, models.BaseModel):
            binding.ensure_one()
        else:
            binding = self.model.browse(binding)
        return binding

    def unwrap_model(self):
        return self.model
