# -*- coding: utf-8 -*-
{
    'name': "Memorandums",

    'summary': """
        Sistema emisión de Memorandums""",

    'description': """
        Modulo emisión y cotrol de Memorandums Universidad de Aysén
    """,

    'author': "Fernando Villaroel",
    'website': "http://uaysen.cl",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','purchase','hr','project','mail'],

    # always loaded
    'data': [
        'security/memorandum_security.xml',
        'security/ir.model.access.csv',
        'views/memos_view.xml',
        'views/items_memos_view.xml',
        'views/solicitudes_view.xml',
        'views/solicitud_items_view.xml',
        'views/certificados_view.xml',
        'views/items_certificados_view.xml',
        'views/memos_search_view.xml',
        'views/memos_report.xml',
        'views/certificados_report.xml',
        'views/purchase_view.xml',
        'views/imputaciones_view.xml',
        'views/anotaciones_view.xml',
    ],
    'application':True,

}
