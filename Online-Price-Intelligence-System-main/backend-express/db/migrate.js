/**
 * Migration Script: Update price_alerts to use user_id instead of user_email
 * 
 * IMPORTANT: Run this script BEFORE deploying the updated schema
 * Usage: node migrate.js
 */

const db = require('../config/db');
const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '../../.env') });

async function migrate() {
  console.log('Starting database migration...');

  try {
    // Step 1: Check if price_alerts has user_email column
    const checkColumn = await db.query(`
      SELECT column_name 
      FROM information_schema.columns 
      WHERE table_name = 'price_alerts' AND column_name = 'user_email'
    `);

    if (checkColumn.rows.length === 0) {
      console.log('✓ Migration already applied or table structure is correct');
      process.exit(0);
    }

    // Step 2: Add user_id column if it doesn't exist
    try {
      await db.query('ALTER TABLE price_alerts ADD COLUMN user_id INTEGER');
      console.log('✓ Added user_id column to price_alerts');
    } catch (err) {
      if (!err.message.includes('already exists')) {
        throw err;
      }
      console.log('✓ user_id column already exists');
    }

    // Step 3: Migrate data from user_email to user_id
    // This joins with the users table to get the correct user_id
    const migrateData = await db.query(`
      UPDATE price_alerts
      SET user_id = users.id
      FROM users
      WHERE price_alerts.user_email = users.email
      AND price_alerts.user_id IS NULL
    `);
    console.log(`✓ Migrated ${migrateData.rowCount} price alert records`);

    // Step 4: Add foreign key constraint
    try {
      await db.query(`
        ALTER TABLE price_alerts
        ADD CONSTRAINT fk_price_alerts_user_id
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
      `);
      console.log('✓ Added foreign key constraint');
    } catch (err) {
      if (!err.message.includes('already exists')) {
        throw err;
      }
      console.log('✓ Foreign key constraint already exists');
    }

    // Step 5: Make user_id NOT NULL
    try {
      await db.query('ALTER TABLE price_alerts ALTER COLUMN user_id SET NOT NULL');
      console.log('✓ Set user_id as NOT NULL');
    } catch (err) {
      console.log('✓ user_id column already NOT NULL or has other constraints');
    }

    // Step 6: Drop user_email column (optional - keep for safety on first run)
    console.log('\n✓ Migration completed successfully!');
    console.log('\nNote: The user_email column is still present for safety.');
    console.log('After verifying everything works, you can remove it with:');
    console.log('ALTER TABLE price_alerts DROP COLUMN user_email;');

  } catch (err) {
    console.error('✗ Migration failed:', err.message);
    process.exit(1);
  }

  process.exit(0);
}

migrate();
