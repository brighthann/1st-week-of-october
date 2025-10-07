--Initialize monitoring database
CREATE DATABASE IF NOT EXISTS monitoring;

--tables for status history
CREATE TABLE IF NOT EXISTS endpoint_status (
    id SERIAL PRIMARY KEY,
    endpoint_name VARCHAR(255) NOT NULL,
    url TEXT NOT NULL,
    status VARCHAR(50) NOT NULL,
    status_code INTEGER,
    response_time FLOAT,
    ssl_valid BOOLEAN,
    ssl_expires TIMESTAMP,
    error_message TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    uptime_percentage FLOAT
);

--index for faster queries
CREATE INDEX IF NOT EXISTS idx_endpoint_timestamp ON endpoint_status(endpoint_name, timestamp);
CREATE INDEX IF NOT EXISTS idx_timestamp ON endpoint_status(timestamp);

--create alert table
CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    endpoint_name VARCHAR(255) NOT NULL,
    alert_type VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    severity VARCHAR(20) DEFAULT 'medium',
    resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);

--create index for alerts
CREATE INDEX IF NOT EXISTS idx_alerts_endpoint ON alerts(endpoint_name, created_at);
