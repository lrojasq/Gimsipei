-- Alter courses table to match the model
-- First, add missing columns
ALTER TABLE courses 
ADD COLUMN IF NOT EXISTS academic_year VARCHAR(9) NOT NULL DEFAULT '2024-2025' AFTER id,
ADD COLUMN IF NOT EXISTS period INT NOT NULL DEFAULT 1 AFTER academic_year,
ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE AFTER description,
ADD COLUMN IF NOT EXISTS created_by INT NOT NULL AFTER is_active;

-- Modify existing columns
ALTER TABLE courses 
MODIFY COLUMN grade_level VARCHAR(50) NOT NULL,
MODIFY COLUMN name VARCHAR(100) NOT NULL;

-- Drop the old period_id column if it exists
ALTER TABLE courses DROP COLUMN IF EXISTS period_id;

-- Add foreign key constraint for created_by
ALTER TABLE courses 
ADD CONSTRAINT fk_courses_created_by 
FOREIGN KEY (created_by) REFERENCES users(id);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_courses_academic_year ON courses(academic_year);
CREATE INDEX IF NOT EXISTS idx_courses_period ON courses(period);
CREATE INDEX IF NOT EXISTS idx_courses_grade_level ON courses(grade_level);
CREATE INDEX IF NOT EXISTS idx_courses_name ON courses(name);
CREATE INDEX IF NOT EXISTS idx_courses_created_by ON courses(created_by);
