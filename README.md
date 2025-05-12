# Inventory Management System API

A comprehensive REST API built with Flask for managing inventory, tracking products, stock levels, customers, suppliers, and orders.

## Features

- **Complete Inventory Tracking**: Manage products, categories, stock levels, and pricing
- **Order Management**: Track both incoming (supplier) and outgoing (customer) orders
- **User Authentication**: Secure JWT-based authentication with role-based access control
- **Automated Calculations**: Background calculations for inventory, pricing, and discounts
- **Email Integration**: Automated notifications for orders and system events
- **RESTful API Design**: Well-structured endpoints following REST principles

## Tech Stack

- **Framework**: Flask
- **Database**: SQLAlchemy
- **Authentication**: Flask-JWT-Extended
- **Email**: Flask-Mail
- **Validation**: Flask-Marshmallow
- **Package Management**: Poetry

## Getting Started

### Prerequisites

- Python 3.8+
- Poetry package manager

### Installation

1. Clone the repository:

```bash
  git clone https://github.com/EmmyAnieDev/inventory-management-system.git
  cd inventory-management-system
```

2. Install dependencies with Poetry:

```bash
  poetry install
```

3. Create a `.env` file in the project root:

```bash
  cp .env.sample .env
```

Then edit the `.env` file with your specific configuration values.

### Environment Setup

#### Using Poetry (Recommended)

1. Install Poetry if you haven't already:

```bash
  curl -sSL https://install.python-poetry.org | python3 -
```

2. Create a virtual environment with Poetry:

```bash
  poetry env use python3.8  # or your preferred Python version
```

3. Activate the virtual environment:

```bash
  poetry shell
```

Alternatively, you can run commands within the virtual environment without activating it:

```bash
  poetry run <command>
```

#### Using Standard Python venv

1. **Create a virtual environment**:  

```bash
  python3 -m venv .venv
```

2. **Activate the virtual environment**:  

- On macOS/Linux:  

```bash
  source .venv/bin/activate
```

- On Windows (PowerShell):  

```bash
  .venv\Scripts\Activate
```

3. **Install Poetry (if not already installed)**:

```bash
  pip install poetry
```

4. **Install project dependencies using Poetry**:  

```bash
  poetry install
```


### Running the Application

#### Option 1: Using Docker (Recommended)

Build and start the containers:

```bash
  docker-compose up -d
```

#### Option 2: (Using Poetry)

1. Activate the Poetry virtual environment (if not already activated):

```bash
  poetry shell
```

2. Create the database:

```bash
  flask db upgrade
```

3. Run the application:

```bash
  python app.py
```

The API will be available at `http://localhost:5000/`.

The API documentation will be available at http://localhost:5000/apidocs.

## Project Structure

```
InventoryManagement/
├── .venv/
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── core/
│   │   │   └── __init__.py
│   │   ├── db/
│   │   │   └── __init__.py  # Contains db = SQLAlchemy()
│   │   ├── utils/
│   │   │   └── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── models/
│   │       │   ├── __init__.py
│   │       │   ├── base.py  # BaseModel definition
│   │       │   └── user.py  # User model
│   │       ├── routes/
│   │       │   └── __init__.py
│   │       ├── schemas/
│   │       │   └── __init__.py
│   │       └── services/
│   │           └── __init__.py
│   └── __init__.py
├── .env
├── .env.sample
├── .gitignore
├── app.py
├── config.py
├── poetry.lock
├── pyproject.toml
└── README.md
```

### Development Tasks

#### Adding Dependencies

```bash
  poetry add package-name
```

For development dependencies:

```bash
  poetry add --dev package-name
```

#### Running Tests

```bash
  poetry run pytest
```

#### Database Migrations

Initialize migrations (first time only):

```bash
  flask db init
```

Create a new migration:

```bash
  flask db migrate -m "Description of changes"
```

Apply migrations:

```bash
  flask db upgrade
```

## License
![License](https://img.shields.io/badge/license-MIT-blue.svg)