"""Res Users model."""
from odoo import api, models, fields, _


class ResUsers(models.Model):
    """Extend the res.users to add teacher-specific fields and course information."""

    _inherit = 'res.users'

    is_teacher = fields.Boolean(
        default=False,
        string="Is a Teacher",
    )
    course_ids = fields.One2many(
        'online_course.course',
        'teacher_id',
        string='Courses',
    )
    taught_course_count = fields.Integer(
        compute='_compute_taught_course_count',
    )

    # ----- Actions -----

    def action_open_courses(self):
        """Open a list of courses taught by this user."""
        self.ensure_one()
        return {
            'name': _('Courses'),
            'type': 'ir.actions.act_window',
            'res_model': 'online_course.course',
            'view_mode': 'kanban,tree,form',
            'domain': [('teacher_id', '=', self.id)],
            'context': {'default_teacher_id': self.id},
        }

    # ----- Private Methods -----

    @api.depends('course_ids')
    def _compute_taught_course_count(self):
        """Calculate the number of courses the user teaches."""
        for user in self:
            user.taught_course_count = len(user.course_ids)
