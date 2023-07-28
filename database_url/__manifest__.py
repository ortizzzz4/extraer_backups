# -*- coding: utf-8 -*-
{
    'name': "database url",

    'summary': """
       """,

    'description': """
        Historial backups 
    """,

    'author': "",
    'website': "",

    
    'category': 'backups',

    'version': '16.01',
    'license': 'LGPL-3',

   
    'depends': ['base','mail'],

  
    'data': [
         'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
