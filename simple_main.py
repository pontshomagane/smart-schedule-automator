#!/usr/bin/env python3
"""
Smart Schedule Automator - Simple Local Version
No external dependencies required - uses only Python standard library
"""

import json
import datetime
import os
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class Task:
    """Represents a study task or deadline"""
    id: str
    title: str
    subject: str
    deadline: str  # ISO format string
    priority: int  # 1-5 (5 = highest)
    estimated_hours: float
    completion_status: float = 0.0  # 0-1 (1 = completed)
    task_type: str = "study"  # study, assignment, exam, review
    difficulty: int = 3  # 1-5 scale
    
    def get_deadline_datetime(self) -> datetime.datetime:
        """Convert deadline string to datetime object"""
        return datetime.datetime.fromisoformat(self.deadline)
    
    def days_until_deadline(self) -> int:
        """Calculate days remaining until deadline"""
        return (self.get_deadline_datetime() - datetime.datetime.now()).days

class SimpleAIScheduler:
    """Simple AI-like scheduling algorithm using heuristics"""
    
    def __init__(self):
        self.time_preferences = {
            'morning': {'start': 9, 'focus_multiplier': 1.0},
            'afternoon': {'start': 14, 'focus_multiplier': 0.8},
            'evening': {'start': 19, 'focus_multiplier': 0.6}
        }
    
    def generate_schedule(self, tasks: List[Task], available_hours: Dict[str, float]) -> Dict:
        """Generate weekly study schedule"""
        
        if not tasks:
            return {}
        
        # Calculate task urgency scores
        scored_tasks = []
        for task in tasks:
            if task.completion_status >= 1.0:
                continue
                
            days_left = max(1, task.days_until_deadline())
            urgency = task.priority * (10 / days_left) * (1 + task.difficulty * 0.1)
            
            scored_tasks.append({
                'task': task,
                'urgency': urgency,
                'remaining_hours': task.estimated_hours * (1 - task.completion_status)
            })
        
        # Sort by urgency (highest first)
        scored_tasks.sort(key=lambda x: x['urgency'], reverse=True)
        
        # Generate 7-day schedule
        schedule = {}
        start_date = datetime.datetime.now().date()
        
        for day_offset in range(7):
            current_date = start_date + datetime.timedelta(days=day_offset)
            day_name = current_date.strftime("%A")
            
            schedule[day_name] = {
                'date': current_date.isoformat(),
                'sessions': [],
                'total_hours': 0.0,
                'available_hours': available_hours.get(day_name, 0),
                'recommendations': []
            }
            
            # Distribute tasks for this day
            available_time = available_hours.get(day_name, 0)
            used_time = 0.0
            
            for scored_task in scored_tasks:
                if used_time >= available_time:
                    break
                
                task = scored_task['task']
                remaining_hours = scored_task['remaining_hours']
                
                if remaining_hours <= 0:
                    continue
                
                # Calculate session duration
                session_duration = min(
                    available_time - used_time,  # Remaining time today
                    2.0,  # Max 2 hours per session
                    remaining_hours  # Don't exceed task requirement
                )
                
                if session_duration >= 0.5:  # Minimum 30 minutes
                    optimal_time = self._get_optimal_time(task, day_name)
                    
                    session = {
                        'task_id': task.id,
                        'title': task.title,
                        'subject': task.subject,
                        'duration': round(session_duration, 1),
                        'priority': task.priority,
                        'task_type': task.task_type,
                        'difficulty': task.difficulty,
                        'optimal_time': optimal_time,
                        'deadline_days': task.days_until_deadline()
                    }
                    
                    schedule[day_name]['sessions'].append(session)
                    used_time += session_duration
                    
                    # Update remaining hours for next iteration
                    scored_task['remaining_hours'] -= session_duration
            
            schedule[day_name]['total_hours'] = used_time
            schedule[day_name]['recommendations'] = self._generate_recommendations(
                schedule[day_name], day_name
            )
        
        return schedule
    
    def _get_optimal_time(self, task: Task, day: str) -> str:
        """Determine optimal time slot for task"""
        
        # High difficulty tasks work best in morning
        if task.difficulty >= 4:
            return 'morning'
        
        # Task type preferences
        type_preferences = {
            'exam': 'morning',
            'assignment': 'afternoon',
            'review': 'evening',
            'study': 'morning'
        }
        
        return type_preferences.get(task.task_type, 'morning')
    
    def _generate_recommendations(self, day_schedule: Dict, day: str) -> List[str]:
        """Generate AI-like recommendations"""
        recommendations = []
        
        total_hours = day_schedule['total_hours']
        available_hours = day_schedule['available_hours']
        sessions = day_schedule['sessions']
        
        # Workload recommendations
        if total_hours > available_hours * 0.9:
            recommendations.append("⚠️ Heavy study day - schedule regular breaks")
        elif total_hours < available_hours * 0.5:
            recommendations.append("💡 Light day - consider adding review sessions")
        
        # Subject diversity
        subjects = set(session['subject'] for session in sessions)
        if len(subjects) > 3:
            recommendations.append("🔄 Multiple subjects - plan transition time")
        
        # Difficulty balance
        difficult_sessions = [s for s in sessions if s['difficulty'] >= 4]
        if len(difficult_sessions) > 1:
            recommendations.append("🧠 Multiple challenging topics - space them out")
        
        # Urgent tasks
        urgent_sessions = [s for s in sessions if s['deadline_days'] <= 2]
        if urgent_sessions:
            recommendations.append("🚨 Urgent deadlines - prioritize these sessions")
        
        # Weekend specific
        if day in ['Saturday', 'Sunday']:
            recommendations.append("📅 Weekend - good time for longer study sessions")
        
        return recommendations

class TaskManager:
    """Manages tasks and persistent storage"""
    
    def __init__(self, data_file: str = "tasks_data.json"):
        self.data_file = data_file
        self.tasks: List[Task] = []
        self.load_data()
    
    def add_task(self, task: Task) -> bool:
        """Add a new task"""
        try:
            self.tasks.append(task)
            self.save_data()
            logger.info(f"Added task: {task.title}")
            return True
        except Exception as e:
            logger.error(f"Failed to add task: {e}")
            return False
    
    def update_task(self, task_id: str, **updates) -> bool:
        """Update task properties"""
        try:
            for task in self.tasks:
                if task.id == task_id:
                    for key, value in updates.items():
                        if hasattr(task, key):
                            setattr(task, key, value)
                    self.save_data()
                    logger.info(f"Updated task {task_id}")
                    return True
            return False
        except Exception as e:
            logger.error(f"Failed to update task: {e}")
            return False
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task"""
        try:
            original_length = len(self.tasks)
            self.tasks = [t for t in self.tasks if t.id != task_id]
            if len(self.tasks) < original_length:
                self.save_data()
                logger.info(f"Deleted task {task_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete task: {e}")
            return False
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a specific task"""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    def get_all_tasks(self) -> List[Task]:
        """Get all tasks"""
        return self.tasks.copy()
    
    def get_incomplete_tasks(self) -> List[Task]:
        """Get tasks that are not completed"""
        return [task for task in self.tasks if task.completion_status < 1.0]
    
    def save_data(self) -> bool:
        """Save tasks to file"""
        try:
            data = {
                'tasks': [asdict(task) for task in self.tasks],
                'last_updated': datetime.datetime.now().isoformat()
            }
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to save data: {e}")
            return False
    
    def load_data(self) -> bool:
        """Load tasks from file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                
                self.tasks = []
                for task_data in data.get('tasks', []):
                    self.tasks.append(Task(**task_data))
                
                logger.info(f"Loaded {len(self.tasks)} tasks from {self.data_file}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            return False

class ScheduleApp:
    """Main application class"""
    
    def __init__(self):
        self.task_manager = TaskManager()
        self.scheduler = SimpleAIScheduler()
        self.current_schedule = {}
    
    def run(self):
        """Run the interactive application"""
        print("🎓 Smart Schedule Automator")
        print("=" * 50)
        
        # Initialize with sample data if no tasks exist
        if not self.task_manager.get_all_tasks():
            self.create_sample_tasks()
        
        while True:
            self.show_main_menu()
            choice = input("\nEnter your choice (1-8): ").strip()
            
            if choice == '1':
                self.view_tasks()
            elif choice == '2':
                self.add_task_interactive()
            elif choice == '3':
                self.update_task_interactive()
            elif choice == '4':
                self.delete_task_interactive()
            elif choice == '5':
                self.generate_schedule_interactive()
            elif choice == '6':
                self.view_current_schedule()
            elif choice == '7':
                self.export_schedule()
            elif choice == '8':
                print("\n👋 Thanks for using Smart Schedule Automator!")
                break
            else:
                print("❌ Invalid choice. Please try again.")
    
    def show_main_menu(self):
        """Display main menu"""
        print("\n" + "=" * 50)
        print("📋 Main Menu")
        print("1. 📝 View all tasks")
        print("2. ➕ Add new task")
        print("3. ✏️  Update task")
        print("4. ❌ Delete task")
        print("5. 🤖 Generate AI schedule")
        print("6. 📅 View current schedule")
        print("7. 💾 Export schedule")
        print("8. 🚪 Exit")
    
    def view_tasks(self):
        """Display all tasks"""
        tasks = self.task_manager.get_all_tasks()
        
        if not tasks:
            print("\n📭 No tasks found.")
            return
        
        print(f"\n📋 All Tasks ({len(tasks)} total)")
        print("-" * 60)
        
        for i, task in enumerate(tasks, 1):
            status = "✅" if task.completion_status >= 1.0 else "📝"
            progress = int(task.completion_status * 100)
            days_left = task.days_until_deadline()
            
            print(f"{i}. {status} {task.title}")
            print(f"   📚 Subject: {task.subject}")
            print(f"   📅 Deadline: {days_left} days")
            print(f"   ⭐ Priority: {task.priority}/5")
            print(f"   📊 Progress: {progress}%")
            print(f"   🎯 Type: {task.task_type}")
            print(f"   🔥 Difficulty: {task.difficulty}/5")
            print()
    
    def add_task_interactive(self):
        """Interactive task addition"""
        print("\n➕ Add New Task")
        print("-" * 20)
        
        try:
            title = input("📝 Task title: ").strip()
            if not title:
                print("❌ Title cannot be empty.")
                return
            
            subject = input("📚 Subject: ").strip()
            if not subject:
                subject = "General"
            
            days = int(input("📅 Days until deadline: "))
            deadline = datetime.datetime.now() + datetime.timedelta(days=days)
            
            priority = int(input("⭐ Priority (1-5): "))
            priority = max(1, min(5, priority))
            
            estimated_hours = float(input("⏰ Estimated hours: "))
            
            difficulty = int(input("🔥 Difficulty (1-5): "))
            difficulty = max(1, min(5, difficulty))
            
            task_type = input("🎯 Task type (study/assignment/exam/review): ").strip().lower()
            if task_type not in ['study', 'assignment', 'exam', 'review']:
                task_type = 'study'
            
            # Generate unique ID
            task_id = str(len(self.task_manager.get_all_tasks()) + 1)
            
            task = Task(
                id=task_id,
                title=title,
                subject=subject,
                deadline=deadline.isoformat(),
                priority=priority,
                estimated_hours=estimated_hours,
                task_type=task_type,
                difficulty=difficulty
            )
            
            if self.task_manager.add_task(task):
                print(f"✅ Task '{title}' added successfully!")
            else:
                print("❌ Failed to add task.")
                
        except ValueError:
            print("❌ Invalid input. Please enter valid numbers.")
        except Exception as e:
            print(f"❌ Error adding task: {e}")
    
    def update_task_interactive(self):
        """Interactive task update"""
        tasks = self.task_manager.get_all_tasks()
        
        if not tasks:
            print("\n📭 No tasks to update.")
            return
        
        print("\n✏️ Update Task")
        print("-" * 15)
        
        # Show tasks
        for i, task in enumerate(tasks, 1):
            progress = int(task.completion_status * 100)
            print(f"{i}. {task.title} ({progress}% complete)")
        
        try:
            choice = int(input("\nSelect task number: ")) - 1
            if 0 <= choice < len(tasks):
                task = tasks[choice]
                
                print(f"\nUpdating: {task.title}")
                print("Press Enter to keep current value")
                
                # Update progress
                current_progress = int(task.completion_status * 100)
                progress_input = input(f"Progress ({current_progress}%): ").strip()
                
                if progress_input:
                    new_progress = float(progress_input) / 100
                    new_progress = max(0, min(1, new_progress))
                    
                    if self.task_manager.update_task(task.id, completion_status=new_progress):
                        print(f"✅ Updated progress to {int(new_progress * 100)}%")
                    else:
                        print("❌ Failed to update task.")
                else:
                    print("ℹ️ No changes made.")
            else:
                print("❌ Invalid task number.")
                
        except ValueError:
            print("❌ Invalid input.")
        except Exception as e:
            print(f"❌ Error updating task: {e}")
    
    def delete_task_interactive(self):
        """Interactive task deletion"""
        tasks = self.task_manager.get_all_tasks()
        
        if not tasks:
            print("\n📭 No tasks to delete.")
            return
        
        print("\n❌ Delete Task")
        print("-" * 15)
        
        for i, task in enumerate(tasks, 1):
            print(f"{i}. {task.title}")
        
        try:
            choice = int(input("\nSelect task number to delete: ")) - 1
            if 0 <= choice < len(tasks):
                task = tasks[choice]
                confirm = input(f"Delete '{task.title}'? (y/N): ").strip().lower()
                
                if confirm == 'y':
                    if self.task_manager.delete_task(task.id):
                        print(f"✅ Task '{task.title}' deleted.")
                    else:
                        print("❌ Failed to delete task.")
                else:
                    print("ℹ️ Deletion cancelled.")
            else:
                print("❌ Invalid task number.")
                
        except ValueError:
            print("❌ Invalid input.")
        except Exception as e:
            print(f"❌ Error deleting task: {e}")
    
    def generate_schedule_interactive(self):
        """Interactive schedule generation"""
        print("\n🤖 Generate AI Schedule")
        print("-" * 25)
        
        incomplete_tasks = self.task_manager.get_incomplete_tasks()
        
        if not incomplete_tasks:
            print("✅ No incomplete tasks found!")
            return
        
        print(f"Found {len(incomplete_tasks)} incomplete tasks.")
        
        # Get available hours
        available_hours = {}
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        print("\nEnter available study hours for each day:")
        for day in days:
            try:
                hours = float(input(f"📅 {day}: "))
                available_hours[day] = max(0, hours)
            except ValueError:
                available_hours[day] = 0
        
        # Generate schedule
        print("\n🤖 Generating AI-optimized schedule...")
        self.current_schedule = self.scheduler.generate_schedule(
            incomplete_tasks, available_hours
        )
        
        if self.current_schedule:
            print("✅ Schedule generated successfully!")
            
            # Show summary
            total_hours = sum(day['total_hours'] for day in self.current_schedule.values())
            print(f"📊 Total weekly study time: {total_hours:.1f} hours")
            
            # Show daily breakdown
            for day, schedule in self.current_schedule.items():
                session_count = len(schedule['sessions'])
                if session_count > 0:
                    print(f"   {day}: {schedule['total_hours']:.1f}h ({session_count} sessions)")
        else:
            print("❌ Failed to generate schedule.")
    
    def view_current_schedule(self):
        """Display current schedule"""
        if not self.current_schedule:
            print("\n📭 No schedule generated yet. Use option 5 to generate one.")
            return
        
        print("\n📅 Current AI Schedule")
        print("=" * 40)
        
        for day_name, day_data in self.current_schedule.items():
            print(f"\n📍 {day_name} ({day_data['date']})")
            print(f"   ⏰ Total: {day_data['total_hours']:.1f}h / {day_data['available_hours']:.1f}h available")
            
            if day_data['sessions']:
                print("   📚 Sessions:")
                for session in day_data['sessions']:
                    urgency = "🚨" if session['deadline_days'] <= 2 else "📅"
                    print(f"     • {session['subject']}: {session['title']}")
                    print(f"       ⏱️  {session['duration']}h | 🎯 P{session['priority']} | 🔥 D{session['difficulty']}")
                    print(f"       🕒 {session['optimal_time']} | {urgency} {session['deadline_days']} days left")
                
                if day_data['recommendations']:
                    print("   💡 AI Recommendations:")
                    for rec in day_data['recommendations']:
                        print(f"     {rec}")
            else:
                print("   🎉 No sessions scheduled - free day!")
    
    def export_schedule(self):
        """Export schedule to file"""
        if not self.current_schedule:
            print("\n📭 No schedule to export. Generate one first.")
            return
        
        try:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"schedule_{timestamp}.json"
            
            export_data = {
                'generated_at': datetime.datetime.now().isoformat(),
                'schedule': self.current_schedule,
                'tasks_included': len(self.task_manager.get_incomplete_tasks())
            }
            
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            print(f"✅ Schedule exported to {filename}")
            
            # Also create a readable text version
            txt_filename = f"schedule_{timestamp}.txt"
            with open(txt_filename, 'w', encoding='utf-8') as f:
                f.write("🎓 Smart Schedule Automator - Weekly Plan\n")
                f.write("=" * 50 + "\n\n")
                
                for day_name, day_data in self.current_schedule.items():
                    f.write(f"📍 {day_name} ({day_data['date']})\n")
                    f.write(f"   Total: {day_data['total_hours']:.1f}h\n")
                    
                    if day_data['sessions']:
                        f.write("   Sessions:\n")
                        for session in day_data['sessions']:
                            f.write(f"     • {session['subject']}: {session['title']}\n")
                            f.write(f"       {session['duration']}h | Priority: {session['priority']}/5\n")
                            f.write(f"       Time: {session['optimal_time']} | Deadline: {session['deadline_days']} days\n")
                        
                        if day_data['recommendations']:
                            f.write("   Recommendations:\n")
                            for rec in day_data['recommendations']:
                                f.write(f"     {rec}\n")
                    else:
                        f.write("   No sessions scheduled\n")
                    f.write("\n")
            
            print(f"✅ Readable version exported to {txt_filename}")
            
        except Exception as e:
            print(f"❌ Export failed: {e}")
    
    def create_sample_tasks(self):
        """Create sample tasks for demonstration"""
        sample_tasks = [
            Task(
                id="1",
                title="Calculus Integration Problems",
                subject="Mathematics",
                deadline=(datetime.datetime.now() + datetime.timedelta(days=3)).isoformat(),
                priority=4,
                estimated_hours=5.0,
                task_type="assignment",
                difficulty=4
            ),
            Task(
                id="2",
                title="Physics Midterm Study",
                subject="Physics",
                deadline=(datetime.datetime.now() + datetime.timedelta(days=7)).isoformat(),
                priority=5,
                estimated_hours=8.0,
                task_type="exam",
                difficulty=5
            ),
            Task(
                id="3",
                title="History Essay Research",
                subject="History",
                deadline=(datetime.datetime.now() + datetime.timedelta(days=5)).isoformat(),
                priority=3,
                estimated_hours=4.0,
                task_type="assignment",
                difficulty=3
            ),
            Task(
                id="4",
                title="Chemistry Lab Report",
                subject="Chemistry",
                deadline=(datetime.datetime.now() + datetime.timedelta(days=2)).isoformat(),
                priority=4,
                estimated_hours=3.0,
                task_type="assignment",
                difficulty=3
            )
        ]
        
        for task in sample_tasks:
            self.task_manager.add_task(task)
        
        print("📝 Created sample tasks for demonstration")

def main():
    """Main function"""
    try:
        app = ScheduleApp()
        app.run()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        logger.error(f"Application error: {e}")

if __name__ == "__main__":
    main()