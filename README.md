# Smart Schedule Automator 🎓

A Python-based study task manager and intelligent scheduler that helps students organize their academic workload and generate optimal study schedules using AI-like algorithms.

![Main Menu](project_images/Screenshot%202025-07-15%20002230.png)

## Features ✨

- **📝 Task Management**: Add, edit, delete, and track progress on study tasks
- **🤖 AI-Powered Scheduling**: Intelligent algorithm that considers priority, deadlines, difficulty, and available time
- **📊 Progress Tracking**: Monitor completion status and task statistics
- **📅 Weekly Schedule**: Generate and view optimized study schedules
- **🎯 Priority System**: 5-level priority system with visual indicators
- **⏰ Time Management**: Set available study hours for each day of the week
- **💾 Data Persistence**: Tasks are automatically saved to JSON file
- **📱 Basic Web Interface**: Simple HTML template for future web development

## Quick Start 🚀

### Option 1: One-Click Start (Recommended)
```bash
python run.py
```

### Option 2: Manual Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python simple_main.py
   ```

3. Follow the interactive menu to manage your tasks and generate schedules

![Task Management](project_images/Screenshot%202025-07-15%20002633.png)

## How It Works 🔧

### Backend (Python)
- **Task Management**: Handles CRUD operations for study tasks via command-line interface
- **AI Scheduler**: Uses heuristics to optimize study schedules based on:
  - Task priority and urgency
  - Available time slots
  - Task difficulty and type
  - Deadline proximity
- **Data Persistence**: Stores tasks in JSON format (`tasks_data.json`)

### Frontend (Basic HTML Template)
- **Simple Interface**: Basic HTML template (`scheduler.tsx`) for future web development
- **Modern Design**: Gradient background and clean styling
- **Responsive Layout**: Mobile-friendly design

## Current Implementation Status 📋

### ✅ Completed Features
- Command-line task management (add, edit, delete, view)
- AI-powered schedule generation
- Task persistence with JSON storage
- Priority and difficulty systems
- Deadline tracking and urgency calculation
- Sample data generation
- Schedule export functionality

### 🚧 In Development
- Web interface (basic HTML template exists)
- Flask web application (dependencies prepared)
- Real-time updates and notifications

![Schedule Generation](project_images/Screenshot%202025-07-15%20002533.png)

## Task Properties 📋

Each task includes:
- **Title**: Task name
- **Subject**: Academic subject
- **Deadline**: Due date and time (ISO format)
- **Priority**: 1-5 scale (5 = highest)
- **Estimated Hours**: Time required to complete
- **Task Type**: study, assignment, exam, review
- **Difficulty**: 1-5 scale
- **Completion Status**: 0-100% progress

## Schedule Generation 🧠

The AI scheduler considers:
1. **Urgency Score**: Priority × (10/days_until_deadline) × difficulty
2. **Time Preferences**: Morning for difficult tasks, afternoon for assignments
3. **Workload Balance**: Distributes tasks across available time
4. **Subject Diversity**: Avoids scheduling too many subjects in one day
5. **Break Recommendations**: Suggests breaks for heavy study days

![Task View](project_images/Screenshot%202025-07-15%20002338.png)

## File Structure 📁

```
smart-schedule-automator/
├── simple_main.py      # Main application with CLI interface
├── scheduler.tsx       # Basic HTML template for web interface
├── tasks_data.json     # Task storage (auto-generated)
├── requirements.txt    # Python dependencies
├── run.py             # Startup script
├── project_images/     # Application screenshots
└── README.md          # This file
```

## Usage Examples 💡

### Adding a Task
```
1. Select "Add New Task" from main menu
2. Enter task details:
   - Title: "Physics Midterm Study"
   - Subject: "Physics"
   - Deadline: 2025-07-22
   - Priority: 5
   - Estimated Hours: 8.0
   - Task Type: exam
   - Difficulty: 5
```

### Generating a Schedule
```
1. Select "Generate Study Schedule" from main menu
2. Enter available hours for each day
3. View the optimized weekly schedule
4. Export schedule to file if needed
```

## Customization 🎨

### Adding New Task Types
Edit the `Task` class in `simple_main.py` and update the scheduler preferences.

### Modifying Schedule Algorithm
Edit the `SimpleAIScheduler` class in `simple_main.py`:
- Adjust urgency calculation
- Change time preferences
- Modify session duration limits

### Styling Changes
The HTML template in `scheduler.tsx` can be customized for future web development.

## Troubleshooting 🔧

### Common Issues

**Dependencies not found:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Data not loading:**
- Check that `tasks_data.json` exists and is readable
- Ensure the application has write permissions

**Port already in use (for future web version):**
```bash
# Kill process on port 5000
lsof -ti:5000 | xargs kill -9
```

## Development Roadmap 🗺️

### Phase 1: Core Functionality ✅
- [x] Command-line interface
- [x] Task management system
- [x] AI scheduling algorithm
- [x] Data persistence

### Phase 2: Web Interface 🚧
- [ ] Flask web application
- [ ] Real-time updates
- [ ] Interactive dashboard
- [ ] API endpoints

### Phase 3: Advanced Features 📈
- [ ] Calendar integration
- [ ] Email notifications
- [ ] Mobile app
- [ ] Team collaboration

## Contributing 🤝

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License 📄

This project is licensed under the MIT License - see the LICENSE file for details.

## Support 💬

If you encounter any issues or have questions:
1. Check the troubleshooting section
2. Review the console for error messages
3. Ensure all dependencies are installed correctly

---

**Happy Studying! 📚✨** 