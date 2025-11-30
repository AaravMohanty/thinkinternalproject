-- Setup Storage Bucket and Policies for Resumes
-- Run this in Supabase SQL Editor

-- Create the resumes bucket if it doesn't exist
INSERT INTO storage.buckets (id, name, public)
VALUES ('resumes', 'resumes', false)
ON CONFLICT (id) DO NOTHING;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Allow authenticated uploads to resumes" ON storage.objects;
DROP POLICY IF EXISTS "Allow authenticated reads from resumes" ON storage.objects;
DROP POLICY IF EXISTS "Allow authenticated updates to resumes" ON storage.objects;
DROP POLICY IF EXISTS "Allow authenticated deletes from resumes" ON storage.objects;

-- Policy: Allow authenticated users to upload resumes
CREATE POLICY "Allow authenticated uploads to resumes"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (bucket_id = 'resumes');

-- Policy: Allow authenticated users to read resumes
CREATE POLICY "Allow authenticated reads from resumes"
ON storage.objects FOR SELECT
TO authenticated
USING (bucket_id = 'resumes');

-- Policy: Allow authenticated users to update resumes
CREATE POLICY "Allow authenticated updates to resumes"
ON storage.objects FOR UPDATE
TO authenticated
USING (bucket_id = 'resumes');

-- Policy: Allow authenticated users to delete resumes
CREATE POLICY "Allow authenticated deletes from resumes"
ON storage.objects FOR DELETE
TO authenticated
USING (bucket_id = 'resumes');
