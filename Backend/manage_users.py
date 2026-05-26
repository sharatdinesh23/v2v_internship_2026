import os
import sys
import uuid
from getpass import getpass

# Ensure we can import from the Backend directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import supabase
from argon2 import PasswordHasher

ph = PasswordHasher()

def get_roles():
    res = supabase.table("Roles").select("*").execute()
    if not res.data:
        print("No roles found in the database. Ensure the Roles table is configured.")
        sys.exit(1)
    return {role['role_name']: role['id'] for role in res.data}

def create_admin():
    print("\n--- Create New Admin / User ---")
    name = input("Name: ").strip()
    email = input("Email: ").strip()
    
    if not name or not email:
        print("Error: Name and Email cannot be empty.")
        return

    # Check if user already exists
    res = supabase.table("Profiles").select("id").eq("email", email).execute()
    if res.data:
        print(f"Error: User with email '{email}' already exists.")
        return
        
    password = getpass("Password: ")
    if not password:
        print("Error: Password cannot be empty.")
        return
        
    hashed_pass = ph.hash(password)
    
    roles = get_roles()
    print("\nAvailable Roles:")
    role_names = list(roles.keys())
    for i, r in enumerate(role_names, 1):
        print(f"{i}. {r}")
        
    role_choice = input("Select a role (number or name) [default: admin]: ").strip()
    
    # Resolve the selected role
    selected_role_name = "admin"
    if role_choice.isdigit():
        idx = int(role_choice) - 1
        if 0 <= idx < len(role_names):
            selected_role_name = role_names[idx]
    elif role_choice in roles:
        selected_role_name = role_choice
    
    # Fallback to the first available role if 'admin' isn't explicitly defined safely 
    if selected_role_name not in roles:
        selected_role_name = role_names[0]
            
    role_id = roles[selected_role_name]
    
    new_id = str(uuid.uuid4())
    insert_res = supabase.table("Profiles").insert({
        "id": new_id,
        "name": name,
        "email": email,
        "password": hashed_pass,
        "role_id": role_id
    }).execute()
    
    if insert_res.data:
        print(f"\n✅ Success! Created user '{name}' ({email}) with role '{selected_role_name}'.")
    else:
        print("\n❌ Failed to create user.")


def change_password():
    print("\n--- Change Existing User Password ---")
    email = input("User Email: ").strip()
    
    if not email:
        return
        
    res = supabase.table("Profiles").select("id, name").eq("email", email).execute()
    if not res.data:
        print(f"Error: User with email '{email}' not found in the Profiles table.")
        return
        
    user_id = res.data[0]['id']
    user_name = res.data[0]['name']
    
    print(f"Found user: {user_name}")
    new_password = getpass("New Password: ")
    
    if not new_password:
        print("Error: Password cannot be empty.")
        return
        
    hashed_pass = ph.hash(new_password)
    
    update_res = supabase.table("Profiles").update({"password": hashed_pass}).eq("id", user_id).execute()
    if update_res.data:
        print(f"\n✅ Success! Password updated for '{email}'.")
    else:
        print("\n❌ Failed to update password.")


def main():
    while True:
        print("\n" + "="*30)
        print(" User Management CLI")
        print("="*30)
        print("1. Create a new user")
        print("2. Change password for an existing user")
        print("3. Exit")
        
        choice = input("\nSelect an option [1-3]: ").strip()
        
        if choice == "1":
            try:
                create_admin()
            except Exception as e:
                print(f"\nAn error occurred: {e}")
        elif choice == "2":
            try:
                change_password()
            except Exception as e:
                print(f"\nAn error occurred: {e}")
        elif choice == "3" or choice.lower() == "q":
            print("Exiting.")
            break
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
