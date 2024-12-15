import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId

class NotesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Notes App")
        self.root.geometry("400x600")
        self.root.configure(bg="#1A1A1A")

        # MongoDB Connection
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["notes_app"]
        self.notes_collection = self.db["notes"]
        self.users_collection = self.db["users"]
        self.categories_collection = self.db["categories"]  # New collection for categories

        self.current_user = None  # To store the logged-in user
        self.additional_properties = {}  # Store custom properties

        self.initialize_welcome_page()

    def initialize_welcome_page(self):
        # Clear frame
        for widget in self.root.winfo_children():
            widget.destroy()

        # Welcome Title
        title = tk.Label(self.root, text="Welcome to Notes App", font=("Helvetica", 18), bg="#1A1A1A", fg="#00FFCC")
        title.pack(pady=30)

        # Signup Button
        signup_button = tk.Button(self.root, text="Sign Up", bg="#00FFCC", fg="#1A1A1A", font=("Helvetica", 14),
                                   command=self.initialize_signup_page)
        signup_button.pack(pady=10)

        # Login Button
        login_button = tk.Button(self.root, text="Login", bg="#F2A900", fg="#1A1A1A", font=("Helvetica", 14),
                                  command=self.initialize_login_page)
        login_button.pack(pady=10)

    def initialize_signup_page(self):
        # Clear frame
        for widget in self.root.winfo_children():
            widget.destroy()

        # Signup Title
        tk.Label(self.root, text="Sign Up", font=("Helvetica", 18), bg="#1A1A1A", fg="#00FFCC").pack(pady=20)

        # Fields
        tk.Label(self.root, text="Username", bg="#1A1A1A", fg="#FFFFFF").pack(anchor="w", padx=20)
        username_entry = tk.Entry(self.root, font=("Helvetica", 14))
        username_entry.pack(fill="x", padx=20)

        tk.Label(self.root, text="Email", bg="#1A1A1A", fg="#FFFFFF").pack(anchor="w", padx=20)
        email_entry = tk.Entry(self.root, font=("Helvetica", 14))
        email_entry.pack(fill="x", padx=20)

        tk.Label(self.root, text="Password", bg="#1A1A1A", fg="#FFFFFF").pack(anchor="w", padx=20)
        password_entry = tk.Entry(self.root, font=("Helvetica", 14), show="*")
        password_entry.pack(fill="x", padx=20)

        tk.Label(self.root, text="Confirm Password", bg="#1A1A1A", fg="#FFFFFF").pack(anchor="w", padx=20)
        confirm_password_entry = tk.Entry(self.root, font=("Helvetica", 14), show="*")
        confirm_password_entry.pack(fill="x", padx=20)

        # Sign Up Button
        tk.Button(self.root, text="Sign Up", bg="#00FFCC", fg="#1A1A1A", font=("Helvetica", 14),
                  command=lambda: self.signup_user(
                      username_entry.get(),
                      email_entry.get(),
                      password_entry.get(),
                      confirm_password_entry.get()
                  )).pack(pady=20)

        # Back Button
        tk.Button(self.root, text="Back", bg="#F2A900", fg="#1A1A1A", font=("Helvetica", 14),
                  command=self.initialize_welcome_page).pack(pady=10)

    def signup_user(self, username, email, password, confirm_password):
        if not username or not email or not password:
            messagebox.showerror("Error", "All fields are required!")
            return

        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match!")
            return

        if self.users_collection.find_one({"email": email}):
            messagebox.showerror("Error", "Email already exists!")
        else:
            user_id = self.users_collection.insert_one({"username": username, "email": email, "password": password}).inserted_id
            self.current_user = self.users_collection.find_one({"_id": user_id})  # Save the user document in memory
            messagebox.showinfo("Success", "User registered successfully!")
            self.initialize_main_page()

    def initialize_login_page(self):
        # Clear frame
        for widget in self.root.winfo_children():
            widget.destroy()

        # Login Title
        tk.Label(self.root, text="Login", font=("Helvetica", 18), bg="#1A1A1A", fg="#00FFCC").pack(pady=20)

        # Fields
        tk.Label(self.root, text="Email", bg="#1A1A1A", fg="#FFFFFF").pack(anchor="w", padx=20)
        email_entry = tk.Entry(self.root, font=("Helvetica", 14))
        email_entry.pack(fill="x", padx=20)

        tk.Label(self.root, text="Password", bg="#1A1A1A", fg="#FFFFFF").pack(anchor="w", padx=20)
        password_entry = tk.Entry(self.root, font=("Helvetica", 14), show="*")
        password_entry.pack(fill="x", padx=20)

        # Login Button
        tk.Button(self.root, text="Login", bg="#00FFCC", fg="#1A1A1A", font=("Helvetica", 14),
                  command=lambda: self.login_user(email_entry.get(), password_entry.get())).pack(pady=20)

        # Back Button
        tk.Button(self.root, text="Back", bg="#F2A900", fg="#1A1A1A", font=("Helvetica", 14),
                  command=self.initialize_welcome_page).pack(pady=10)

    def login_user(self, email, password):
        user = self.users_collection.find_one({"email": email, "password": password})
        if user:
            self.current_user = user  # Save the user document in memory
            self.initialize_main_page()
        else:
            messagebox.showerror("Error", "Invalid email or password!")

    def initialize_main_page(self):
        # Clear frame
        for widget in self.root.winfo_children():
            widget.destroy()

        # Title
        title = tk.Label(self.root, text="Notes", font=("Helvetica", 24), bg="#1A1A1A", fg="#FFFFFF")
        title.pack(pady=20)

        # Dropdown for categories
        categories = self.categories_collection.find({"user_id": self.current_user["_id"]})
        category_options = [category["name"] for category in categories]
        selected_category = tk.StringVar(self.root)
        selected_category.set("All")
        dropdown = tk.OptionMenu(self.root, selected_category, *category_options)
        dropdown.pack(pady=10)

        # Fetch notes for the logged-in user
        notes = self.notes_collection.find({"user_id": self.current_user["_id"]})
        for note in notes:
            note_frame = tk.Frame(self.root, bg="#F2A900", height=80, bd=5, relief=tk.RIDGE)
            note_frame.pack(fill="x", padx=10, pady=5)

            # Display note details
            tk.Label(note_frame, text=note["title"], font=("Helvetica", 14), bg="#F2A900", fg="#1A1A1A").pack(anchor="w")
            tk.Label(note_frame, text=note["content"], font=("Helvetica", 10), bg="#F2A900", fg="#1A1A1A").pack(anchor="w")
            tk.Label(note_frame, text=note["date"], font=("Helvetica", 8), bg="#F2A900", fg="#1A1A1A").pack(anchor="e")

            # Add Remove and Edit Buttons
            remove_button = tk.Button(note_frame, text="Remove", bg="#FF4C4C", fg="#FFFFFF",
                                       command=lambda note_id=note["_id"]: self.remove_note(note_id))
            remove_button.pack(side="right", padx=5, pady=5)

            edit_button = tk.Button(note_frame, text="Edit", bg="#00CCFF", fg="#FFFFFF",
                                     command=lambda note=note: self.open_edit_note_window(note))
            edit_button.pack(side="right", padx=5, pady=5)

        # Add button
        add_button = tk.Button(self.root, text="+", bg="#00FFCC", fg="#1A1A1A", font=("Helvetica", 18),
                                command=self.initialize_add_note_page)
        add_button.pack(side="bottom", pady=10)

        # Category management button
        manage_categories_button = tk.Button(self.root, text="Manage Categories", bg="#F2A900", fg="#1A1A1A",
                                              font=("Helvetica", 14), command=self.initialize_category_page)
        manage_categories_button.pack(side="bottom", pady=5)

    def initialize_add_note_page(self):
        # Clear frame
        for widget in self.root.winfo_children():
            widget.destroy()

        # Title
        tk.Label(self.root, text="Add Note", font=("Helvetica", 24), bg="#1A1A1A", fg="#FFFFFF").pack(pady=20)

        # Title field
        title_label = tk.Label(self.root, text="Title", bg="#1A1A1A", fg="#00FFCC")
        title_label.pack(anchor="w", padx=20)
        title_entry = tk.Entry(self.root, font=("Helvetica", 14))
        title_entry.pack(fill="x", padx=20)

        # Content field
        content_label = tk.Label(self.root, text="Content", bg="#1A1A1A", fg="#00FFCC")
        content_label.pack(anchor="w", padx=20, pady=10)
        content_entry = tk.Text(self.root, height=5, font=("Helvetica", 14))
        content_entry.pack(fill="x", padx=20)

        # Category field
        categories = self.categories_collection.find({"user_id": self.current_user["_id"]})
        category_options = [category["name"] for category in categories]
        selected_category = tk.StringVar(self.root)
        selected_category.set("Select Category")
        dropdown = tk.OptionMenu(self.root, selected_category, *category_options)
        dropdown.pack(pady=10)

        # Add Property Button
        add_property_button = tk.Button(self.root, text="Add Property", bg="#F2A900", fg="#1A1A1A",
                                        command=self.open_add_property_window)
        add_property_button.pack(pady=10)

        # Buttons
        tk.Button(self.root, text="Add Note", bg="#00FFCC", fg="#1A1A1A", font=("Helvetica", 14),
                  command=lambda: self.add_note(title_entry.get(), content_entry.get("1.0", tk.END).strip(),
                                                selected_category.get())).pack(pady=10)
        tk.Button(self.root, text="Back", bg="#F2A900", fg="#1A1A1A", font=("Helvetica", 14),
                  command=self.initialize_main_page).pack(pady=10)

    def initialize_category_page(self):
        # Clear frame
        for widget in self.root.winfo_children():
            widget.destroy()

        # Title
        tk.Label(self.root, text="Manage Categories", font=("Helvetica", 18), bg="#1A1A1A", fg="#00FFCC").pack(pady=20)

        # List existing categories
        categories = self.categories_collection.find({"user_id": self.current_user["_id"]})
        for category in categories:
            frame = tk.Frame(self.root, bg="#F2A900", bd=2, relief=tk.RIDGE)
            frame.pack(fill="x", padx=10, pady=5)

            tk.Label(frame, text=category["name"], font=("Helvetica", 14), bg="#F2A900", fg="#1A1A1A").pack(side="left")

            tk.Button(frame, text="Delete", bg="#FF4C4C", fg="#FFFFFF",
                      command=lambda cat_id=category["_id"]: self.delete_category(cat_id)).pack(side="right", padx=5)

        # Add new category
        tk.Label(self.root, text="Add New Category", font=("Helvetica", 14), bg="#1A1A1A", fg="#00FFCC").pack(pady=10)
        category_name_entry = tk.Entry(self.root, font=("Helvetica", 14))
        category_name_entry.pack(fill="x", padx=20, pady=5)

        tk.Button(self.root, text="Add", bg="#00FFCC", fg="#1A1A1A", font=("Helvetica", 14),
                  command=lambda: self.add_category(category_name_entry.get())).pack(pady=10)

        # Back Button
        tk.Button(self.root, text="Back", bg="#F2A900", fg="#1A1A1A", font=("Helvetica", 14),
                  command=self.initialize_main_page).pack(pady=10)

    def add_category(self, name):
        if not name:
            messagebox.showerror("Error", "Category name cannot be empty!")
            return

        self.categories_collection.insert_one({"name": name, "user_id": self.current_user["_id"]})
        messagebox.showinfo("Success", "Category added successfully!")
        self.initialize_category_page()

    def delete_category(self, cat_id):
        self.categories_collection.delete_one({"_id": ObjectId(cat_id)})
        messagebox.showinfo("Success", "Category deleted successfully!")
        self.initialize_category_page()

    def add_note(self, title, content, category):
        if not title or not content:
            messagebox.showerror("Error", "Title and content cannot be empty!")
            return

        if category == "Select Category":
            messagebox.showerror("Error", "Please select a category!")
            return

        note = {
            "title": title,
            "content": content,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user_id": self.current_user["_id"],
            "properties": self.additional_properties,
            "category": category
        }
        self.notes_collection.insert_one(note)
        messagebox.showinfo("Success", "Note added successfully!")
        self.initialize_main_page()

if __name__ == "__main__":
    root = tk.Tk()
    app = NotesApp(root)
    root.mainloop()

