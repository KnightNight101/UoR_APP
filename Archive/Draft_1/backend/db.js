/**
 * PostgreSQL connection setup for UoR_APP backend.
 * Edit the connection string as needed for your environment.
 */

const { Pool } = require('pg');

const pool = new Pool({
  connectionString: process.env.DATABASE_URL || 'postgres://postgres:postgres@localhost:5432/uor_app'
});

module.exports = {
  query: (text, params) => pool.query(text, params),
  pool
};