{
    'name': "Online Courses",
    'version': '18.0.1.0.0',
    'summary': """
        Manage online courses, teachers, and students.
    """,
    'description': """
        This module provides a simple system to manage online courses.
        It includes models for courses, enrollments, and extends user profiles.
    """,
    'author': "Oliver Kubicka",
    'website': "https://www.aktin.com",
    'category': 'Education',
    'license': 'AGPL-3',
    'depends': [
        # Core Modules
        'base',
    ],
    'data': [
        # Security
        'security/online_course_security.xml',
        'security/ir.model.access.csv',
        # Data
        # Assets
        # Wizard Actions
        # Views
        'views/course_views.xml',
        'views/res_users_views.xml',
        # Wizards
        # Actions
        'views/actions.xml',
        # Reports
        # Menu Items
        'views/menu_items.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'online_course/static/src/css/style.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'demo': [],
    'qweb': [],
}
