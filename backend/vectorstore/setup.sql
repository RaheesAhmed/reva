-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Chat History Table
CREATE TABLE IF NOT EXISTS chat_history (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID NOT NULL,
    message TEXT NOT NULL,
    response TEXT NOT NULL,
    tool_used TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Saved Items Table
CREATE TABLE IF NOT EXISTS saved_items (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID NOT NULL,
    item_type TEXT NOT NULL,
    title TEXT NOT NULL,
    content JSONB NOT NULL,
    tags TEXT[] DEFAULT ARRAY[]::TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Property Views Table
CREATE TABLE IF NOT EXISTS property_views (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID NOT NULL,
    property_id TEXT NOT NULL,
    views_count INTEGER DEFAULT 1,
    last_viewed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, property_id)
);

-- Economic Indicators Table
CREATE TABLE IF NOT EXISTS economic_indicators (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    indicator_name TEXT NOT NULL,
    value NUMERIC NOT NULL,
    unit TEXT,
    region TEXT,
    date DATE NOT NULL,
    source TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- System Messages Table
CREATE TABLE IF NOT EXISTS system_messages (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    message TEXT NOT NULL,
    is_active BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indices for better performance
CREATE INDEX IF NOT EXISTS idx_chat_history_user_created 
ON chat_history(user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_saved_items_user 
ON saved_items(user_id);

CREATE INDEX IF NOT EXISTS idx_property_views_user_count 
ON property_views(user_id, views_count DESC);

CREATE INDEX IF NOT EXISTS idx_economic_indicators_date 
ON economic_indicators(date DESC);

CREATE INDEX IF NOT EXISTS idx_system_messages_active 
ON system_messages(is_active) WHERE is_active = true;

-- Function for tool usage statistics
CREATE OR REPLACE FUNCTION get_tool_usage_stats(user_id UUID)
RETURNS jsonb
LANGUAGE plpgsql AS $$
BEGIN
    RETURN (
        SELECT jsonb_object_agg(tool_used, count)
        FROM (
            SELECT tool_used, COUNT(*) as count
            FROM chat_history
            WHERE user_id = $1
            AND created_at >= NOW() - INTERVAL '7 days'
            GROUP BY tool_used
        ) t
    );
END;
$$;

-- Function to update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create update triggers
DROP TRIGGER IF EXISTS update_chat_history_updated_at ON chat_history;
CREATE TRIGGER update_chat_history_updated_at
    BEFORE UPDATE ON chat_history
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_saved_items_updated_at ON saved_items;
CREATE TRIGGER update_saved_items_updated_at
    BEFORE UPDATE ON saved_items
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_property_views_updated_at ON property_views;
CREATE TRIGGER update_property_views_updated_at
    BEFORE UPDATE ON property_views
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_economic_indicators_updated_at ON economic_indicators;
CREATE TRIGGER update_economic_indicators_updated_at
    BEFORE UPDATE ON economic_indicators
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_system_messages_updated_at ON system_messages;
CREATE TRIGGER update_system_messages_updated_at
    BEFORE UPDATE ON system_messages
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security
ALTER TABLE chat_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE saved_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE property_views ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_messages ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can view their own chat history" ON chat_history;
DROP POLICY IF EXISTS "Users can insert their own chat history" ON chat_history;
DROP POLICY IF EXISTS "Users can view their own saved items" ON saved_items;
DROP POLICY IF EXISTS "Users can insert their own saved items" ON saved_items;
DROP POLICY IF EXISTS "Users can update their own saved items" ON saved_items;
DROP POLICY IF EXISTS "Users can delete their own saved items" ON saved_items;
DROP POLICY IF EXISTS "Users can view their own property views" ON property_views;
DROP POLICY IF EXISTS "Users can insert their own property views" ON property_views;
DROP POLICY IF EXISTS "Users can update their own property views" ON property_views;
DROP POLICY IF EXISTS "Admins can manage system messages" ON system_messages;

-- Create RLS policies for chat_history
CREATE POLICY "Users can view their own chat history"
    ON chat_history FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own chat history"
    ON chat_history FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Create RLS policies for saved_items
CREATE POLICY "Users can view their own saved items"
    ON saved_items FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own saved items"
    ON saved_items FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own saved items"
    ON saved_items FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own saved items"
    ON saved_items FOR DELETE
    USING (auth.uid() = user_id);

-- Create RLS policies for property_views
CREATE POLICY "Users can view their own property views"
    ON property_views FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own property views"
    ON property_views FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own property views"
    ON property_views FOR UPDATE
    USING (auth.uid() = user_id);

-- Create RLS policies for system_messages
CREATE POLICY "Admins can manage system messages"
    ON system_messages
    USING (auth.role() = 'admin');

-- Function to get active system message
CREATE OR REPLACE FUNCTION get_active_system_message()
RETURNS TEXT
LANGUAGE plpgsql
AS $$
DECLARE
    active_message TEXT;
BEGIN
    SELECT message INTO active_message
    FROM system_messages
    WHERE is_active = true
    ORDER BY updated_at DESC
    LIMIT 1;
    
    RETURN COALESCE(active_message, 'You are a helpful AI assistant for commercial real estate.');
END;
$$;

-- Function to get all users
CREATE OR REPLACE FUNCTION get_users()
RETURNS TABLE (
    id uuid,
    email varchar(255),
    role varchar(255),
    last_sign_in_at timestamptz,
    created_at timestamptz,
    updated_at timestamptz,
    confirmed_at timestamptz
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        au.id,
        au.email,
        COALESCE(au.role::varchar(255), 'user'),
        au.last_sign_in_at,
        au.created_at,
        au.updated_at,
        au.confirmed_at
    FROM auth.users au
    ORDER BY au.created_at DESC;
END;
$$;

-- Grant execute permission to authenticated users
GRANT EXECUTE ON FUNCTION get_users() TO authenticated;

-- Create admin user if not exists
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM auth.users WHERE email = 'admin@cre.com') THEN
        INSERT INTO auth.users (
            instance_id,
            id,
            aud,
            role,
            email,
            encrypted_password,
            email_confirmed_at,
            recovery_sent_at,
            last_sign_in_at,
            raw_app_meta_data,
            raw_user_meta_data,
            created_at,
            updated_at,
            confirmation_token,
            email_change,
            email_change_token_new,
            recovery_token
        ) VALUES (
            '00000000-0000-0000-0000-000000000000',
            uuid_generate_v4(),
            'authenticated',
            'admin',
            'admin@cre.com',
            crypt('Admin@Cre', gen_salt('bf')),
            NOW(),
            NOW(),
            NOW(),
            '{"provider":"email","providers":["email"],"role":"admin"}',
            '{}',
            NOW(),
            NOW(),
            '',
            '',
            '',
            ''
        );
    END IF;
END
$$;

-- Ensure the user has admin privileges (this will update even if user exists)
UPDATE auth.users 
SET role = 'admin', 
    raw_app_meta_data = raw_app_meta_data || 
        '{"role": "admin"}'::jsonb,
    email_confirmed_at = NOW()
WHERE email = 'admin@cre.com';

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT USAGE ON SCHEMA public TO anon;
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO authenticated;

-- Grant execute permission to authenticated users
GRANT EXECUTE ON FUNCTION get_users() TO authenticated; 