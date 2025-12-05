-- Storage Bucket Policies for Profile Images
-- This allows authenticated users to upload, update, and view their own profile images

-- Policy 1: Allow authenticated users to upload their own profile images
-- The filename must start with their user_id
CREATE POLICY "Users can upload their own profile images"
ON storage.objects
FOR INSERT
TO authenticated
WITH CHECK (
  bucket_id = 'profile-images'
  AND (storage.foldername(name))[1] = auth.uid()::text
  OR name LIKE auth.uid()::text || '_%'
);

-- Policy 2: Allow authenticated users to update their own profile images
CREATE POLICY "Users can update their own profile images"
ON storage.objects
FOR UPDATE
TO authenticated
USING (
  bucket_id = 'profile-images'
  AND (storage.foldername(name))[1] = auth.uid()::text
  OR name LIKE auth.uid()::text || '_%'
);

-- Policy 3: Allow everyone to view profile images (since bucket is public)
CREATE POLICY "Anyone can view profile images"
ON storage.objects
FOR SELECT
TO public
USING (bucket_id = 'profile-images');

-- Policy 4: Allow users to delete their own profile images
CREATE POLICY "Users can delete their own profile images"
ON storage.objects
FOR DELETE
TO authenticated
USING (
  bucket_id = 'profile-images'
  AND (storage.foldername(name))[1] = auth.uid()::text
  OR name LIKE auth.uid()::text || '_%'
);
