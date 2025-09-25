"""Course Tests."""
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError, ValidationError


class TestCourseLogic(TransactionCase):
    """
    Test the business logic of the 'online_course.course' and related models.

    It covers state transitions, constraints, enrollment, and user interactions.
    """

    @classmethod
    def setUpClass(cls):
        """Set course logic and models before tests."""
        super().setUpClass()
        # Create references to the models for easier use
        cls.User = cls.env['res.users']
        cls.Course = cls.env['online_course.course']
        cls.Enrollment = cls.env['online_course.enrollment']

        # Get references to the security groups
        group_student = cls.env.ref('online_course.group_online_course_student')
        group_teacher = cls.env.ref('online_course.group_online_course_teacher')

        # Create test users and assign them to groups
        cls.teacher_user = cls.User.create({
            'name': 'Test Teacher',
            'login': 'teacher@test.com',
            'is_teacher': True,
            'groups_id': [(6, 0, [group_teacher.id])],
        })
        cls.student_user = cls.User.create({
            'name': 'Test Student 1',
            'login': 'student1@test.com',
            'groups_id': [(6, 0, [group_student.id])],
        })
        cls.student_user_2 = cls.User.create({
            'name': 'Test Student 2',
            'login': 'student2@test.com',
            'groups_id': [(6, 0, [group_student.id])],
        })

        # Create a base course for the tests
        cls.course = cls.Course.create({
            'name': 'Test Course for Enrollment',
            'description': 'A course to test various scenarios.',
            'teacher_id': cls.teacher_user.id,
            'price': 99.99,
            'capacity': 2, # Set a capacity for testing purposes
        })

    def test_010_publish_course_successfully(self):
        """Test that publishing a course with a valid price is successful."""
        # Create a course in the 'draft' state
        draft_course = self.Course.create({
            'name': 'Successful Course',
            'description': 'Description',
            'teacher_id': self.teacher_user.id,
            'price': 99.99,
        })
        self.assertEqual(draft_course.state, 'draft', "Course should start in 'draft' state.")

        # Run the action as the course's teacher
        draft_course.with_user(self.teacher_user).action_publish()
        self.assertEqual(
            draft_course.state,
            'published',
            "Course with a valid price should be published."
        )
        self.assertTrue(draft_course.is_paid, "Course with price > 0 should be marked as paid.")

    def test_011_publish_course_with_zero_price_fails(self):
        """Test that publishing a course with a price of 0 raises a UserError."""
        free_course = self.Course.create({
            'name': 'Free Course Fail',
            'description': 'Description',
            'teacher_id': self.teacher_user.id,
            'price': 0.0,
        })
        # Expect a UserError because the price is 0
        with self.assertRaises(
            UserError,
            msg="Publishing a course with price 0 should be forbidden."
        ):
            free_course.action_publish()
        self.assertEqual(
            free_course.state,
            'draft',
            "Course state should remain 'draft' after a failed publish."
        )

    def test_020_student_enroll_successfully(self):
        """Test that a student can successfully enroll in a published course."""
        # First, we publish the course
        self.course.action_publish()
        self.assertEqual(self.course.state, 'published')

        # Verify the initial state
        self.assertEqual(self.course.enrollments_count, 0)

        # Enroll the student - we run the action as that specific student
        self.course.with_user(self.student_user).action_enroll()

        # Verify that the state has changed as expected
        self.assertEqual(self.course.enrollments_count, 1, "Enrollment count should be 1.")
        self.assertTrue(
            self.course.with_user(self.student_user).is_current_user_enrolled,
            "Student should be marked as enrolled."
        )
        # Verify that the enrollment record actually exists in the database
        enrollment_exists = self.Enrollment.search_count([
            ('course_id', '=', self.course.id),
            ('student_id', '=', self.student_user.id),
        ])
        self.assertEqual(enrollment_exists, 1, "An enrollment record should have been created.")

    def test_021_enroll_fails_if_course_is_full(self):
        """Test that enrollment fails when the course capacity is reached."""
        self.course.action_publish()

        # Enroll the first student (capacity is 2)
        self.course.with_user(self.student_user).action_enroll()
        # Enroll the second student
        self.course.with_user(self.student_user_2).action_enroll()

        self.assertEqual(self.course.enrollments_count, 2, "Course should be full.")

        # Create a third student who will try to enroll
        student_3 = self.User.create({'name': 'Late Student', 'login': 'student3@test.com'})

        # Expect an error because the course is full
        with self.assertRaises(
            ValidationError,
            msg="Should not be able to enroll in a full course."
        ):
            self.course.with_user(student_3).action_enroll()

        self.assertEqual(self.course.enrollments_count, 2, "Enrollment count should remain 2.")

    def test_022_enroll_fails_if_course_not_published(self):
        """Test that a student cannot enroll in a course that is not published."""
        # The course is in 'draft' state, we don't call action_publish()
        self.assertEqual(self.course.state, 'draft')

        with self.assertRaises(
            ValidationError,
            msg="Should not be able to enroll in a draft course."
        ):
            self.course.with_user(self.student_user).action_enroll()

    def test_030_unenroll_successfully(self):
        """Test that a student can successfully unenroll from a course."""
        self.course.action_publish()

        # First, we enroll the student
        self.course.with_user(self.student_user).action_enroll()
        self.assertEqual(self.course.enrollments_count, 1)

        # Then, we unenroll them
        self.course.with_user(self.student_user).action_unenroll()

        # Verify that the enrollment count decreased and the record was deleted
        self.assertEqual(
            self.course.enrollments_count,
            0,
            "Enrollment count should be 0 after unenrolling."
        )
        enrollment_exists = self.Enrollment.search_count([
            ('course_id', '=', self.course.id),
            ('student_id', '=', self.student_user.id),
        ])
        self.assertEqual(enrollment_exists, 0, "Enrollment record should have been deleted.")

    def test_031_teacher_cannot_enroll_in_own_course(self):
        """(FIXED TEST) Test that a teacher cannot enroll in their own course."""
        self.course.action_publish()

        # We try to enroll in the course as its own teacher
        with self.assertRaises(
            UserError,
            msg="A teacher should not be able to enroll in their own course."
        ):
            self.course.with_user(self.teacher_user).action_enroll()

    def test_040_compute_fields_work_correctly(self):
        """Test the logic of computed fields like 'can_enroll'."""
        # As a student, the course is in draft -> cannot enroll
        self.assertFalse(self.course.with_user(self.student_user).can_enroll)

        self.course.action_publish()

        # As a student, the course is published -> can enroll
        self.assertTrue(self.course.with_user(self.student_user).can_enroll)

        # The student enrolls
        self.course.with_user(self.student_user).action_enroll()

        # The student is already enrolled -> cannot enroll again
        self.assertFalse(self.course.with_user(self.student_user).can_enroll)

        # The course teacher -> cannot enroll
        self.assertFalse(self.course.with_user(self.teacher_user).can_enroll)
