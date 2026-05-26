-- Migration: add optional college_name for student profiles
-- Date: 2026-05-24
-- Safe to run multiple times.

BEGIN;

ALTER TABLE public."Profiles"
ADD COLUMN IF NOT EXISTS college_name VARCHAR(255);

COMMENT ON COLUMN public."Profiles".college_name IS
'Optional college/school name for student records; used by admin student creation and bulk import.';

-- Helps admin filters and reporting by college when data grows.
CREATE INDEX IF NOT EXISTS idx_profiles_college_name
ON public."Profiles"(college_name);

COMMIT;

