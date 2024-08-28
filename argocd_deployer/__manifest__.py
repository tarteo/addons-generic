{
    "name": "ArgoCD Deployer",
    "author": "Onestein",
    "website": "https://www.onestein.nl",
    "license": "AGPL-3",
    "category": "Tools",
    "version": "16.0.1.1.0",
    "data": [
        "data/ir_config_parameter_data.xml",
        "data/application_namespace_prefix.xml",
        "data/application_set_template.xml",
        "data/application_set.xml",
        "data/ir_cron_data.xml",
        "views/application_domain_view.xml",
        "views/application_template_view.xml",
        "views/application_set_template_view.xml",
        "views/application_tag_view.xml",
        "views/application_value_view.xml",
        "views/application_view.xml",
        "views/application_set_view.xml",
        "views/application_namespace_prefix_view.xml",
        "views/application_stat_type_view.xml",
        "views/application_stat_view.xml",
        "templates/application_description.xml",
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "menuitems.xml",
    ],
    "depends": ["queue_job", "mail"],
    "demo": [
        "demo/application_template_demo.xml",
        "demo/application_tag_demo.xml",
        "demo/application_stat_type_demo.xml",
    ],
    "external_dependencies": {"python": ["git"]},
}
