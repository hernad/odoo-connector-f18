import binascii
import json
import logging
import urllib.parse
from contextlib import closing, contextmanager
from datetime import datetime
from os import urandom

import psycopg2
import pytz

import odoo
from odoo import _, api, exceptions, fields, models, tools

from odoo.addons.component.core import Component


_logger = logging.getLogger(__name__)


@contextmanager
def new_env(env):
    registry = odoo.registry(env.cr.dbname)
    with closing(registry.cursor()) as cr:
        new_env = api.Environment(cr, env.uid, env.context)
        try:
            yield new_env
        except Exception:
            cr.rollback()
            raise
        else:
            if not tools.config["test_enable"]:
                cr.commit()  # pylint: disable=invalid-commit


class F18Backend(models.Model):
    _name = "f18.backend"
    _description = "F18 Backend"
    _inherit = "connector.backend"

    name = fields.Char()
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    #worklog_fallback_project_id = fields.Many2one(
    #    comodel_name="project.project",
    #    string="Fallback for Worklogs",
    #    help="Worklogs which could not be linked to any project "
    #    "will be created in this project. Worklogs landing in "
    #    "the fallback project can be reassigned to the correct "
    #    "project by: 1. linking the expected project with the Jira one, "
    #    "2. using 'Refresh Worklogs from Jira' on the timesheet lines.",
    #)


    state = fields.Selection(
        selection=[
            ("config", "Configured"),
            ("ok", "OK"),
        ],
        default="config",
        required=True,
        readonly=True,
    )

    host_name = fields.Char(string="Host name", default="localhost")
    user_name = fields.Char(string="User name", default="hernad")
    password = fields.Char(string="password")
    database = fields.Char(string="database", default="bringout")
    port = fields.Integer(string="port number", default=5432)

    #verify_ssl = fields.Boolean(default=False, string="Verify SSL?")

    #odoo_webhook_base_url = fields.Char(
    #    string="Base Odoo URL for Webhooks",
    #    default=lambda self: self._default_odoo_webhook_base_url(),
    #)
    
  
    #@api.depends("database", "host_name")
    #def _set_name(self):
    #    for rec in self:
    #        rec.name = rec.host_name + "_" + rec.database

    #def _compute_last_import_date(self):
    #    for backend in self:
    #        self.env.cr.execute(
    #            """
    #            SELECT from_date_field, last_timestamp
    #            FROM f18_backend_timestamp
    #            WHERE backend_id = %s""",
    #            (backend.id,),
    #        )
    #        rows = self.env.cr.dictfetchall()
    #        for row in rows:
    #            field = row["from_date_field"]
    #            if field in self._fields:
    #                backend[field] = row["last_timestamp"]
    #        if not rows:
    #            backend.update(
    #                {
    #                    "import_project_task_from_date": False,
    #                    "import_analytic_line_from_date": False,
    #                    "delete_analytic_line_from_date": False,
    #                }
    #            )



    #def _run_background_from_date(
    #    self, model, from_date_field, component_usage, force=False
    #):
    #    """Import records from a date
    #
    #    Create jobs and update the sync timestamp in a savepoint; if a
    #    concurrency issue arises, it will be logged and rollbacked silently.
    #    """
    #    self.ensure_one()
    #    ts_model = self.env["f18.backend.timestamp"]
    #    timestamp = ts_model._timestamp_for_field(
    #        self,
    #        from_date_field,
    #        component_usage,
    #    )
    #    self.env[model].with_delay(priority=9).run_batch_timestamp(
    #        self, timestamp, force=force
    #    )



    @api.model
    def create(self, values):
        record = super().create(values)
        #record.create_rsa_key_vals()
        return record


    def button_setup(self):
        self.state_running()



    def state_ok(self):
        for backend in self:
            #if backend.state == "authenticate":
            backend.state = "ok"



    def check_connection(self):
        self.ensure_one()
        try:
            self.get_api_client().myself()
        except (ValueError, requests.exceptions.ConnectionError) as err:
            raise exceptions.UserError(_("Failed to connect (%s)") % (err,)) from err
        except JIRAError as err:
            raise exceptions.UserError(
                _("Failed to connect (%s)") % (err.text,)
            ) from err
        raise exceptions.UserError(_("Connection successful"))

    #def import_project_task(self):
    #    self._run_background_from_date(
    #        "jira.project.task",
    #        "import_project_task_from_date",
    #        "timestamp.batch.importer",
    #        force=self.import_project_task_force,
    #    )
    #    return True

    #def import_analytic_line(self):
    #    self._run_background_from_date(
    #        "jira.account.analytic.line",
    #        "import_analytic_line_from_date",
    #        "timestamp.batch.importer",
    #        force=self.import_analytic_line_force,
    #    )
    #    return True

    #def delete_analytic_line(self):
    #    self._run_background_from_date(
    #        "jira.account.analytic.line",
    #        "delete_analytic_line_from_date",
    #        "timestamp.batch.deleter",
    #    )
    #    return True

    #def import_res_users(self):
    #    self.report_user_sync = None
    #    result = self.env["res.users"].search([]).link_with_jira(backends=self)
    #    for __, bknd_result in result.items():
    #        if bknd_result.get("error"):
    #            self.report_user_sync = self.env.ref(
    #                "connector_jira.backend_report_user_sync"
    #            ).render({"backend": self, "result": bknd_result})
    #    return True

    #def get_user_resolution_order(self):
    #    """User resolution should happen by login first as it's unique, while
    #    resolving by email is likely to give false positives"""
    #    return ["login", "email"]

    def import_issue_type(self):
        self.env["f18.issue.type"].import_batch(self)
        return True

    #@api.model
    #def get_api_client(self):
    #    self.ensure_one()
    #    # tokens are only readable by connector managers
    #    backend = self.sudo()
    #    oauth = {
    #        "access_token": backend.access_token,
    #        "access_token_secret": backend.access_secret,
    #        "consumer_key": backend.consumer_key,
    #        "key_cert": backend.private_key,
    #    }
    #    options = {
    #        "server": backend.uri,
    #        "verify": backend.verify_ssl,
    #    }
    #    return JIRA(options=options, oauth=oauth, timeout=JIRA_TIMEOUT)



    #@api.model
    #def _scheduler_import_res_users(self):
    #    self.search([]).import_res_users()

 
