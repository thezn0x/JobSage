# JobSage 🚀

**Pakistan's First Career Intelligence Platform**

JobSage is a data-driven platform designed to bring transparency to Pakistan's tech job market. It aggregates job postings from multiple platforms, extracts key insights like in-demand skills and salary ranges, and provides actionable career intelligence for developers and students.

---

## 🌟 Key Features

- **Automated Data Aggregation:** Scrapes job postings from major Pakistani job boards including Rozee.pk, Careerjet, and more.
- **Skill Extraction:** Uses pattern matching to identify core technical and soft skills from job descriptions.
- **Salary Analysis:** Normalizes and analyzes salary ranges to provide market benchmarks.
- **Trend Tracking:** Monitors the growth and decline of specific technologies over time.
- **Interactive Dashboard:** (In Development) A Streamlit-based interface for visualizing market data.

---

## 🛠 Tech Stack

- **Language:** Python 3.14+
- **Web Scraping:** Playwright (Headless Browser)
- **Data Processing:** Pandas
- **Database:** PostgreSQL (with `znpg` wrapper)
- **Configuration:** TOML & Environment variables
- **Orchestration:** Apache Airflow (Planned)

---

## 📁 Project Structure

```text
.
├── config/             # Project configuration (settings, .env, TOML)
├── docs/               # Technical documentation and concept notes
│   ├── CONCEPT_NOTE.md # Original project vision and goals
│   └── SystemDesign.txt# Database and system architecture details
├── scripts/            # ETL pipeline runner scripts
├── src/                # Core source code
│   ├── extractors/     # Web scraping logic for different platforms
│   ├── transformers/   # Data cleaning and normalization logic
│   ├── loaders/        # Database loading modules
│   └── utils/          # Shared utilities (logger, db connection)
├── schema.sql          # PostgreSQL database schema
├── pyproject.toml      # Project dependencies and metadata
└── requirements.txt    # Python package requirements
```

---

## ⚙️ Installation & Setup

### 1. Prerequisites
- Python 3.14 or higher
- PostgreSQL database
- Node.js (for Playwright dependencies, usually handled by pip)

### 2. Clone the Repository
```bash
git clone https://github.com/thezn0x/JobSage.git
cd JobSage
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
playwright install chromium
```

### 4. Database Setup
1. Create a PostgreSQL database.
2. Execute the `schema.sql` file to create the necessary tables:
```bash
psql -h localhost -U your_username -d your_database -f schema.sql
```

### 5. Configuration
1. Copy `config/.env.example` to `config/.env`.
2. Update the `DATABASE_URL` and other environment variables in `config/.env`.

---

## 🚀 Usage

The ETL (Extract, Transform, Load) pipeline is split into three main stages:

### 1. Extraction
Run the scrapers to fetch raw job data from supported platforms:
```bash
python scripts/run_extractors.py
```
*Extracted data is typically saved as JSON files in a configured output directory.*

### 2. Transformation
Clean and normalize the extracted data:
```bash
python scripts/run_transformers.py
```
*This stage handles deduplication, salary parsing, and skill extraction.*

### 3. Loading
Load the cleaned data into the PostgreSQL database:
```bash
python scripts/run_loaders.py
```

---

## 📊 Database Schema

JobSage uses a normalized PostgreSQL schema to ensure data integrity and efficient querying:

- **jobs:** Core table for job posting details.
- **companies:** Unique list of hiring organizations.
- **skills:** Master list of technical and soft skills.
- **locations:** Standardized cities and countries.
- **platforms:** Job boards where data is sourced from.
- **Junction Tables:** `job_skills`, `job_platforms`, and `job_locations` manage many-to-many relationships.

Refer to `schema.sql` for the full DDL.

## Future updates (coming gradually)

- **Apache Airflow:** Adding Apache AirFlow to schedule the pipeline.
- **Analytics:** Adding analytics to make it actually helpfull.
 
---

## 📄 Documentation

For more detailed information, please refer to the files in the `docs/` directory:
- [Concept Note](docs/CONCEPT_NOTE.md)
- [System Design](docs/SystemDesign.txt)

---

## 🤝 Contributing

Contributions are welcome! If you'd like to improve JobSage, please:
1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Open a Pull Request.

---

## 📜 License

This project is licensed under the **MIT License**.

---

**Developed by [ZN-0X](https://github.com/thezn0x)**
