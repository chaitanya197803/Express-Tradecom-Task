# User Management REST API

## Project Overview
This is a production-ready User Management REST API application developed using Python 3.12+, Django 5+, Django REST Framework (DRF), and MySQL. The application is designed following clean architecture principles and maintains a highly modular code structure.

## Tech Stack
- **Backend Framework**: Django 5.x
- **API Framework**: Django REST Framework (DRF)
- **Database**: MySQL 8.x+
- **Documentation**: Swagger / OpenAPI (via `drf-spectacular`)
- **Other Libraries**: `django-filter`, `mysqlclient`, `python-dotenv`

---

## Installation

### 1. Clone Repository
```bash
git clone <repository_url>
cd Task
```

### 2. Create Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Requirements
Install dependencies using the virtual environment pip:
```bash
pip install -r requirements.txt
```
*(On macOS, if you encounter compilation errors for `mysqlclient`, ensure mysql is installed via Homebrew and run: `MYSQLCLIENT_CFLAGS="-I/opt/homebrew/Cellar/mysql/<version>/include/mysql" MYSQLCLIENT_LDFLAGS="-L/opt/homebrew/Cellar/mysql/<version>/lib -lmysqlclient -lz -lzstd -lssl -lcrypto -lresolv" pip install mysqlclient`)*

### 4. Configure MySQL
Ensure MySQL is running and create the `users` database:
```sql
CREATE DATABASE users;
```

Configure your credentials in the `.env` file at the project root.

### 5. Run Migrations
Apply the migrations to set up the database schema:
```bash
python manage.py migrate
```

### 6. Start Server
Run the local development server:
```bash
python manage.py runserver
```
The server will start at `http://127.0.0.1:8000/`.

---

## Environment Variables
The application reads settings from a `.env` file at the project root. The following keys are supported:

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | `django-insecure-...` |
| `DEBUG` | Enable/disable debug mode (`True`/`False`) | `True` |
| `DB_NAME` | MySQL database name | `users` |
| `DB_USER` | MySQL username | `root` |
| `DB_PASSWORD`| MySQL password | (empty) |
| `DB_HOST` | MySQL database host | `127.0.0.1` |
| `DB_PORT` | MySQL database port | `3306` |

---

## Database Schema

### `users` Table
The application creates a table named `users` in MySQL:

| Column Name | Data Type | Attributes |
|-------------|-----------|------------|
| `id` | INT | Primary Key, Auto Increment |
| `name` | VARCHAR(255) | Required, Not Null |
| `email` | VARCHAR(255) | Required, Unique, Not Null |
| `role` | VARCHAR(100) | Required, Not Null |

---

## API Documentation

The project includes interactive API documentation. Start the server and navigate to:
- **Swagger UI**: `http://127.0.0.1:8000/swagger/`
- **Redoc**: `http://127.0.0.1:8000/redoc/`

### Endpoints

#### 1. Get All Users
- **Method**: `GET`
- **Endpoint**: `/users` or `/users/`
- **Response Example**:
  ```json
  {
    "success": true,
    "count": 1,
    "data": [
      {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com",
        "role": "Admin"
      }
    ]
  }
  ```

#### 2. Create User
- **Method**: `POST`
- **Endpoint**: `/users` or `/users/`
- **Request Body Example**:
  ```json
  {
    "name": "John Doe",
    "email": "john@example.com",
    "role": "Admin"
  }
  ```
- **Response Example (201 Created)**:
  ```json
  {
    "success": true,
    "message": "User created successfully",
    "data": {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "role": "Admin"
    }
  }
  ```

#### 3. Get User By ID
- **Method**: `GET`
- **Endpoint**: `/users/{id}`
- **Response Example (200 OK)**:
  ```json
  {
    "success": true,
    "data": {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "role": "Admin"
    }
  }
  ```

#### 4. Search Users
- **Method**: `GET`
- **Endpoint**: `/users?search=value`
- **Description**: Performs a case-insensitive search matching `name` or `email`.
- **Response Example**:
  ```json
  {
    "success": true,
    "count": 1,
    "data": [
      {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com",
        "role": "Admin"
      }
    ]
  }
  ```

#### 5. Pagination
- **Method**: `GET`
- **Endpoint**: `/users?page=1&limit=10`
- **Response Example**:
  ```json
  {
    "success": true,
    "page": 1,
    "limit": 10,
    "total_records": 100,
    "total_pages": 10,
    "data": [...]
  }
  ```

### Validation Errors

- **Invalid Email Format** (Status `400`):
  ```json
  {
    "success": false,
    "error": "Invalid email format"
  }
  ```

- **Duplicate Email** (Status `409`):
  ```json
  {
    "success": false,
    "error": "Email already exists"
  }
  ```

- **User Not Found** (Status `404`):
  ```json
  {
    "success": false,
    "error": "User not found"
  }
  ```

---

## Assumptions
1. **SQLite for Unit Tests**: When running automated tests using `python manage.py test`, Django automatically configures the database connection to use an in-memory SQLite database. This speeds up test execution and bypasses the need for a running local MySQL server during CI/CD or test validation.
2. **Case-Insensitive Search**: The search query param checks both the name and email fields using case-insensitive substring matching (`__icontains`).
3. **Roles**: Roles are stored as plain strings (VARCHAR(100)) to allow flexible role designations.
