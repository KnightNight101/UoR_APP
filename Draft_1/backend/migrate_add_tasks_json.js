// Migration script to add tasks_json column to projects table (idempotent, PostgreSQL)
const { Pool } = require('pg');

const pool = new Pool({
  connectionString: process.env.DATABASE_URL || 'postgres://postgres:postgres@localhost:5432/uor_app'
});

async function migrate() {
  try {
    // Check if the column already exists
    const checkRes = await pool.query(`
      SELECT column_name
      FROM information_schema.columns
      WHERE table_name='projects' AND column_name='tasks_json'
    `);

    if (checkRes.rows.length === 0) {
      await pool.query('ALTER TABLE projects ADD COLUMN tasks_json TEXT');
      console.log('tasks_json column added.');
    } else {
      console.log('tasks_json column already exists.');
    }
  } catch (err) {
    console.error('Migration failed:', err);
    process.exit(1);
  } finally {
    await pool.end();
  }
}

migrate();