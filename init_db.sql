-- SQL Script to initialize Sybase database for wos_audit

-- Create 'user' table
-- Note: 'user' is often a reserved word, so we use brackets if necessary,
-- but standard Sybase often allows it or requires quoting.
CREATE TABLE [user] (
    id INT IDENTITY PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    full_name VARCHAR(100)
)
GO

-- Create 'userrole' table
CREATE TABLE userrole (
    id INT IDENTITY PRIMARY KEY,
    user_id INT NOT NULL,
    role_name VARCHAR(50) NOT NULL,
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES [user](id)
)
GO

-- Insert sample users
INSERT INTO [user] (username, full_name) VALUES ('jdoe', 'John Doe')
INSERT INTO [user] (username, full_name) VALUES ('asmith', 'Alice Smith')
GO

-- Insert sample roles
-- Assuming IDs are 1 and 2 due to IDENTITY
INSERT INTO userrole (user_id, role_name) VALUES (1, 'ADMIN')
INSERT INTO userrole (user_id, role_name) VALUES (2, 'VIEWER')
GO

-- Example of creating a separate 'main' user for application queries
-- This typically requires 'sa' privileges and should be run by an admin.
-- sp_addlogin 'main_user', 'main_password'
-- GO
-- use your_database_name
-- GO
-- sp_adduser 'main_user'
-- GO
-- grant all on [user] to main_user
-- grant all on userrole to main_user
-- GO
