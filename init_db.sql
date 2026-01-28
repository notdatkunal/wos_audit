-- SQL Script to initialize Sybase database for wos_audit

USE master
GO

-- CREATE DATABASE cannot be in a block in Sybase ASE
CREATE DATABASE auditdb
GO

USE auditdb
GO

SET QUOTED_IDENTIFIER ON
GO

-- Create 'user' table (quoted because 'user' is a reserved keyword)
CREATE TABLE "user" (
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
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES "user"(id)
)
GO

-- Create Sybase logins
-- These might fail if run multiple times, but are necessary for first-time setup
EXEC sp_addlogin 'jdoe', 'password123', 'auditdb'
GO
EXEC sp_addlogin 'asmith', 'password456', 'auditdb'
GO

-- Create users in the database
EXEC sp_adduser 'jdoe'
GO
EXEC sp_adduser 'asmith'
GO

-- Insert sample data
INSERT INTO "user" (username, full_name) VALUES ('jdoe', 'John Doe')
GO
INSERT INTO "user" (username, full_name) VALUES ('asmith', 'Alice Smith')
GO

-- Insert sample roles
INSERT INTO userrole (user_id, role_name) SELECT id, 'ADMIN' FROM "user" WHERE username = 'jdoe'
GO
INSERT INTO userrole (user_id, role_name) SELECT id, 'VIEWER' FROM "user" WHERE username = 'asmith'
GO

-- Grant permissions to the users
GRANT ALL ON "user" TO jdoe
GO
GRANT ALL ON "user" TO asmith
GO
GRANT ALL ON userrole TO jdoe
GO
GRANT ALL ON userrole TO asmith
GO
