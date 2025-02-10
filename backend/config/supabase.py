from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_ANON_KEY or not SUPABASE_SERVICE_KEY:
    raise ValueError("SUPABASE_URL, SUPABASE_ANON_KEY and SUPABASE_SERVICE_KEY must be set in .env file")

# Create two clients - one with anon key for auth, one with service key for admin operations
supabase_auth = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
supabase_admin = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def get_supabase(auth=True):
    """Get Supabase client. Use auth=True for user operations, auth=False for admin operations."""
    return supabase_auth if auth else supabase_admin
