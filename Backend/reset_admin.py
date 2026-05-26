import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load env variables from Backend/.env
load_dotenv()

url = os.environ.get("SUPABASE_URL")
# IMPORTANT: Resetting an admin password requires the SERVICE_ROLE_KEY
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("Error: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not found in .env")
    exit(1)

supabase: Client = create_client(url, key)

def reset_admin_password(email, new_password):
    try:
        # 1. Find the user ID by email in the Profiles table
        profile_res = supabase.table("Profiles").select("id, email").eq("email", email).execute()
        if not profile_res.data:
            print(f"Error: User with email {email} not found in Profiles.")
            print("Listing all registered profiles to help you find the correct email:")
            all_profiles = supabase.table("Profiles").select("email").execute()
            for p in (all_profiles.data or []):
                print(f" - {p['email']}")
            return

        user_id = profile_res.data[0]["id"]

        # 2. Update the user password via Auth Admin API
        res = supabase.auth.admin.update_user_by_id(
            user_id, 
            {"password": new_password}
        )
        
        if res.user:
            print(f"🚀 Success! Password updated for {email} (User ID: {user_id})")
        else:
            print(f"Failed to update password: {res}")
            
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    # CONFIGURATION: Update these values
    ADMIN_EMAIL = "sharathdinesh23@gmail.com" # Check your actual admin email
    NEW_PASSWORD = "Sharath@23" # Set your desired password

    print(f"Attempting to reset password for {ADMIN_EMAIL}...")
    reset_admin_password(ADMIN_EMAIL, NEW_PASSWORD)
