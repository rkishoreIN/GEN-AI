import streamlit as st
import json
import os
from datetime import datetime
from typing import List, Dict, Any
import requests
import base64

# Configuration
TASKS_FILE = "tasks.json"

class SimpleCloudTaskManager:
    def __init__(self):
        self.tasks = self.load_tasks()
        self.user_id = None
    
    def set_user_id(self, user_id: str):
        """Set the current user ID"""
        self.user_id = user_id
    
    def load_tasks(self) -> List[Dict[str, Any]]:
        """Load tasks from JSON file"""
        if os.path.exists(TASKS_FILE):
            try:
                with open(TASKS_FILE, 'r', encoding='utf-8') as f:
                    all_tasks = json.load(f)
                    # Filter tasks for current user
                    if self.user_id:
                        return [task for task in all_tasks if task.get('user_id') == self.user_id]
                    return all_tasks
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []
    
    def save_tasks(self):
        """Save tasks to JSON file"""
        try:
            # Load all tasks first
            all_tasks = []
            if os.path.exists(TASKS_FILE):
                try:
                    with open(TASKS_FILE, 'r', encoding='utf-8') as f:
                        all_tasks = json.load(f)
                except:
                    all_tasks = []
            
            # Update tasks for current user
            if self.user_id:
                # Remove old tasks for this user
                all_tasks = [task for task in all_tasks if task.get('user_id') != self.user_id]
                # Add current user's tasks
                all_tasks.extend(self.tasks)
            
            with open(TASKS_FILE, 'w', encoding='utf-8') as f:
                json.dump(all_tasks, f, indent=2, ensure_ascii=False)
        except Exception as e:
            st.error(f"Error saving tasks: {e}")
    
    def add_task(self, title: str, description: str = "", priority: str = "Medium") -> bool:
        """Add a new task"""
        if not title.strip():
            return False
        
        task = {
            "id": len(self.tasks) + 1,
            "user_id": self.user_id,
            "title": title.strip(),
            "description": description.strip(),
            "priority": priority,
            "completed": False,
            "created_at": datetime.now().isoformat(),
            "completed_at": None
        }
        
        self.tasks.append(task)
        self.save_tasks()
        return True
    
    def mark_complete(self, task_id: int) -> bool:
        """Mark a task as complete"""
        for task in self.tasks:
            if task["id"] == task_id:
                task["completed"] = True
                task["completed_at"] = datetime.now().isoformat()
                self.save_tasks()
                return True
        return False
    
    def mark_incomplete(self, task_id: int) -> bool:
        """Mark a task as incomplete"""
        for task in self.tasks:
            if task["id"] == task_id:
                task["completed"] = False
                task["completed_at"] = None
                self.save_tasks()
                return True
        return False
    
    def delete_task(self, task_id: int) -> bool:
        """Delete a task"""
        for i, task in enumerate(self.tasks):
            if task["id"] == task_id:
                del self.tasks[i]
                self.save_tasks()
                return True
        return False
    
    def get_tasks(self, show_completed: bool = True) -> List[Dict[str, Any]]:
        """Get tasks, optionally filtering completed ones"""
        if show_completed:
            return self.tasks
        return [task for task in self.tasks if not task["completed"]]
    
    def get_task_stats(self) -> Dict[str, int]:
        """Get task statistics"""
        total = len(self.tasks)
        completed = len([task for task in self.tasks if task["completed"]])
        pending = total - completed
        
        return {
            "total": total,
            "completed": completed,
            "pending": pending
        }

def main():
    st.set_page_config(
        page_title="Cloud Task Manager",
        page_icon="☁️",
        layout="wide"
    )
    
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None
    if 'task_manager' not in st.session_state:
        st.session_state.task_manager = SimpleCloudTaskManager()
    
    # Authentication check
    if not st.session_state.authenticated:
        show_login_page()
    else:
        show_main_app()

def show_login_page():
    """Display login page"""
    st.title("☁️ Cloud Task Manager")
    st.markdown("### Sign in to manage your tasks")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; border: 2px dashed #ccc; border-radius: 10px;">
            <h3>🔐 Simple Authentication</h3>
            <p>Enter your name and email to get started with your personal task manager.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Simple login form
        with st.form("login_form"):
            name = st.text_input("Your Name", placeholder="Enter your name...")
            email = st.text_input("Email Address", placeholder="Enter your email...")
            
            submitted = st.form_submit_button("🚀 Sign In", use_container_width=True, type="primary")
            
            if submitted:
                if name.strip() and email.strip():
                    # Create a simple user ID from email
                    user_id = email.strip().lower().replace("@", "_").replace(".", "_")
                    
                    st.session_state.authenticated = True
                    st.session_state.user_info = {
                        'user_id': user_id,
                        'email': email.strip(),
                        'name': name.strip(),
                        'picture': f"https://ui-avatars.com/api/?name={name.replace(' ', '+')}&background=1f77b4&color=fff"
                    }
                    st.session_state.task_manager.set_user_id(user_id)
                    st.rerun()
                else:
                    st.error("❌ Please enter both name and email!")
        
        st.markdown("---")
        st.caption("💾 Your tasks are saved locally and synced across sessions.")

def show_main_app():
    """Display main application"""
    user_info = st.session_state.user_info
    task_manager = st.session_state.task_manager
    
    # Header with user info
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.title("☁️ Cloud Task Manager")
    
    with col2:
        st.markdown(f"""
        <div style="text-align: right;">
            <img src="{user_info['picture']}" width="40" height="40" style="border-radius: 50%;">
            <br>
            <strong>{user_info['name']}</strong><br>
            <small>{user_info['email']}</small>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚪 Sign Out", key="signout"):
            st.session_state.authenticated = False
            st.session_state.user_info = None
            st.session_state.task_manager = SimpleCloudTaskManager()
            st.rerun()
    
    st.markdown("---")
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["Add Task", "View Tasks", "Task Statistics"]
    )
    
    # Add Task Page
    if page == "Add Task":
        st.header("➕ Add New Task")
        
        with st.form("add_task_form"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                title = st.text_input(
                    "Task Title *",
                    placeholder="Enter task title...",
                    help="Required field"
                )
                description = st.text_area(
                    "Description",
                    placeholder="Enter task description (optional)...",
                    height=100
                )
            
            with col2:
                priority = st.selectbox(
                    "Priority",
                    ["Low", "Medium", "High"],
                    index=1
                )
            
            submitted = st.form_submit_button("Add Task", use_container_width=True)
            
            if submitted:
                if task_manager.add_task(title, description, priority):
                    st.success(f"✅ Task '{title}' added successfully!")
                    st.rerun()
                else:
                    st.error("❌ Please enter a task title!")
    
    # View Tasks Page
    elif page == "View Tasks":
        st.header("📋 View Tasks")
        
        # Filters
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            show_completed = st.checkbox("Show completed tasks", value=True)
        
        with col2:
            priority_filter = st.selectbox(
                "Filter by priority",
                ["All", "Low", "Medium", "High"]
            )
        
        with col3:
            sort_by = st.selectbox(
                "Sort by",
                ["Created Date", "Priority", "Title"]
            )
        
        # Get filtered tasks
        tasks = task_manager.get_tasks(show_completed)
        
        # Apply priority filter
        if priority_filter != "All":
            tasks = [task for task in tasks if task["priority"] == priority_filter]
        
        # Apply sorting
        if sort_by == "Created Date":
            tasks.sort(key=lambda x: x["created_at"], reverse=True)
        elif sort_by == "Priority":
            priority_order = {"High": 3, "Medium": 2, "Low": 1}
            tasks.sort(key=lambda x: priority_order.get(x["priority"], 0), reverse=True)
        elif sort_by == "Title":
            tasks.sort(key=lambda x: x["title"].lower())
        
        # Display tasks
        if not tasks:
            st.info("📝 No tasks found. Add a new task to get started!")
        else:
            for task in tasks:
                with st.container():
                    # Task card
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        # Task status and title
                        status_icon = "✅" if task["completed"] else "⏳"
                        priority_color = {
                            "High": "🔴",
                            "Medium": "🟡", 
                            "Low": "🟢"
                        }
                        
                        st.markdown(f"""
                        **{status_icon} {task['title']}** {priority_color[task['priority']]}
                        """)
                        
                        if task["description"]:
                            st.markdown(f"*{task['description']}*")
                        
                        # Task metadata
                        created_date = datetime.fromisoformat(task["created_at"]).strftime("%Y-%m-%d %H:%M")
                        if task["completed"]:
                            completed_date = datetime.fromisoformat(task["completed_at"]).strftime("%Y-%m-%d %H:%M")
                            st.caption(f"Created: {created_date} | Completed: {completed_date}")
                        else:
                            st.caption(f"Created: {created_date}")
                    
                    with col2:
                        # Mark complete/incomplete button
                        if task["completed"]:
                            if st.button("↩️ Undo", key=f"undo_{task['id']}"):
                                task_manager.mark_incomplete(task["id"])
                                st.rerun()
                        else:
                            if st.button("✅ Complete", key=f"complete_{task['id']}"):
                                task_manager.mark_complete(task["id"])
                                st.rerun()
                    
                    with col3:
                        # Delete button
                        if st.button("🗑️ Delete", key=f"delete_{task['id']}"):
                            task_manager.delete_task(task["id"])
                            st.rerun()
                    
                    st.markdown("---")
    
    # Task Statistics Page
    elif page == "Task Statistics":
        st.header("📊 Task Statistics")
        
        stats = task_manager.get_task_stats()
        
        # Display statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Total Tasks",
                value=stats["total"],
                delta=None
            )
        
        with col2:
            st.metric(
                label="Completed Tasks",
                value=stats["completed"],
                delta=f"{stats['completed']}/{stats['total']}" if stats['total'] > 0 else "0/0"
            )
        
        with col3:
            st.metric(
                label="Pending Tasks",
                value=stats["pending"],
                delta=f"{stats['pending']}/{stats['total']}" if stats['total'] > 0 else "0/0"
            )
        
        # Progress bar
        if stats["total"] > 0:
            completion_rate = stats["completed"] / stats["total"]
            st.progress(completion_rate)
            st.caption(f"Completion Rate: {completion_rate:.1%}")
        
        # Priority breakdown
        if stats["total"] > 0:
            st.subheader("Priority Breakdown")
            
            priority_counts = {"High": 0, "Medium": 0, "Low": 0}
            for task in task_manager.tasks:
                priority_counts[task["priority"]] += 1
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("High Priority", priority_counts["High"])
            with col2:
                st.metric("Medium Priority", priority_counts["Medium"])
            with col3:
                st.metric("Low Priority", priority_counts["Low"])
    
    # Footer
    st.markdown("---")
    st.caption("☁️ Tasks are saved locally and synced across sessions")

if __name__ == "__main__":
    main()
