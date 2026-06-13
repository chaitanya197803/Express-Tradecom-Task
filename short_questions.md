# Technical Interview Questions & Answers

### 1. Why did you choose Django?
* **Batteries-Included Architecture**: Django comes out-of-the-box with a secure ORM, migration system, authentication/authorization modules, admin panel, and middleware. This drastically reduces boilerplate code.
* **Security Defaults**: It handles cross-site scripting (XSS), cross-site request forgery (CSRF), SQL injection, and clickjacking protection automatically.
* **REST Framework (DRF) Ecosystem**: Combined with Django REST Framework, we get robust features like serialization, viewsets, built-in pagination, filtering, and seamless documentation auto-generation via `drf-spectacular`.

---

### 2. How would you scale this system?
* **Database Optimization**:
  * **Read-Write Splitting / Replication**: Set up read replicas for read-heavy operations (e.g., listing/searching users) and keep a primary database instance for write operations.
  * **Database Indexing**: Add database indexes on fields frequently used in search queries (e.g., `email`, `name`).
  * **Connection Pooling**: Use a tool like **PgBouncer** to manage PostgreSQL database connections efficiently.
* **Caching**: Use **Redis** with Django's caching framework to store frequently requested user profiles or query results, preventing redundant database hits.
* **Asynchronous Tasks**: Offload background operations (e.g., sending verification emails upon user registration) to task queues using **Celery** with **RabbitMQ/Redis**.
* **Load Balancer & Auto-Scaling**: Deploy behind an **Nginx** or **AWS ALB** reverse proxy/load balancer and run multiple WSGI/ASGI application worker nodes (using **Gunicorn/Uvicorn**) in a stateless manner (e.g., using Docker & Kubernetes) to scale out horizontally as traffic grows.

---

### 3. What changes would you make for production?
* **Security Configurations**:
  * Set `DEBUG = False` in your settings to disable verbose error reporting.
  * Set a strong, randomly generated `SECRET_KEY` pulled securely from an environment variable vault (e.g., AWS Secrets Manager).
  * Configure security headers: `SECURE_SSL_REDIRECT = True`, `SESSION_COOKIE_SECURE = True`, and `CSRF_COOKIE_SECURE = True`.
* **Database & Infrastructure**:
  * Move from local/standalone PostgreSQL to a managed database service (like **AWS RDS PostgreSQL** or **GCP Cloud SQL**) with automated backups and Multi-AZ high availability.
* **Static File Hosting**: Use **WhiteNoise** or offload static files directly to an **Amazon S3** bucket behind a CDN (**CloudFront** / **Cloudflare**) for faster delivery.
* **Logging & Monitoring**: 
  * Configure centralized logging to output to standard output (stdout/stderr) for container orchestration (Twelve-Factor App rule).
  * Integrate an APM tool like **Sentry** for real-time error tracking and **Prometheus/Grafana** for resource metrics.
