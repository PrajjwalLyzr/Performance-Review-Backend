from supabase import create_client, Client


def supabase_client(SUPABASE_URL, SUPABASE_KEY):
    supabase_db: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return supabase_db
