-- 1. Enable Required Extensions 
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. Create Roles Master Table
CREATE TABLE public."Roles" (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    role_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT
);

-- Seed Default Roles Context Natively
INSERT INTO public."Roles" (role_name, description) VALUES 
('student', 'Internship Participant Paradigm'), 
('teacher', 'Instructor Matrix'), 
('admin', 'System Administrator Root');

-- 3. Create Internships Table
CREATE TABLE public."Internships" (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 4. Create Profiles Table (Linked natively to Roles and Internships explicit keys)
CREATE TABLE public."Profiles" (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    role_id UUID REFERENCES public."Roles"(id) ON DELETE RESTRICT NOT NULL,
    internship_id UUID REFERENCES public."Internships"(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 5. Create Assignments Table
CREATE TABLE public."Assignments" (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    internship_id UUID REFERENCES public."Internships"(id) ON DELETE CASCADE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    doc_link VARCHAR(512),
    due_date TIMESTAMP WITH TIME ZONE NOT NULL,
    created_by UUID REFERENCES public."Profiles"(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 6. Create Submissions Repository Table
CREATE TABLE public."Submissions" (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assignment_id UUID REFERENCES public."Assignments"(id) ON DELETE CASCADE NOT NULL,
    student_id UUID REFERENCES public."Profiles"(id) ON DELETE CASCADE NOT NULL,
    repo_link VARCHAR(512) NOT NULL,
    status VARCHAR(50) DEFAULT 'Pending' CHECK (status IN ('Pending', 'Graded', 'Late')),
    grade VARCHAR(50),
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    UNIQUE(assignment_id, student_id)
);

-- 7. Create Attendance Core Table
CREATE TABLE public."Attendance" (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID REFERENCES public."Profiles"(id) ON DELETE CASCADE NOT NULL,
    date DATE NOT NULL,
    status VARCHAR(50) NOT NULL CHECK (status IN ('Present', 'Absent', 'Late')),
    recorded_by UUID REFERENCES public."Profiles"(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    UNIQUE(student_id, date)
);

-- 8. Create Notes Table
CREATE TABLE public."Notes" (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    internship_id UUID REFERENCES public."Internships"(id) ON DELETE CASCADE NOT NULL,
    title VARCHAR(255) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    markdown_content TEXT NOT NULL,
    created_by UUID REFERENCES public."Profiles"(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 9. Explicitly Disable RLS for isolated backend processing routing mechanisms 
ALTER TABLE public."Roles" DISABLE ROW LEVEL SECURITY;
ALTER TABLE public."Internships" DISABLE ROW LEVEL SECURITY;
ALTER TABLE public."Profiles" DISABLE ROW LEVEL SECURITY;
ALTER TABLE public."Assignments" DISABLE ROW LEVEL SECURITY;
ALTER TABLE public."Submissions" DISABLE ROW LEVEL SECURITY;
ALTER TABLE public."Attendance" DISABLE ROW LEVEL SECURITY;
ALTER TABLE public."Notes" DISABLE ROW LEVEL SECURITY;
