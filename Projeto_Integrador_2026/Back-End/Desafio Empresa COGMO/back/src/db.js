const fs = require('node:fs');
const path = require('node:path');
const Database = require('better-sqlite3');
require('dotenv').config();

const filePath = process.env.DB_PATH
  ? path.resolve(process.env.DB_PATH)
  : path.join(__dirname, '..', 'data', 'monitoramento.sqlite');

fs.mkdirSync(path.dirname(filePath), { recursive: true });

const db = new Database(filePath);
db.pragma('foreign_keys = ON');
db.exec(fs.readFileSync(path.join(__dirname, '..', 'db', 'schema.sql'), 'utf8'));

module.exports = { db, filePath };
