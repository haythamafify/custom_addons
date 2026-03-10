# Todo Management

A comprehensive task management module for Odoo 18 that enables users to create, track, and manage daily tasks with workflow capabilities and collaborative features.

## Features

- **Task Creation & Management**: Create and organize tasks with detailed information
- **Task Assignment**: Assign tasks to team members for better task distribution
- **Workflow States**: Track tasks through multiple states:
  - New
  - In Progress
  - Completed
  - Cancelled
- **Priority Levels**: Set task priority (Low, Normal, High, Urgent)
- **Due Date Tracking**: Schedule tasks with due dates and automatic deadline status calculation
- **Progress Tracking**: Monitor task completion percentage
- **Deadline Status**: Automatic status indicators (On Time, Due Soon, Overdue)
- **Tags**: Organize and categorize tasks using tags
- **Chatter Integration**: Add comments and collaborate on tasks
- **Activity Mail**: Built-in notification system with mail integration
- **Rich Text Support**: Add detailed notes using HTML formatting

## Module Information

| Property        | Value                                      |
| --------------- | ------------------------------------------ |
| **Name**        | Todo Management                            |
| **Version**     | 18.0.1.0                                   |
| **Category**    | Productivity                               |
| **License**     | LGPL-3                                     |
| **Author**      | Haytham Gamal                              |
| **Website**     | https://github.com/haytham/todo-management |
| **Depends On**  | base, mail                                 |
| **Application** | Yes                                        |

## Installation

1. Place this module in your Odoo addons directory
2. Update the app list in Odoo
3. Install the "Todo Management" module from the Apps menu
4. Access the module from the main menu under **Todo Management**

## Technical Details

### Model Structure

#### Todo Task (`todo.task`)

- Inherits from `mail.thread` and `mail.activity.mixin` for chatter and activity support
- Fields:
  - **Task Title**: Required, main task identifier
  - **Assigned To**: User assignment (defaults to current user)
  - **Due Date**: Schedule deadline
  - **Status**: Current task state with workflow tracking
  - **Priority**: Urgency level
  - **Description**: Task overview
  - **Tags**: Categorization using many-to-many relation
  - **Progress**: Percentage completion
  - **Is Overdue**: Computed boolean field
  - **Deadline Status**: Automatic status based on due date
  - **Completed Date**: Auto-recorded completion timestamp
  - **Additional Notes**: Rich text field for detailed information

### Security

Access control is defined in `security/ir.model.access.csv` with role-based permissions.

### Views

- **Todo Task Views** (`views/todo_task_view.xml`):
  - List view for browsing all tasks
  - Form view for creating/editing tasks
  - Search and filter capabilities

- **Menu** (`views/base_menu_view.xml`):
  - Main menu entry under "Todo Management"
  - Quick access to tasks

## Usage

### Creating a Task

1. Navigate to **Todo Management** > **Tasks**
2. Click **Create**
3. Fill in the task details:
   - Task Title (required)
   - Assigned To
   - Due Date
   - Priority Level
   - Description
   - Tags
   - Progress percentage
4. Save the task

### Managing Tasks

- Change task status using the **Status** dropdown
- Adjust priority on-the-fly
- Update progress percentage
- Add notes and collaborate using the chatter
- Track task history through activity timeline

### Task Ordering

Tasks are displayed ordered by:

1. Priority (highest first)
2. Due Date (earliest first)
3. ID (newest first)

## Database Tables

- `todo_task`: Main tasks table
- `todo_task_tag`: Tags for task categorization (if applicable)
- Related mail tables for chatter and activity tracking

## Notes

- All task changes are automatically tracked with field history
- The module integrates with Odoo's built-in email and activity systems
- Date fields use Odoo's date picker for easy selection

## License

This module is licensed under LGPL-3. See the LICENSE file for more information.

## Support

For issues, feature requests, or contributions, visit the project repository.
