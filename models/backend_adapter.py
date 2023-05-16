class BackendAdapter(Component):
    _name = "f18.backend.adapter"
    _inherit = "f18.database.adapter"
    _apply_on = ["f18.backend"]

    webhook_base_path = "{server}/rest/webhooks/1.0/{path}"

    def list_fields(self):
        return self.client._get_json("field")


