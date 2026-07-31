{
    'name': 'Position Sync Viewer',
    'version': '1.0',
    'summary': 'Read-only viewer and importer for external Course Project positions',
    'category': 'Services',
    'author': 'Bekzod',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/wizard_views.xml',
        'views/position_views.xml',
    ],
    'installable': True,
    'application': True,
}