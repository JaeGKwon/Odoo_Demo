{
    'name': 'Oil Refining Company Demo Data',
    'version': '1.0',
    'category': 'Manufacturing',
    'summary': 'Comprehensive demo data for oil refining chemical company',
    'description': """
        This module provides comprehensive demo data for an oil refining chemical company.
        Includes:
        - Products (Crude Oil, Gasoline, Diesel, Heavy Oil, LPG, Naphtha, Asphalt, etc.)
        - Partners (Suppliers and Customers)
        - BOMs (Refining Processes)
        - Warehouses and Locations
        - Manufacturing, Sales, and Purchase Orders
        - Employees and Users
    """,
    'author': 'Demo Data Generator',
    'depends': [
        'base',
        'product',
        'stock',
        'mrp',
        'sale',
        'purchase',
        'account',
        'hr',
    ],
    'data': [
        'data/company_data.xml',
        'data/product_categories.xml',
        'data/products.xml',
        'data/partners.xml',
        'data/warehouses.xml',
        'data/boms.xml',
        'data/manufacturing_orders.xml',
        'data/employees.xml',
        # 주문 데이터는 Python 스크립트로 생성 (scripts/create_orders.py)
        # 'data/sale_orders.xml',
        # 'data/purchase_orders.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

