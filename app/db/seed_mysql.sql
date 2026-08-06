-- Seed Data for Interior Design Business Platform
-- Populate initial roles, permissions, users, leads, lead sources, portfolio items, testimonials, and blogs.

-- 1. Insert Roles
INSERT INTO roles (id, name, description) VALUES
(1, 'Admin', 'Platform administrator with full control over users, settings, and CRM analytics'),
(2, 'Designer', 'Interior Designer who manages client projects, milestones, tasks, and documents'),
(3, 'Client', 'Homeowner or commercial client accessing their specific project portal')
ON DUPLICATE KEY UPDATE id=id;

-- Reset roles serial sequence (PostgreSQL specific)
-- 2. Insert Permissions
INSERT INTO permissions (id, name, description) VALUES
(1, 'manage_users', 'Ability to create, update, and deactivate users'),
(2, 'manage_leads', 'Access to leads pipeline and CRM status tracking'),
(3, 'manage_projects', 'Ability to create projects, milestones, tasks, and invoices'),
(4, 'client_portal_access', 'Access to own project details, chat, documents, and payments')
ON DUPLICATE KEY UPDATE id=id;

-- Link Role permissions
INSERT INTO role_permissions (role_id, permission_id) VALUES
(1, 1), (1, 2), (1, 3), (1, 4), -- Admin gets all
(2, 2), (2, 3), (2, 4),         -- Designer gets leads, projects, client interactions
(3, 4)                          -- Client only gets portal access
ON DUPLICATE KEY UPDATE id=id;

-- 3. Insert Users (password is hash of 'password123')
INSERT INTO users (id, email, password_hash, full_name, phone, role_id, is_active) VALUES
(1, 'admin@kelebekdesigner.com', '$2b$12$K.r0aRZEV3.Icw2P9W2qZOKCdAVBV4pLYi7mZ.Yiyx0KImupUKM.u', 'Kelebek Admin', '+91 98765 43210', 1, 1),
(2, 'sarah.designer@kelebekdesigners.com', '$2b$12$7kP.Lz39/4ZzV5X.fU.LHe.x7k26b1E83.0B7e930/1u/Q0K9Z2lW', 'Sarah Jenkins', '+91 98765 43211', 2, 1),
(3, 'robert.client@gmail.com', '$2b$12$7kP.Lz39/4ZzV5X.fU.LHe.x7k26b1E83.0B7e930/1u/Q0K9Z2lW', 'Robert Miller', '+91 98765 43212', 3, 1)
ON DUPLICATE KEY UPDATE id=id;

-- 4. Insert Lead Sources
INSERT INTO lead_sources (id, name) VALUES
(1, 'Website'),
(2, 'WhatsApp'),
(3, 'Google Ads'),
(4, 'Instagram'),
(5, 'Facebook'),
(6, 'Referral')
ON DUPLICATE KEY UPDATE id=id;

-- 5. Insert Leads (Starts empty for real client submissions)
-- Leads will populate automatically as clients submit consultation forms on the website.

-- 6. Insert Follow-ups
INSERT INTO followups (id, lead_id, followup_date, followup_type, notes, is_completed) VALUES
(1, 1, CURRENT_TIMESTAMP + INTERVAL '1 hour', 'Call', 'Call Ananya to introduce design concepts and schedule site visit.', 0),
(2, 3, CURRENT_TIMESTAMP - INTERVAL '1 day', 'Email', 'Send follow-up portfolio images of modular kitchens.', 0),
(3, 2, CURRENT_TIMESTAMP + INTERVAL '2 days', 'Meeting', 'Onsite office layout measurement and 3D review.', 0)
ON DUPLICATE KEY UPDATE id=id;

-- 7. Insert Portfolio Items
INSERT INTO portfolio_items (id, title, slug, category, description, before_image_url, after_image_url, budget_range, client_review) VALUES
(1, 'Kelebek Royal Villa Sanctuary', 'kelebek-royal-villa', 'Residential', 'A complete overhaul of a 5,000 sq ft luxury villa, focusing on warm wood paneling, brass details, and panoramic glass boundaries.', '/images/hero_interior_1784468037551.png', '/images/hero_interior_1784468037551.png', '₹25 Lakhs – ₹45 Lakhs', 'Kelebek Designers turned our house into an architectural masterpiece.'),
(2, 'Solas Corporate Office & Lounge', 'solas-corporate-office', 'Commercial', 'An open-concept commercial office layout built with soundproofing, custom work pods, and high-end executive lounges.', '/images/portfolio_commercial_1784468061607.png', '/images/portfolio_commercial_1784468061607.png', '₹35 Lakhs+', 'Our team productivity spiked, and clients are constantly wowed by our reception layout.'),
(3, 'Bespoke Italian Culinary Suite', 'italian-culinary-suite', 'Modular Kitchen', 'A premium culinary kitchen design featuring integrated appliances, dark oak cabinets, and a massive marble island.', '/images/portfolio_kitchen_1784468083139.png', '/images/portfolio_kitchen_1784468083139.png', '₹8 Lakhs – ₹15 Lakhs', 'Absolute perfection. Every drawer has a purpose and the design flows seamlessly.')
ON DUPLICATE KEY UPDATE id=id;

-- 8. Insert Testimonials
INSERT INTO testimonials (id, client_name, designation, content, rating, image_url, is_featured) VALUES
(1, 'Rajesh & Meera Kapoor', 'Villa Owners, Mumbai', 'Kelebek Designers completely redefined how we live. The lighting, choice of materials, and space flow are works of art.', 5, '/images/hero_interior_1784468037551.png', 1),
(2, 'Vikram Malhotra', 'CEO, InovaTech India', 'They delivered our corporate headquarters on time and within budget. The aesthetic matches our brand perfectly.', 5, '/images/portfolio_commercial_1784468061607.png', 1),
(3, 'Emily Watson', 'Penthouse Owner, Bengaluru', 'Attentions to detail is incomparable. From initial 3D renders to final styling, Kelebek was exceptional.', 5, '/images/portfolio_penthouse_1784468094816.png', 0)
ON DUPLICATE KEY UPDATE id=id;

-- 9. Insert Blogs
INSERT INTO blogs (id, title, slug, summary, content, category, tags, author_id, seo_title, seo_description, status) VALUES
(1, 'The Art of Minimalist Luxury: Designing Indian Homes', 'art-of-minimalist-luxury', 'How to leverage light, negative space, and premium organic materials to craft peaceful home environments.', '<h2>Understanding Quiet Luxury</h2><p>In modern interior design, luxury is expressed through the deliberate selection of raw, organic materials, textured surfaces, and functional layouts.</p>', 'Residential', 'Luxury, Minimalist, Guide', 2, 'Luxury Minimalist Interior Design | Kelebek Designers', 'Learn how to apply quiet luxury and natural lighting layouts to achieve a serene home environment.', 'Published'),
(2, 'Trends in Modern Commercial & Workspace Design', 'trends-modern-office-design', 'Discover how flexible layouts, acoustic partitions, and biophilic details can elevate office energy.', '<p>Corporate environments are changing. Today, offices must serve as hubs of creative collaboration...</p>', 'Commercial', 'Office, Productivity, Trends', 2, 'Modern Office Interior Design & Trends | Kelebek Designers', 'Explore office interior trends including biophilic workspaces, soundproofing, and modular spaces.', 'Published')
ON DUPLICATE KEY UPDATE id=id;

-- 10. Insert Settings
INSERT INTO settings (id, key, value) VALUES
(1, 'site_name', 'KELEBEK DESIGNERS'),
(2, 'contact_email', 'contact@kelebekdesigners.com'),
(3, 'contact_phone', '+91 98765 43210'),
(4, 'office_address', 'KELEBEK DESIGNERS STUDIO, Architectural & Interior Spaces Plaza, India')
ON DUPLICATE KEY UPDATE id=id;

