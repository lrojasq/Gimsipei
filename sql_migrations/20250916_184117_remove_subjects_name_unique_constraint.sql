-- Remove unique constraint from subjects.name column
-- This allows multiple subjects with the same name for different teachers

-- Drop the unique index on subjects.name
DROP INDEX IF EXISTS ix_subjects_name ON subjects;

-- Add a regular index on subjects.name (non-unique)
CREATE INDEX idx_subjects_name ON subjects(name);

-- Note: The unique constraint is now removed, allowing multiple subjects 
-- with the same name as long as they have different teacher_id values.
-- The uniqueness is now enforced at the course-subject-teacher level in 
-- the course_subjects table via the unique_course_subject_teacher constraint.
