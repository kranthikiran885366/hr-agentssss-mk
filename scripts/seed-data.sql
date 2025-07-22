-- Seed data for HR Agent System

-- Insert sample users
INSERT INTO users (id, name, email, role, department) VALUES
('550e8400-e29b-41d4-a716-446655440001', 'Admin User', 'admin@company.com', 'admin', 'HR'),
('550e8400-e29b-41d4-a716-446655440002', 'John Doe', 'john.doe@email.com', 'candidate', 'Engineering'),
('550e8400-e29b-41d4-a716-446655440003', 'Sarah Johnson', 'sarah.johnson@company.com', 'mentor', 'Engineering'),
('550e8400-e29b-41d4-a716-446655440004', 'Michael Chen', 'michael.chen@company.com', 'mentor', 'Product'),
('550e8400-e29b-41d4-a716-446655440005', 'Emily Rodriguez', 'emily.rodriguez@company.com', 'mentor', 'Design'),
('550e8400-e29b-41d4-a716-446655440006', 'Jane Smith', 'jane.smith@email.com', 'candidate', 'Marketing');

-- Insert candidates
INSERT INTO candidates (id, user_id, onboarding_status, onboarding_step, mentor_id) VALUES
('660e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440002', 'in-progress', 3, '550e8400-e29b-41d4-a716-446655440003'),
('660e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440006', 'pending', 1, NULL);

-- Insert mentors
INSERT INTO mentors (id, user_id, expertise, rating, availability, max_mentees) VALUES
('770e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440003', ARRAY['React', 'Node.js', 'Python', 'Team Leadership'], 4.9, 'available', 5),
('770e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440004', ARRAY['Product Strategy', 'Agile', 'Data Analysis'], 4.8, 'available', 3),
('770e8400-e29b-41d4-a716-446655440003', '550e8400-e29b-41d4-a716-446655440005', ARRAY['UI/UX Design', 'Figma', 'User Research'], 4.9, 'available', 4);

-- Insert sample documents
INSERT INTO documents (id, candidate_id, name, type, status, verification_confidence) VALUES
('880e8400-e29b-41d4-a716-446655440001', '660e8400-e29b-41d4-a716-446655440001', 'passport.pdf', 'government_id', 'verified', 95.5),
('880e8400-e29b-41d4-a716-446655440002', '660e8400-e29b-41d4-a716-446655440001', 'degree.pdf', 'education', 'verified', 92.3),
('880e8400-e29b-41d4-a716-446655440003', '660e8400-e29b-41d4-a716-446655440001', 'resume.pdf', 'resume', 'uploaded', NULL);

-- Insert onboarding steps
INSERT INTO onboarding_steps (candidate_id, step_number, step_name, status, completed_at) VALUES
('660e8400-e29b-41d4-a716-446655440001', 1, 'welcome', 'completed', CURRENT_TIMESTAMP - INTERVAL '2 days'),
('660e8400-e29b-41d4-a716-446655440001', 2, 'document_upload', 'completed', CURRENT_TIMESTAMP - INTERVAL '1 day'),
('660e8400-e29b-41d4-a716-446655440001', 3, 'verification', 'in-progress', NULL);

-- Insert system accounts
INSERT INTO system_accounts (candidate_id, service_name, username, email, status) VALUES
('660e8400-e29b-41d4-a716-446655440001', 'Google Workspace', 'john.doe', 'john.doe@company.com', 'created'),
('660e8400-e29b-41d4-a716-446655440001', 'HR System', 'jdoe001', 'john.doe@company.com', 'created'),
('660e8400-e29b-41d4-a716-446655440001', 'Development Tools', 'john.doe', 'john.doe@company.com', 'pending');
