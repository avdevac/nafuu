# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name" : "MRP Subcintracting PO",
    "version" : "12.0.0.0",
    "category" : "",
    'summary': 'Brief description of the module',
    "description": """
    
   Description of the module. 
    
    """,
    "author": "BrowseInfo",
    "website" : "www.browseinfo.in",
    "price": 000,
    "currency": 'EUR',
    "depends" : ['base','sale_management','purchase','mrp' ,'mrp_workorder'],
    "data": [
       'security/ir.model.access.csv',
       'views/bom_inherited.xml',
       'views/mrp_production.xml',
       'views/product_product_inherited.xml',
       'views/purchase_inherited.xml',
       'views/po_by_email_report.xml',
    ],
    'qweb': [
    ],
    "auto_install": False,
    "installable": True,
    "live_test_url":'youtube link',
    "images":["static/description/Banner.png"],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
