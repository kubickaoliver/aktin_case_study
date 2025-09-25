"""Course Enrollment model."""
from odoo import fields, models


class CourseEnrollment(models.Model):
    """
    This model represents the enrollment of a student in a course.

    It acts as a relational model between 'res.users' (students) and 'online_course.course',
    allowing to store additional information about the enrollment, such as the date
    and status.
    """

    _name = 'online_course.enrollment'
    _description = 'Course Enrollment'
    _rec_name = 'course_id'

    course_id = fields.Many2one(
        'online_course.course',
        string='Course',
        required=True,
        ondelete='cascade'
    )
    student_id = fields.Many2one(
        'res.users',
        string='Student',
        required=True,
        ondelete='cascade'
    )
    enrollment_date = fields.Date(
        string='Enrollment Date',
        default=fields.Date.today,
        readonly=True
    )
    state = fields.Selection(
        [
            ('enrolled', 'Enrolled'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled')
        ],
        string='Status',
        default='enrolled',
        required=True,
        tracking=True,
    )

    _sql_constraints = [
        ('student_course_unique', 'unique(student_id, course_id)',
         'A student can only be enrolled in a course once.')
    ]
