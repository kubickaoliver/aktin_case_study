# Online Courses Management

![License: AGPL-3](https://img.shields.io/badge/License-AGPL--3-blue.svg)
![Odoo Version: 18.0](https://img.shields.io/badge/Odoo-18.0-714B67.svg)

This module provides a comprehensive platform for managing online courses within Odoo. It allows creating courses, assigning teachers, managing student enrollments, and handling different user roles with specific access rights.

## Key Features

-   **Course Creation & Management**: Easily create and manage courses with details like name, description, price, and student capacity.
-   **Teacher Management**: Link Odoo users to courses as teachers. A user profile includes a stat button showing the number of courses they teach.
-   **Student Enrollment System**: Students can browse published courses and enroll or unenroll with a single click from the Kanban view.
-   **Role-based Security**: Pre-configured security groups (Student, Teacher, Manager) ensure users only see and do what they are permitted to.
    -   **Student**: Can view all published courses and manage their own enrollments.
    -   **Teacher**: Can create, edit, and manage their own courses and view the enrollments for them.
    -   **Manager**: Has full access to all courses and settings.
-   **Course State Management**: Courses follow a simple workflow: Draft -> Published -> Archived.

## Installation

1.  Clone or download this repository.
2.  Copy the `online_course` folder into your Odoo `addons` directory.
3.  Restart your Odoo server.
4.  Navigate to the **Apps** menu in your Odoo instance.
5.  Click on **Update Apps List**.
6.  Search for "Online Courses Management" and click **Install**.

## Configuration

To use this module, you need to configure your users with the appropriate roles.

1.  Navigate to **Settings > Users & Companies > Users**.
2.  Select the user you want to assign a role to.
3.  Click **Edit**.
4.  To make a user a **Teacher**:
    -   Under the "Access Rights" tab, in the "Online Courses" section, select **Teacher**.
    -   To enable the "Courses taught" button on their profile, check the **Is a Teacher** boolean field on the user form.
5.  To make a user a **Student**, ensure they have the **Student** role (this is implied for all logged-in users).
6.  To make a user a **Manager**, assign them the **Manager** role, which grants full access.

## Usage / Workflow

### As a Teacher

1.  Navigate to the **Online Courses** menu.
2.  Click **Create** to set up a new course. Fill in the name, description, price, and capacity.
3.  When the course is ready, click the **Publish** button.
4.  You can view all students enrolled in your courses from the "Enrollments" tab on the course form.

### As a Student

1.  Navigate to the **Online Courses** menu.
2.  You will see a Kanban view of all published courses.
3.  To join a course, simply click the **Enroll** button on the course card.
4.  If you wish to leave a course, click the **Unenroll** button.

## Running Tests

This module comes with a suite of automated tests to ensure its functionality. To run them, execute the following command from your terminal, in the directory where your `odoo-bin` executable is located:

```bash
./odoo-bin -c your_config_file.conf -d your_test_database --test-enable -i online_course --stop-after-init