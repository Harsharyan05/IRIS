-- ================================================================
-- IRIS Database Setup - Complete SQL Script for Supabase
-- Run this entire script in Supabase SQL Editor
-- ================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ================================================================
-- TABLE CREATION
-- ================================================================

-- profiles table (extends auth.users)
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT,
    name TEXT,
    remember_me BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- documents table
CREATE TABLE IF NOT EXISTS public.documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    filename TEXT NOT NULL,
    storage_path TEXT NOT NULL,
    sha256 TEXT NOT NULL,
    status TEXT DEFAULT 'uploaded' CHECK (status IN ('uploaded', 'processing', 'done', 'failed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- extracted_texts table
CREATE TABLE IF NOT EXISTS public.extracted_texts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES public.documents(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    page_number INTEGER NOT NULL,
    text TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- analyses table
CREATE TABLE IF NOT EXISTS public.analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES public.documents(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    risk JSONB,
    compliance JSONB,
    crossverify JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- heatmaps table
CREATE TABLE IF NOT EXISTS public.heatmaps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES public.analyses(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    heatmap_path TEXT NOT NULL,
    caption TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- dossiers table
CREATE TABLE IF NOT EXISTS public.dossiers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES public.documents(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    dossier_url TEXT NOT NULL,
    sha256 TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- blockchain_certificates table
CREATE TABLE IF NOT EXISTS public.blockchain_certificates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dossier_id UUID REFERENCES public.dossiers(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    dossier_hash TEXT NOT NULL,
    tx_hash TEXT NOT NULL,
    explorer_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- audit_logs table
CREATE TABLE IF NOT EXISTS public.audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    action TEXT NOT NULL,
    target_table TEXT,
    target_id UUID,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ================================================================
-- INDEXES FOR PERFORMANCE
-- ================================================================

CREATE INDEX IF NOT EXISTS idx_documents_user_id ON public.documents(user_id);
CREATE INDEX IF NOT EXISTS idx_documents_status ON public.documents(status);
CREATE INDEX IF NOT EXISTS idx_extracted_texts_document_id ON public.extracted_texts(document_id);
CREATE INDEX IF NOT EXISTS idx_analyses_document_id ON public.analyses(document_id);
CREATE INDEX IF NOT EXISTS idx_analyses_user_id ON public.analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_heatmaps_analysis_id ON public.heatmaps(analysis_id);
CREATE INDEX IF NOT EXISTS idx_dossiers_document_id ON public.dossiers(document_id);
CREATE INDEX IF NOT EXISTS idx_blockchain_certs_dossier_id ON public.blockchain_certificates(dossier_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON public.audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON public.audit_logs(created_at DESC);

-- ================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ================================================================

-- Enable RLS on all tables
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.extracted_texts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.heatmaps ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.dossiers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.blockchain_certificates ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist (for clean re-run)
DROP POLICY IF EXISTS "profiles_self_access" ON public.profiles;
DROP POLICY IF EXISTS "documents_user_select" ON public.documents;
DROP POLICY IF EXISTS "documents_user_insert" ON public.documents;
DROP POLICY IF EXISTS "documents_user_update" ON public.documents;
DROP POLICY IF EXISTS "documents_user_delete" ON public.documents;
DROP POLICY IF EXISTS "extracted_texts_user_select" ON public.extracted_texts;
DROP POLICY IF EXISTS "extracted_texts_user_insert" ON public.extracted_texts;
DROP POLICY IF EXISTS "analyses_user_select" ON public.analyses;
DROP POLICY IF EXISTS "analyses_user_insert" ON public.analyses;
DROP POLICY IF EXISTS "heatmaps_user_select" ON public.heatmaps;
DROP POLICY IF EXISTS "heatmaps_user_insert" ON public.heatmaps;
DROP POLICY IF EXISTS "dossiers_user_select" ON public.dossiers;
DROP POLICY IF EXISTS "dossiers_user_insert" ON public.dossiers;
DROP POLICY IF EXISTS "blockchain_certs_user_select" ON public.blockchain_certificates;
DROP POLICY IF EXISTS "blockchain_certs_user_insert" ON public.blockchain_certificates;
DROP POLICY IF EXISTS "audit_logs_backend_only" ON public.audit_logs;

-- Profiles: Users can manage their own profile
CREATE POLICY "profiles_self_access" 
ON public.profiles 
FOR ALL 
USING (auth.uid() = id)
WITH CHECK (auth.uid() = id);

-- Documents: Users can only access their own documents
CREATE POLICY "documents_user_select" 
ON public.documents 
FOR SELECT 
USING (auth.uid() = user_id);

CREATE POLICY "documents_user_insert" 
ON public.documents 
FOR INSERT 
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "documents_user_update" 
ON public.documents 
FOR UPDATE 
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "documents_user_delete" 
ON public.documents 
FOR DELETE 
USING (auth.uid() = user_id);

-- Extracted Texts: Users can only access their own
CREATE POLICY "extracted_texts_user_select" 
ON public.extracted_texts 
FOR SELECT 
USING (auth.uid() = user_id);

CREATE POLICY "extracted_texts_user_insert" 
ON public.extracted_texts 
FOR INSERT 
WITH CHECK (auth.uid() = user_id);

-- Analyses: Users can only access their own
CREATE POLICY "analyses_user_select" 
ON public.analyses 
FOR SELECT 
USING (auth.uid() = user_id);

CREATE POLICY "analyses_user_insert" 
ON public.analyses 
FOR INSERT 
WITH CHECK (auth.uid() = user_id);

-- Heatmaps: Users can only access their own
CREATE POLICY "heatmaps_user_select" 
ON public.heatmaps 
FOR SELECT 
USING (auth.uid() = user_id);

CREATE POLICY "heatmaps_user_insert" 
ON public.heatmaps 
FOR INSERT 
WITH CHECK (auth.uid() = user_id);

-- Dossiers: Users can only access their own
CREATE POLICY "dossiers_user_select" 
ON public.dossiers 
FOR SELECT 
USING (auth.uid() = user_id);

CREATE POLICY "dossiers_user_insert" 
ON public.dossiers 
FOR INSERT 
WITH CHECK (auth.uid() = user_id);

-- Blockchain Certificates: Users can read their own, anyone can verify by tx_hash
CREATE POLICY "blockchain_certs_user_select" 
ON public.blockchain_certificates 
FOR SELECT 
USING (auth.uid() = user_id OR auth.role() = 'anon');

CREATE POLICY "blockchain_certs_user_insert" 
ON public.blockchain_certificates 
FOR INSERT 
WITH CHECK (auth.uid() = user_id);

-- Audit Logs: Backend only (service_role)
CREATE POLICY "audit_logs_backend_only" 
ON public.audit_logs 
FOR ALL 
USING (auth.role() = 'service_role');

-- ================================================================
-- STORAGE BUCKET POLICIES
-- ================================================================

-- Note: Storage bucket policies must be set via Supabase Dashboard
-- Create these buckets in Dashboard -> Storage:
-- 1. documents (private)
-- 2. heatmaps (private)
-- 3. dossiers (private)

-- After creating buckets, apply these policies in Storage settings:

-- DOCUMENTS BUCKET POLICY:
-- Allow authenticated users to upload to their own folder
-- Allow authenticated users to read from their own folder
-- SQL equivalent (run in Storage policies):
/*
CREATE POLICY "Users can upload own documents"
ON storage.objects FOR INSERT
WITH CHECK (
    bucket_id = 'documents' 
    AND auth.uid()::text = (storage.foldername(name))[1]
);

CREATE POLICY "Users can read own documents"
ON storage.objects FOR SELECT
USING (
    bucket_id = 'documents' 
    AND auth.uid()::text = (storage.foldername(name))[1]
);

CREATE POLICY "Users can delete own documents"
ON storage.objects FOR DELETE
USING (
    bucket_id = 'documents' 
    AND auth.uid()::text = (storage.foldername(name))[1]
);
*/

-- Repeat similar policies for 'heatmaps' and 'dossiers' buckets

-- ================================================================
-- FUNCTIONS (Optional - for convenience)
-- ================================================================

-- Function to automatically create profile on signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, remember_me)
    VALUES (NEW.id, NEW.email, false)
    ON CONFLICT (id) DO NOTHING;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to create profile on user signup
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();

-- ================================================================
-- VERIFICATION QUERIES
-- ================================================================

-- Run these to verify setup:
/*
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN (
    'profiles', 'documents', 'extracted_texts', 'analyses', 
    'heatmaps', 'dossiers', 'blockchain_certificates', 'audit_logs'
);

SELECT tablename, policyname 
FROM pg_policies 
WHERE schemaname = 'public';
*/

-- ================================================================
-- SETUP COMPLETE
-- ================================================================

-- After running this script:
-- 1. Create storage buckets: documents, heatmaps, dossiers (private)
-- 2. Configure storage policies in Supabase Dashboard
-- 3. Enable Google OAuth in Authentication -> Providers
-- 4. Add your site URL in Authentication -> URL Configuration
-- 5. Copy your API keys to .env file

SELECT 'IRIS Database Setup Complete! ✓' as status;