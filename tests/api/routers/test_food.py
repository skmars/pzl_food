import json

import pytest
from fastapi.testclient import TestClient

from app.application import app

client = TestClient(app)


@pytest.mark.db_test
class TestFood:
    async def test_get_food_not_scpecial(self, db_session, test_context, make_foods):
        not_special_food = make_foods(is_special=False)
        _ = make_foods()
        food_input_data = {"is_special": False}
        resp = client.post("/get_foods", data=json.dumps(food_input_data))
        data_from_resp = resp.json()
        assert resp.status_code == 200
        assert data_from_resp.len() != 0
        assert data_from_resp[0].id == not_special_food.id

    async def test_get_food_is_published_grouped_by_category(
        self, db_session, test_context, make_foods, make_food_category
    ):
        food_category_1 = make_food_category().id
        food_category_2 = make_food_category(name="Напитки").id
        _ = make_foods(is_published=False, category_id=food_category_1)
        _ = make_foods(category_id=food_category_1)
        _ = make_foods(category_id=food_category_2)
        _ = make_foods()
        food_input_data = {"is_published": True, "grouped_by_categories": True}
        resp = client.post("/get_foods", data=json.dumps(food_input_data))
        data_from_resp = resp.json()
        assert resp.status_code == 200
        assert data_from_resp.len() == 2

    async def test_get_food_with_topping_name(self, db_session, test_context, make_foods):
        _ = make_foods(topping_names=["Рог единорога", "Рак на горе"])
        _ = make_foods()
        food_input_data = {"topping_name": "Рог единорога"}
        resp = client.post("/get_foods", data=json.dumps(food_input_data))
        data_from_resp = resp.json()
        assert resp.status_code == 200
        assert data_from_resp.len() == 1

    async def test_create_food(self, db_session, test_context, make_food_category):
        food_category = make_food_category(name="Напитки").id
        food_input_data = {
            "description": "Что-то веганское",
            "price": 16,
            "is_special": True,
            "is_vegan": True,
            "is_published": True,
            "category_id": food_category,
            "toppings": ["Волшебная пыль", "Яйцо страуса"],
        }
        resp = client.post("/create_food", data=json.dumps(food_input_data))
        data_from_resp = resp.json()
        assert resp.status_code == 200
        assert data_from_resp.len() == 1
        assert data_from_resp[0].price == 16

    async def test_update_food_with_topping_name(self, db_session, test_context, make_foods):
        old_food = make_foods()
        food_input_data = {"id": old_food.id, "name": "Новинка"}
        resp = client.post("/update_food", data=json.dumps(food_input_data))
        data_from_resp = resp.json()
        assert resp.status_code == 200
        assert data_from_resp[0].name == "Новинка"

    async def test_delete_food(self, db_session, test_context, make_foods):
        old_food = make_foods()
        food_input_data = {"ids": [old_food.id]}
        resp = client.post("/delete_food", data=json.dumps(food_input_data))
        data_from_resp = resp.json()
        assert resp.status_code == 200
        assert data_from_resp.len() != 0

    async def test_food_not_found(self, db_session, test_context):
        food_input_data = {"ids": [11, 22]}
        resp = client.post("/get_foods", data=json.dumps(food_input_data))
        assert resp.status_code == 404
