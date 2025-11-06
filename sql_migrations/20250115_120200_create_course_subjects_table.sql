-- Create course_subjects table
CREATE TABLE IF NOT EXISTS course_subjects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    subject_id INT NOT NULL,
    teacher_id INT NOT NULL,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (course_id) REFERENCES courses(id),
    FOREIGN KEY (subject_id) REFERENCES subjects(id),
    FOREIGN KEY (teacher_id) REFERENCES users(id),
    UNIQUE KEY unique_course_subject_teacher (course_id, subject_id, teacher_id)
) ENGINE=InnoDB;

-- Create indexes
CREATE INDEX idx_course_subjects_course_id ON course_subjects(course_id);
CREATE INDEX idx_course_subjects_subject_id ON course_subjects(subject_id);
CREATE INDEX idx_course_subjects_teacher_id ON course_subjects(teacher_id);
CREATE INDEX idx_course_subjects_is_active ON course_subjects(is_active);
