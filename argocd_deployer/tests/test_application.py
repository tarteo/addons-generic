from unittest import skip
from unittest.mock import MagicMock, patch

from odoo import Command
from odoo.tests.common import TransactionCase


class TestApplication(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.app = cls.env["argocd.application"].create(
            {
                "name": "myapp",
                "template_id": cls.env.ref(
                    "argocd_deployer.demo_curq_basis_application_template"
                ).id,
                "tag_ids": [
                    cls.env.ref(
                        "argocd_deployer.demo_matomo_server_application_tag"
                    ).id,
                ],
            }
        )

    # FIXME: Re-enable when the domain functionality works.
    @skip("Domains are disabled.")
    def test_get_urls(self):
        self.app.render_config()
        urls = {url for url in self.app.get_urls()}
        expected_urls = {
            ("https://myapp.curq.k8s.onestein.eu", "Odoo"),
            ("https://matomo.myapp.curq.k8s.onestein.eu", "Matomo Server"),
        }
        self.assertEqual(expected_urls, urls)

        self.app.tag_ids = [Command.clear()]
        self.app.render_config()
        urls = self.app.get_urls()
        expected_urls = [("https://myapp.curq.k8s.onestein.eu", "Odoo")]
        self.assertEqual(urls, expected_urls)

    def _disable_simulation(self):
        simulation_mode = (
            self.env["ir.config_parameter"]
            .get_param("argocd.git_simulation_mode", "none")
            .lower()
        )
        if simulation_mode != "none":
            self.env["ir.config_parameter"].set_param(
                "argocd.git_simulation_mode", "none"
            )

    def test_immediate_deploy(self):
        mock_repository = MagicMock()
        mock_remote = MagicMock()
        mock_repository.remotes.origin = mock_remote
        mock_repository.working_dir = "/home/test"
        mock_get_repository = MagicMock(return_value=mock_repository)
        mock_deploy_files = MagicMock(
            return_value=({"add": "test.yaml"}, "Added `%s`.)")
        )
        self._disable_simulation()  # We're doing patching instead

        with patch.multiple(
            "odoo.addons.argocd_deployer.models.application.Application",
            _get_deploy_content=mock_deploy_files,
            _get_repository=mock_get_repository,
        ):
            self.app.immediate_deploy()
            mock_get_repository.assert_called_once()
            mock_remote.pull.assert_called_once()
            mock_deploy_files.assert_called_once()
            mock_repository.commit.called_once_with(
                mock_repository, "Added `test-set`", ["application_set.yaml"]
            )
            mock_remote.push.assert_called_once()

    def test_immediate_destroy(self):
        mock_repository = MagicMock()
        mock_remote = MagicMock()
        mock_repository.remotes.origin = mock_remote
        mock_repository.working_dir = "/home/test"
        mock_get_repository = MagicMock(return_value=mock_repository)
        mock_destroy_files = MagicMock(
            return_value=({"remove": "test.yaml"}, "Removed `%s`.)")
        )
        self._disable_simulation()  # We're doing patching instead

        with patch.multiple(
            "odoo.addons.argocd_deployer.models.application.Application",
            _get_destroy_content=mock_destroy_files,
            _get_repository=mock_get_repository,
        ):
            self.app.immediate_destroy()
            mock_get_repository.assert_called_once()
            mock_remote.pull.assert_called_once()
            mock_destroy_files.assert_called_once()
            mock_repository.commit.called_once_with(
                mock_repository, "Removed `test-set`", ["application_set.yaml"]
            )
            mock_remote.push.assert_called_once()

    def test_search_is_deployed(self):
        app2 = self.env["argocd.application"].create(
            {
                "name": "myapp2",
                "template_id": self.env.ref(
                    "argocd_deployer.demo_curq_basis_application_template"
                ).id,
                "tag_ids": [
                    self.env.ref(
                        "argocd_deployer.demo_matomo_server_application_tag"
                    ).id,
                ],
            }
        )
        result = self.env["argocd.application"].search([("is_deployed", "=", False)])
        self.assertEqual(self.app | app2, result)
        result = self.env["argocd.application"].search([("is_deployed", "!=", True)])
        self.assertEqual(self.app | app2, result)

        with patch(
            "odoo.addons.argocd_deployer.models.application.Application.is_deployed",
            return_value=True,
        ):
            result = self.env["argocd.application"].search([("is_deployed", "=", True)])
            self.assertEqual(self.app | app2, result)
            result = self.env["argocd.application"].search(
                [("is_deployed", "!=", False)]
            )
            self.assertEqual(self.app | app2, result)

        with self.assertRaisesRegex(NotImplementedError, "Operator not supported."):
            self.env["argocd.application"].search([("is_deployed", "in", [True])])
