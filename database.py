import os
from supabase import create_client
from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

# Service client — full access (for backend operations)
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# Anon client — for auth operations
supabase_auth = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


def signup_user(email, password, name):
    try:
        response = supabase_auth.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {"name": name}
            }
        })
        if response.user:
            return {
                "user_id": str(response.user.id),
                "email": response.user.email,
                "name": name
            }
        return None
    except Exception as e:
        print(f"Signup error: {e}")
        return None


def login_user(email, password):
    try:
        response = supabase_auth.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        if response.user:
            name = response.user.user_metadata.get("name", "")
            return {
                "user_id": str(response.user.id),
                "email": response.user.email,
                "name": name
            }
        return None
    except Exception as e:
        print(f"Login error: {e}")
        return None


def save_session(session_id, user_id, question, context, board_type, votes, moderator_summary):
    try:
        supabase.table("sessions").insert({
            "session_id": session_id,
            "user_id": user_id,
            "question": question,
            "context": context,
            "board_type": board_type,
            "votes": votes,
            "moderator_summary": moderator_summary[:2000]
        }).execute()
    except Exception as e:
        print(f"Save session error: {e}")


def get_user_sessions(user_id):
    try:
        response = supabase.table("sessions").select("*").eq(
            "user_id", user_id
        ).order("created_at", desc=True).execute()
        return response.data
    except Exception as e:
        print(f"Get sessions error: {e}")
        return []


def get_session(session_id):
    try:
        response = supabase.table("sessions").select("*").eq(
            "session_id", session_id
        ).single().execute()
        return response.data
    except Exception as e:
        print(f"Get session error: {e}")
        return None
