# FastAPI Product Catalog Mini-Project

## Description
This is a simple CRUD Product Catalog built with FastAPI.  
You can create, read, update, and delete products using REST API endpoints.  

This mini-project demonstrates:
- FastAPI framework usage
- FastAPI-CRUDRouter for automatic CRUD route generation
- SQLite database integration using SQLAlchemy
- Asynchronous database operations

## Who is this useful for?
- Beginners learning FastAPI and CRUD operations
- Developers needing a quick product catalog prototype
- Anyone looking to understand API design with FastAPI

## Features
- List all products
- Add a new product
- Update an existing product
- Delete a product
- Automatic Swagger UI documentation

## Setup Instructions

1. Clone the repository:

```bash
git clone <your-repo-url>
cd fastapi-crudrouter
2. Create a virtual environment:

```bash
python -m venv venv
3. Activate the virtual environment:
source venv/bin/activate
4. Install dependencies:
pip install -r requirements.txt
5. Run the application:
uvicorn main:app --reload

Open your browser and go to http://127.0.0.1:8000/docs
 to access Swagger UI and test the endpoints.
 | Method | Endpoint       | Description                |
| ------ | -------------- | -------------------------- |
| GET    | /products      | List all products          |
| POST   | /products      | Create a new product       |
| PUT    | /products/{id} | Update an existing product |
| DELETE | /products/{id} | Delete a product           |

Sample Product JSON
{
  "name": "Travel Backpack",
  "description": "Durable 40L backpack ideal for short trips.",
  "price": 2499.99,
  "quantity": 10,
  "id": 1
}

Project Structure
fastapi-crudrouter/
│
├── app.py              # Main FastAPI app and endpoints
├── database.py         # Database setup (SQLite + SQLAlchemy)
├── models.py           # Pydantic/SQLAlchemy models
├── schemas.py          # Pydantic schemas for request/response
├── test.db             # SQLite database file
├── requirements.txt    # Dependencies
├── README.md           # Project documentation
└── venv/               # Virtual environment (optional)

Technologies Used

Python 3.11+
FastAPI
FastAPI-CRUDRouter
SQLite
SQLAlchemy
ggiPydantic