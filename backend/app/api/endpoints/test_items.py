from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from ...main import app
from ...db import crud, models
from ...db.schemas.item import ItemCreate

client = TestClient(app)

def test_create_item(test_client, get_db_username_password_token):
    # Create and authenticate a test user
    test_db, username, password, token = get_db_username_password_token
    
    # Set authorization header
    headers = {'Authorization': f'Bearer {token}'}
    
    # Define a new item
    new_item = {
        "title": "Test Item",
        "description": "This is a test item"
    }
    
    # Simulate a request to create an item
    response = client.post("/items/", json=new_item, headers=headers)
    
    assert response.status_code == 200, response.json()
    
    data = response.json()
    assert data["title"] == new_item["title"], "Incorrect title"
    assert data["description"] == new_item["description"], "Incorrect description"
    assert data["owner_id"] is not None, "Owner ID is not set"
    
    # Clean up: Delete the created item from the database
    #crud.delete_item(test_db, item_id=data["id"], user_id=data["owner_id"])

def test_get_items(test_client, get_db_username_password_token):
    test_db, username, password, token = get_db_username_password_token
    headers = {'Authorization': f'Bearer {token}'}
    
    # Simulate a request to get items
    response = client.get("/items/", headers=headers)
    
    assert response.status_code == 200, response.json()
    
    items = response.json()
    assert isinstance(items, list), "Response is not a list"

def test_protected_route(test_client, get_db_username_password_token):
    test_db, username, password, token = get_db_username_password_token
    headers = {'Authorization': f'Bearer {token}'}
    
    # Simulate a request to the protected route
    response = client.get("/items/protected", headers=headers)
    
    assert response.status_code == 200, response.json()
    
    data = response.json()
    assert data["message"] == "You have access to this protected route"
    assert data["username"] == username
