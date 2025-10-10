
//DashMonitor - API Health Monitoring Dashboard//

A production-ready API health monitoring system built with FastAPI, Streamlit, and Docker. It monitors multiple API endpoints in real-time with automated alerting, comprehensive metrics, and beautiful visualizations.
This project is containerized Python system that monitors multiple API endpoints and displays their real-time health status through a web dashboard. The project is bound to be updated over time. The core concept of this project may likely be implemented in other projects.

//Project Overview//
*More time spent understanding how the system should function, and its components, and how to properly use the resources required to create it
*Difficulty Level: Beginner-to-Intermediate DevOps Project
*Core Concept: Build a production-ready API monitoring system with automated alerting and real-time visualization.

/ Current Status: Day 1 Complete 
/ Completed Features(spending more time understanding how you want the system to functio, than writing code itself makes the task less complex)

//Features//

--  FastAPI backend with async monitoring
--  Health check endpoints for multiple APIs
--  Prometheus metrics integration
--  Automated alerting system with Slack integration
--  SSL certificate monitoring
--  Background monitoring tasks
--  Comprehensive error handling and logging
--  Unit tests with pytest

/Interactive Dashboard/
-- Modern, responsive Streamlit interface
-- Interactive Plotly charts
-- Color-coded status indicators
-- Auto-refresh capability
-- Data History visualization
-- Prometheus metrics endpoint (metrics)

/Alerting and Monitoring/
-- Downtime detection
-- Slow response time alerts
-- SSL expiry warnings
-- Slack integration
-- Prometheus metrics integration
-- Time-series data storage
-- Advanced querying with PromQL
-- Performance analytics

/production/
-- Dockerized
-- CI/CD with GitHub Actions
-- PostgreSQL database integration
-- Security scanning
-- Automated testing



/ Technology Stack /

-- Backend Framework: FastAPI, SQLAlchemy, Prometheus Client, Aiohttp
-- Frontend Framework: Streamlit, Plotly, Pandas
-- Infrastructure: Docker, Prometheus, PostgreSQL, Nginx
-- Testing: pytest, pytest-asyncio
-- CI/CD Pipeline: GitHub Actions
-- Code Quality: black, flake8, bandit
-- Deployment: Docker + Docker Compose

//Clone Repo//
git clone https://github.com/brighthann/1st-week-of-october.git
cd 1st-week-of-october

[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![CI/CD Pipeline](https://github.com/brighthann/api-health-dashboard/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/brighthann/api-health-dashboard/actions/workflows/ci-cd.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
