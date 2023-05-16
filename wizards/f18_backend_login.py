#import logging

from odoo import _, api, exceptions, fields, models

#_logger = logging.getLogger(__name__)


#try:
#    from requests_oauthlib import OAuth1
#except ImportError as err:
#    _logger.debug(err)


class F18BackendLogin(models.TransientModel):
    _name = "f18.backend.login"
    _description = "F18 Backend Login"

    @api.model
    def default_get(self, fields):
        values = super().default_get(fields)
        context = self.env.context
        if context.get("active_model") == "f18.backend" and context.get("active_id"):
            backend = self.env["f18.backend"].browse(context["active_id"])
            values.update(
                {
                    "backend_id": backend.id,
                    "host_name": backend.host_name,
                    "user_name": backend.user_name,
                    "password": backend.password,
                    "port": backend.port,
                    "database": backend.database,
                    "state": "config"
                }
            )
        return values

    backend_id = fields.Many2one("f18.backend")
    state = fields.Selection(
        [
            ("config", "Config"),
            ("ok", "OK"),
        ],
        default="config",
    )

    host_name = fields.Char()
    user_name = fields.Char()
    password = fields.Char()
    database = fields.Char()
    port = fields.Integer()

    def do_login_test(self):
        
        self.backend_id.write({
            "host_name": self.host_name, 
            "user_name": self.user_name, 
            "password": self.password,
            "database": self.database,
            "port": self.port,
            "name": self.host_name + "_" + self.database
        })
        self.state = "ok"
        self.backend_id.state_ok()
        return
