-- Migration: Add tasks_json column to projects table if it does not exist
ALTER TABLE projects ADD COLUMN IF NOT EXISTS tasks_json TEXT;