
//DashMonitor - API Health Monitoring Dashboard

This project is containerized Python system that monitors multiple API endpoints and displays their real-time health status through a web dashboard. The project is bound to be updated over time. The core concept of this project may likely be implemented in other projects.

/Project Overview
*Timeline: 1 Week (7 days. More time spent understanding how the system should function, and its components)
*Difficulty Level: Beginner-to-Intermediate DevOps Project
*Core Concept: Build a production-ready API monitoring system with automated alerting and real-time visualization.

/ Current Status: Day 1 Complete
/ Completed Features(spending more time understanding how you want the system to functio, than writing code itself makes the task less complex)

--  FastAPI backend with async monitoring
--  Health check endpoints for multiple APIs
--  Prometheus metrics integration
--  Automated alerting system with Slack integration
--  SSL certificate monitoring
--  Background monitoring tasks
--  Comprehensive error handling and logging
--  Unit tests with pytest

/ Day 1
-- FastAPI server running locally on port 8000
-- Basic health check endpoint (health)
-- API monitoring service that checks 3 test endpoints
-- Passing unit tests (>80% coverage)
-- Prometheus metrics endpoint (metrics)

/ Technology Stack

-- Backend Framework: FastAPI (Python)
-- Monitoring: Prometheus client metrics
-- Testing: pytest, pytest-asyncio
-- Code Quality: black, flake8, bandit
-- Deployment: Docker + Docker Compose

//  Project Structure

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
