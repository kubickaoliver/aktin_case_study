"""Course model."""
from odoo.exceptions import UserError

from odoo import _, api, fields, models


class CourseCourse(models.Model):
    """Manage online courses, their participants, and pricing."""

    _name = 'online_course.course'
    _description = 'Online Course'

    name = fields.Char(
        string='Course Name',
        required=True,
        tracking=True,
    )
    description = fields.Text(
        required=True,
    )
    price = fields.Float(
        digits='Product Price',
        default=0.0,
        tracking=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id,
    )
    teacher_id = fields.Many2one(
        'res.users',
        string='Teacher',
        required=True,
        domain="[('is_teacher', '=', True)]",
        tracking=True,
    )
    enrollment_ids = fields.One2many(
        comodel_name="online_course.enrollment",
        inverse_name="course_id",
    )
    capacity = fields.Integer(
        string="Capacity",
        default=0,
        help="Maximum number of students for this course. 0 for unlimited.",
    )
    enrollments_count = fields.Integer(
        string="Enrolled Students",
        compute='_compute_enrollments_count',
        store=True,
    )
    is_current_user_enrolled = fields.Boolean(
        string="Is Current User Enrolled",
        compute='_compute_is_current_user_enrolled',
    )
    can_enroll = fields.Boolean(
        string="Can Enroll",
        compute='_compute_can_enroll',
        help="Check if the current user can enroll in this course."
    )
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('published', 'Published'),
            ('archived', 'Archived'),
        ],
        default='draft',
        required=True,
        tracking=True,
        copy=False,
    )
    is_paid = fields.Boolean(
        compute='_compute_is_paid',
        store=True,
    )

    # ----- Actions -----

    def action_publish(self):
        """
        Publish the course.

        A course must have a price greater than 0 to be published.
        """
        self.ensure_one()
        if self.is_paid and self.price <= 0:
            raise UserError(
                _("A paid course must have a price greater than 0 to be published.")
            )
        self.write({'state': 'published'})

    def action_archive(self):
        """Archive the course."""
        self.write({'state': 'archived'})

    def action_reset_to_draft(self):
        """Return the course to draft status."""
        self.write({'state': 'draft'})

    def action_enroll(self):
        """Enroll the current user to the course."""
        self.ensure_one()

        if self.teacher_id.id == self.env.user.id:
            raise UserError("You can't enroll in your own course")

        if self.state != "published":
            raise UserError("Online course must be published to be enrolled.")

        if 0 < self.capacity <= self.enrollments_count:
            raise UserError(_("Cannot enroll in '%s' as it is already full.", self.name))

        self.enrollment_ids.sudo().create(
            {
                'course_id': self.id,
                'student_id': self.env.user.id,
            }
        )

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Enrollment Successful",
                "message": _("You have been enrolled in '%s' course.", self.name),
                "type": "success",
                "next": {
                    "type": "ir.actions.client",
                    "tag": "soft_reload",
                },
            },
        }

    def action_unenroll(self):
        """Unenroll the current user from the course."""
        self.ensure_one()
        enrollment = self.env['online_course.enrollment'].search(
            [
                ('course_id', '=', self.id),
                ('student_id', '=', self.env.user.id),
            ], limit=1
        )
        if enrollment:
            enrollment.unlink()

        return {
            "type":   "ir.actions.client",
            "tag":    "display_notification",
            "params": {
                "title":   "Unenrollment Successful",
                "message": _("You have been unenrolled from '%s' course.", self.name),
                "type":    "warning",
                "next":    {
                    "type": "ir.actions.client",
                    "tag":  "soft_reload",
                },
            },
        }

    # ----- Private Methods -----

    @api.depends('price')
    def _compute_is_paid(self):
        """Calculate whether the course is paid based on price."""
        for course in self:
            course.is_paid = course.price > 0

    @api.depends('enrollment_ids')
    def _compute_enrollments_count(self):
        """Compute the number of enrolled students."""
        for course in self:
            course.enrollments_count = len(course.enrollment_ids)

    def _compute_is_current_user_enrolled(self):
        """Check if the current user is enrolled in the course."""
        if not self.ids:
            for course in self:
                course.is_current_user_enrolled = False
            return
        enrollments = self.env['online_course.enrollment'].search_read(
            [
                ('course_id', 'in', self.ids),
                ('student_id', '=', self.env.user.id)
            ],
            ['course_id']
        )
        enrolled_course_ids = {e['course_id'][0] for e in enrollments}
        for course in self:
            course.is_current_user_enrolled = course.id in enrolled_course_ids

    @api.depends('state', 'is_current_user_enrolled', 'capacity', 'enrollments_count')
    def _compute_can_enroll(self):
        """
        Compute if the current user can enroll.

        Conditions:
        - Course must be published.
        - User must not be already enrolled.
        - Course must not be full.
        """
        for course in self:
            is_full = 0 < course.capacity <= course.enrollments_count

            course.can_enroll = (
                course.state == 'published' and
                not course.is_current_user_enrolled and
                not is_full
            )
