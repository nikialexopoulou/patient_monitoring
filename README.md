## Patient Monitoring API
A Django REST API for managing patients in a clinical environment. The system tracks patients, the devices assigned to them, incoming vital-sign observations recorded from those devices, and alerts generated when observations fall outside safe thresholds.

---

### Tech stack
- Django  
- Django REST Framework  
- PostgreSQL  
- drf-spectacular for OpenAPI/Swagger  
- pytest + pytest-django  
- pre-commit  
- Docker Compose

---

### Setup from a clean checkout
1. Clone the repository
```
git clone <repo-url>  
cd patient_monitoring
```

2. Start the application with Docker
`make up`  

3. Apply migrations
`make migrate`  

4. Open the API
   - Application: http://localhost:8000
   - Swagger: http://localhost:8000/api/docs/  

---

### How to run the application
```
make up 
make down  
make logs  
make shell  
make dbshell  
```

---

### How to run the tests
```
make test  
make test-create-db  
```

---

### Environment variables
Configured via Docker Compose:

- POSTGRES_DB=patient_monitoring  
- POSTGRES_USER=admin  
- POSTGRES_PASSWORD=admin  
- POSTGRES_HOST=db
- POSTGRES_PORT=5432  

---

### Authentication
Lightweight DRF Token Authentication is used.

- Create user: `make createsuperuser`  
- Create token: `make token USER=<username>`  
- Use token: `Authorization: Token <your_token>`  

---

### Demo data
`make seed`  

---

### API endpoints

- POST /api/patients/  
- GET /api/patients/  
- GET /api/patients/{id}/
- PATCH /api/patients/{id}/  
- GET /api/patients/high-risk/
- GET /api/patients/{id}/observations/  

- POST /api/devices/{id}/assign/  

- POST /api/observations/  
- GET /api/observations/?from=...&to=...  

- GET /api/alerts/?severity=...&is_active=...  

---

### Design

1. Patient entry
   * Patients are created via API with explicit flags:
     - is_high_priority  
     - spi_enabled
2. Alert generation
   * Alerts are generated per condition:
     - HIGH_HEART_RATE  
     - HIGH_TEMPERATURE  
     - LOW_SPO2  
3. Deduplication
   * Only one active alert per patient + type. 
   * Implemented via:
     - application logic  
     - PostgreSQL partial unique constraint  
4. Device assignment
   * Safe under concurrency using:
     - transactions  
     - select_for_update()  
5. High-risk patients
   * Implemented using EXISTS subquery at DB level.

---

### Engineering decisions
**Assumptions**
- One alert per condition  
- Deduplication skips duplicates  

**Tradeoffs**
- Simple domain model  
- Token auth instead of JWT  
- No background processing  

**Future improvements**
- Alert lifecycle
- Better auth & permissions  
- Audit logs  
- CI pipeline  
- Metrics & monitoring  

---

### Optional enhancements
- PostgreSQL  
- OpenAPI / Swagger  
- pre-commit  
- DB constraints  
- Transaction safety  
- Token auth  
- Seed data  

---

### Formatting and linting
Code quality is enforced via pre-commit hooks.

- Run checks manually: `make lint`
- Enable hooks: `pre-commit install`  
