{
    'name': 'Required PO in MO',
    'version': '16.0.1.1',
    'category': 'Manufacturing',
    'summary': 'Require Purchase Order for specific products in Manufacturing Orders',
    'description': """ This module introduces a number of features:
                    1. Required Purchase Order for specific products in MO
                    2. When a Customer/Farmer is selected and PO is required, only list the POs that belong to the customer and are not in any other MO.
                    3. Introduces Number Plate in PO
                    4. When a selected PO has a number plate in it, the number plate is imported into MO.
                    5. Farmer and Number Plate in list and form view """,
    'author': 'Jessy Ledama',
    'depends': ['mrp', 'purchase'],
    'data': [
        'views/mrp_settings_view.xml',
        'views/mrp_production_view.xml',
        'views/purchase_order.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
    'images': ['static/description/icon.png'],
}
