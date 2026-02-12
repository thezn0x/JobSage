# JobSage

**Career Intelligence Platform for Pakistan's Tech Job Market**

JobSage is a comprehensive data platform that aggregates, analyzes, and provides insights into Pakistan's technology job market. The system collects job postings from multiple sources, extracts key information about skills, salaries, and trends, and delivers actionable intelligence through a REST API.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Database Schema](#database-schema)
- [Development](#development)
- [Deployment](#deployment)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

JobSage addresses the lack of transparency and data-driven insights in Pakistan's tech job market. The platform automatically collects job postings from major Pakistani job boards, normalizes the data, and provides analytics that help developers make informed career decisions.

### Problem Statement

- No centralized data on in-demand technical skills
- Salary information is fragmented and opaque
- No way to track market trends or skill demand over time
- Job seekers cannot make data-driven career decisions
- Students lack guidance on what skills to learn

### Solution

JobSage transforms scattered job posting data into structured, actionable insights through:

- Automated data collection from multiple job boards
- Intelligent extraction of skills, salaries, and requirements
- Deduplication and normalization of job postings
- REST API for accessing cleaned and structured data
- Analytics capabilities for market trend analysis

---

## Key Features

### Data Collection
- Automated web scraping from Rozee.pk and Careerjet.pk
- Configurable extraction parameters (pages, selectors, URLs)
- Scheduled daily data collection
- Error handling and retry mechanisms

### Data Processing
- Intelligent skill extraction from job descriptions
- Salary parsing and normalization
- Date standardization (relative to absolute dates)
- Soft skill filtering from technical skills
- Company and location normalization

### Data Storage
- Normalized PostgreSQL database schema
- Efficient indexing for analytical queries
- Many-to-many relationship handling via junction tables
- Support for skill categorization and geographic data

### Analytics API
- RESTful endpoints for market insights
- Skill demand analysis
- Geographic job distribution
- Company hiring patterns
- Skill combination recommendations
- Salary range queries (future enhancement)

### Automation
- Scheduler for daily ETL pipeline execution
- Configurable run times and intervals
- Comprehensive logging system
- Automatic error recovery

---

## System Architecture

JobSage follows an Extract-Transform-Load (ETL) architecture pattern:

```
Job Boards (Rozee, Careerjet)
        |
        v
   [Extractors] - Web scraping with Playwright
        |
        v
   [Transformers] - Data cleaning and normalization
        |
        v
   [Loaders] - Database insertion
        |
        v
   PostgreSQL Database
        |
        v
   [Analytics Engine] - Query and aggregate data
        |
        v
   REST API (FastAPI)
        |
        v
   External Clients
```

### Components

**Extractors**: Platform-specific scrapers that fetch raw job data using Playwright for browser automation.

**Transformers**: Data cleaning modules that parse dates, extract skills, normalize salaries, and remove duplicates.

**Loaders**: Database insertion logic that handles relationship mapping and foreign key constraints.

**Analytics Engine**: Query layer that aggregates data for market insights.

**REST API**: FastAPI-based service exposing analytical endpoints.

**Scheduler**: APScheduler-based automation for daily pipeline execution.

---

## Technology Stack

### Core Technologies
- **Python 3.11+** - Primary programming language
- **PostgreSQL 15** - Relational database
- **FastAPI** - High-performance REST API framework
- **Playwright** - Browser automation for web scraping
- **APScheduler** - Job scheduling and automation

### Key Libraries
- **znpg** - Custom PostgreSQL wrapper for database operations
- **python-dotenv** - Environment variable management
- **uvicorn** - ASGI server for FastAPI

### Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration

---

## Installation

### Prerequisites

- Python 3.11 or higher
- PostgreSQL 15 or higher
- Docker and Docker Compose (for containerized deployment)
- Git

### Local Setup

1. **Clone the repository**
```bash
git clone https://github.com/thezn0x/JobSage.git
cd JobSage
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
playwright install chromium
```

4. **Set up database**
```bash
# Create PostgreSQL database
createdb jobsage

# Run schema
psql -d jobsage -f schema.sql
```

5. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

### Docker Setup

1. **Clone repository**
```bash
git clone https://github.com/thezn0x/JobSage.git
cd JobSage
```

2. **Configure environment**
```bash
cp .env.example .env
# Edit .env if needed (defaults are provided)
```

3. **Start services**
```bash
docker compose up -d
```

This will start:
- PostgreSQL database on port 5433
- JobSage API on port 8000
- ETL scheduler for automated data collection

---

## Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/jobsage
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=jobsage
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

### Extractor Configuration

Edit `config/config.toml` to customize data extraction:

```toml
[extractors]
output_dir = "data/raw"

[extractors.rozee]
enabled = true
max_pages = 2
base_url = 'https://www.rozee.pk/job/jsearch/q/'
output_path = "data/raw/rozee.json"
card = 'div.job'

[extractors.careerjet]
enabled = true
max_pages = 2
base_url = 'https://www.careerjet.com.pk/jobs?l=Pakistan&nw=1&s='
output_path = "data/raw/careerjet.json"
card = 'ul.jobs li article.job'
```

### Scheduler Configuration

Modify `config/config.toml` to change the automation schedule (or use GUI in `config/config_GUI`):

```toml
[scheduler]
hour=2
minute=0
```
### Config GUI

**GUI for easy configuration**  
Run by following command:

```bash
python -m config.config_GUI
```

---

## Usage

### Running the ETL Pipeline Manually

**Extract data from job boards:**
```bash
python -m scripts.run_extractors
```

**Transform and clean the data:**
```bash
python -m scripts.run_transformers
```

**Load data into database:**
```bash
python -m scripts.run_loaders
```

**Run complete pipeline:**
```bash
bash run.sh  # Runs all three stages sequentially
```

### Starting the API Server

**Development mode:**
```bash
python -m scripts.run_api
```

**Production mode:**
```bash
uvicorn src.api.api_app:app --host 0.0.0.0 --port 8000
```

Access the API documentation at `http://localhost:8000/docs`

### Running the Scheduler

**Start automated daily runs:**
```bash
python -m scripts.sched
```

The scheduler will:
- Run the ETL pipeline immediately on startup
- Execute daily at 2:00 AM (configurable)
- Log all operations to `utils/logs.log` file
- Retry failed operations automatically

### Using Docker

**Start all services:**
```bash
docker compose up -d
```

**View logs:**
```bash
docker compose logs -f
```

**Stop services:**
```bash
docker compose down
```

**Rebuild after code changes:**
```bash
docker compose up -d --build
```

---

## API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### Skills

**Get trending skills**
```http
GET /skills/trending?limit=10
```
Returns the most in-demand technical skills across all job postings.

**Get skill details**
```http
GET /skills/detail/{skill_name}
```
Returns detailed information about a specific skill, including job count and market percentage.

**Get skill combinations**
```http
GET /skills/combinations/{skill_name}?limit=5
```
Returns skills that commonly appear together with the specified skill.

**Get trending skills by city**
```http
GET /skills/trending/{city_name}?limit=10
```
Returns top skills for a specific city (e.g., Lahore, Karachi, Islamabad).

#### Locations

**Get jobs by location**
```http
GET /locations/jobs
```
Returns job distribution across all cities and countries.

**Get top hiring cities**
```http
GET /locations/cities/top
```
Returns the city with the most job postings.

**Get companies in city**
```http
GET /locations/{city_name}/companies?limit=10
```
Returns companies hiring in a specific city.

#### Companies

**Get top hiring companies**
```http
GET /companies/top?limit=10
```
Returns companies with the most active job postings.

**Get company required skills**
```http
GET /companies/{company_name}/skills?limit=10
```
Returns the skills most frequently required by a specific company.

**Get company locations**
```http
GET /companies/locations/{company_name}
```
Returns all locations where a company is hiring.

### Response Format

All endpoints return JSON in the following format:

**Success Response:**
```json
{
  "success": true,
  "data": {
    "count": 10,
    "skills": [...]
  }
}
```

**Error Response:**
```json
{
  "detail": "Error message"
}
```

### API Examples

**Get top 5 skills:**
```bash
curl http://localhost:8000/skills/trending?limit=5
```

**Get Python skill details:**
```bash
curl http://localhost:8000/skills/detail/Python
```

**Get companies in Lahore:**
```bash
curl http://localhost:8000/locations/Lahore/companies
```

---

## Database Schema

### Core Tables

**jobs**: Primary table storing job posting information
- job_id (UUID, primary key)
- title, description, requirements
- company_id (foreign key to companies)
- employment_type, job_shift, job_level
- min_salary, max_salary, salary_currency
- min_experience
- posted_date, apply_before, scraped_date
- application_url

**companies**: Unique employer records
- company_id (UUID, primary key)
- name (unique)
- industry_id, location_id
- size, website, linkedin_url

**skills**: Master list of technical and soft skills
- skill_id (UUID, primary key)
- skill_name (unique)
- category_id (foreign key to skill_categories)

**locations**: Geographic information
- location_id (UUID, primary key)
- city, country
- Unique constraint on (city, country)

**platforms**: Job board sources
- platform_id (UUID, primary key)
- platform_name (unique)
- base_url

### Junction Tables

**job_skills**: Links jobs to required skills
- job_id, skill_id (composite primary key)
- is_required (boolean)
- experience_level (numeric)

**job_locations**: Links jobs to locations
- job_id, location_id (composite primary key)

**job_platforms**: Links jobs to source platforms
- job_id, platform_id (composite primary key)
- source_url
- scraped_date

### Lookup Tables

**industries**: Company industry categories
**skill_categories**: Skill type classifications (backend, frontend, etc.)

### Schema Features

- UUID primary keys for global uniqueness
- Proper foreign key constraints
- Strategic indexing for query performance
- Normalized structure for data integrity
- Support for many-to-many relationships
- Timestamp tracking for all records

---

## Development

### Project Structure

```
JobSage/
├── config/              # Configuration files
│   ├── config.toml      # Extractor/transformer settings
│   ├── settings.py      # Python config loader
│   └── control_panel/   # Web UI for management
├── docs/                # Documentation
│   ├── concept_note.md  # Project vision
│   └── SystemDesign.md  # Architecture details
├── scripts/             # Executable scripts
│   ├── run_extractors.py
│   ├── run_transformers.py
│   ├── run_loaders.py
│   ├── run_api.py
│   └── sched.py         # Scheduler
├── src/                 # Source code
│   ├── analytics/       # Query and analysis logic
│   ├── api/             # FastAPI application
│   ├── extractors/      # Web scraping modules
│   ├── loaders/         # Database loading
│   ├── transformers/    # Data cleaning
│   └── utils/           # Shared utilities
├── schema.sql           # Database schema
├── requirements.txt     # Python dependencies
├── Dockerfile           # Container definition
└── docker-compose.yml   # Multi-container setup
```

### Code Style

- Follow PEP 8 Python style guidelines
- Use type hints for function signatures
- Document complex functions with docstrings
- Keep functions focused and single-purpose
- Use meaningful variable and function names

### Adding New Extractors

1. Create new extractor class in `src/extractors/`
2. Inherit from `Extractor` base class
3. Implement `extract()` method
4. Add configuration to `config/config.toml`
5. Register in `scripts/run_extractors.py`

Example:
```python
from src.extractors.base import Extractor

class NewSiteExtractor(Extractor):
    def extract(self, card):
        # Implementation
        return job_data
```

### Adding New API Endpoints

1. Add method to `Analyzer` class in `src/analytics/main_analyzer.py`
2. Create endpoint in `src/api/api_app.py`
3. Apply `@handle_errors` decorator
4. Document the endpoint

Example:
```python
@app.get("/new/endpoint")
@handle_errors
def new_endpoint() -> Dict[str, Any]:
    results = analyzer.new_method()
    return {"count": len(results), "data": results}
```


### Logging

All components use a centralized logging system:

- Logs written to `logs/` directory
- Log level: INFO for console, DEBUG for file
- Format: `[LEVEL] timestamp - file:line : message`
- Automatic log rotation (to be implemented)

Access logs:
```bash
tail -f logs/control_panel.log
```

---

## Deployment

### Docker Deployment

**Production configuration:**

1. Set strong passwords in `.env`
2. Configure external database if needed
3. Update `docker-compose.yml` for production settings
4. Deploy to server:

```bash
docker compose -f docker-compose.prod.yml up -d
```

### VPS Deployment

**Manual deployment on Ubuntu/Debian:**

1. Install dependencies:
```bash
sudo apt update
sudo apt install python3.11 python3-pip postgresql nginx
```

2. Set up application:
```bash
git clone https://github.com/thezn0x/JobSage.git
cd JobSage
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

3. Configure systemd service:
```bash
sudo nano /etc/systemd/system/jobsage-api.service
```

```ini
[Unit]
Description=JobSage API
After=network.target postgresql.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/JobSage
Environment="PATH=/home/ubuntu/JobSage/venv/bin"
ExecStart=/home/ubuntu/JobSage/venv/bin/uvicorn src.api.api_app:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

4. Start services:
```bash
sudo systemctl enable jobsage-api
sudo systemctl start jobsage-api
```

5. Configure Nginx reverse proxy:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Cloud Platform Deployment

**Railway.app / Render.com:**

1. Connect GitHub repository
2. Set environment variables in dashboard
3. Configure build command: `pip install -r requirements.txt && playwright install chromium`
4. Configure start command: `uvicorn src.api.api_app:app --host 0.0.0.0 --port $PORT`
5. Deploy

### Monitoring

**Health checks:**
```bash
curl http://localhost:8000/
```

**Database connection:**
```bash
psql $DATABASE_URL -c "SELECT COUNT(*) FROM jobs;"
```

**Logs:**
```bash
docker compose logs -f api
docker compose logs -f etl-scheduler
```

---

## Contributing

Contributions are welcome and appreciated. To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Write or update tests if applicable
5. Update documentation as needed
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to your branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Contribution Guidelines

- Follow existing code style and conventions
- Add comments for complex logic
- Update README if adding new features
- Test your changes thoroughly
- Keep pull requests focused on a single feature or fix

### Reporting Issues

When reporting bugs, please include:
- Operating system and Python version
- Steps to reproduce the issue
- Expected vs actual behavior
- Relevant error messages and logs
- Screenshots if applicable

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.

---

## Acknowledgments

- **[znpg](https://github.com/thezn0x/znpg)**: Custom PostgreSQL wrapper library developed for this project
- **Playwright**: Reliable browser automation framework
- **FastAPI**: Modern, fast web framework for building APIs
- **PostgreSQL**: Robust relational database system

---

## Project Status

**Current Version:** 1.0.0  
**Status:** Production Ready  
**Maintained:** Yes  
**Last Updated:** February 2026

### Roadmap

**Future Enhancements:**
- Web dashboard
- Additional job board integrations
- Machine learning for salary prediction
- Skill demand forecasting
- User authentication and saved searches
- Email alerts for matching jobs
- Mobile application
- Advanced analytics dashboard
- Company reviews integration
- Application tracking

---

## Contact

**Developer:** [ZN-0X](https://instagram.com/zn0x.exe)  
**GitHub:** [@thezn0x](https://github.com/thezn0x)  
**Email:** thezn0x.exe@gmail.com  
**Project Link:** [https://github.com/thezn0x/JobSage](https://github.com/thezn0x/JobSage)

---

## Support

If you find this project helpful, please consider:
- Starring the repository
- Sharing it with others
- Contributing improvements
- Reporting bugs and suggesting features

For questions and support, please open an issue on GitHub.

---

**Built with dedication to bring transparency to Pakistan's tech job market.**