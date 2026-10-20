"""HTTP regression checks for student tools and private expense storage."""

import base64
import io
import json
from decimal import Decimal
from unittest.mock import patch

from django.test import Client, TestCase, override_settings
from PIL import Image


@override_settings(MYBUD_MODE="demo")
class AppTests(TestCase):
    def post(self, path, data, client=None):
        return (client or self.client).post(path, json.dumps(data), content_type="application/json")

    def test_all_pages_render_with_identity_and_mode(self):
        for path in ("/", "/chat/", "/code/", "/recipe/", "/travel/", "/expenses/"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "Bikash Kushwaha")
                self.assertContains(response, "Demo mode")

    def test_chat_contract(self):
        response = self.post("/api/chat/", {"message": "Help me study"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertEqual(response.json()["mode"], "demo")
        self.assertIsInstance(response.json()["response"], str)

    def test_code_service_import_and_syntax_analysis(self):
        response = self.post("/api/code/", {"code": "def broken(:", "language": "python"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["analysis"]["bugs"])

    def test_code_is_never_executed(self):
        response = self.post("/api/code/", {"code": "raise RuntimeError('never execute')"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["analysis"]["bugs"], [])

    def test_recipe_shape(self):
        data = self.post("/api/recipes/", {"ingredients": ["rice", "peas"]}).json()
        self.assertIsInstance(data["recipes"], list)
        self.assertIsInstance(data["recipes"][0]["instructions"], list)

    def test_travel_and_itinerary(self):
        response = self.post("/api/travel/", {"destination": "Sample destination", "duration": 3})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["data"]["itinerary"]), 3)

    def test_invalid_json_and_wrong_root_type(self):
        for body in ("{", "[]", "null", '"text"'):
            with self.subTest(body=body):
                response = self.client.post("/api/chat/", body, content_type="application/json")
                self.assertEqual(response.status_code, 400)

    def test_invalid_inputs_rejected(self):
        cases = [
            ("chat", {"message": 10}),
            ("chat", {"message": " "}),
            ("code", {"code": "x" * 20001}),
            ("recipes", {"ingredients": "rice"}),
            ("recipes", {"ingredients": [1]}),
            ("travel", {"destination": "A", "duration": 31}),
            ("travel", {"destination": "A", "duration": True}),
            ("detect-food", {"image": "not base64"}),
        ]
        for endpoint, payload in cases:
            with self.subTest(endpoint=endpoint, payload=str(payload)[:80]):
                self.assertEqual(self.post(f"/api/{endpoint}/", payload).status_code, 400)

    def test_get_does_not_trigger_ai(self):
        for endpoint in ("chat", "code", "recipes", "travel", "detect-food"):
            self.assertEqual(self.client.get(f"/api/{endpoint}/").status_code, 405)

    def test_api_requires_csrf(self):
        client = Client(enforce_csrf_checks=True)
        self.assertEqual(self.post("/api/chat/", {"message": "Hello"}, client).status_code, 403)
        client.get("/")
        response = client.post(
            "/api/chat/",
            json.dumps({"message": "Hello"}),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value,
        )
        self.assertEqual(response.status_code, 200)

    def test_page_post_does_not_swallow_api_request(self):
        self.assertEqual(self.post("/chat/", {"message": "Hello"}).status_code, 405)

    def test_expenses_use_exact_decimal_arithmetic(self):
        self.post("/api/expenses/", {"action": "budget", "amount": "100.00"})
        self.post("/api/expenses/", {"action": "add", "category": "Meals", "amount": "0.10"})
        self.post("/api/expenses/", {"action": "add", "category": "Meals", "amount": "0.20"})
        data = self.client.get("/api/expenses/").json()
        self.assertEqual(Decimal(data["total"]), Decimal("0.30"))
        self.assertEqual(Decimal(data["remaining"]), Decimal("99.70"))

    def test_expenses_are_isolated_by_browser_session(self):
        other = Client()
        self.post("/api/expenses/", {"action": "add", "category": "Travel", "amount": "75"})
        self.assertEqual(other.get("/api/expenses/").json()["expenses"], [])
        item = self.client.get("/api/expenses/").json()["expenses"][0]
        self.assertEqual(
            self.post("/api/expenses/", {"action": "delete", "id": item["id"]}, other).status_code,
            404,
        )

    def test_invalid_money_never_enters_database(self):
        for amount in ("-1", "0", "NaN", "Infinity", "0.001", "100000000", True, None):
            self.assertEqual(
                self.post(
                    "/api/expenses/", {"action": "add", "category": "Meals", "amount": amount}
                ).status_code,
                400,
            )
        self.assertEqual(self.client.get("/api/expenses/").json()["expenses"], [])

    def test_delete_and_reset(self):
        self.post("/api/expenses/", {"action": "budget", "amount": "100"})
        self.post("/api/expenses/", {"action": "add", "category": "Books", "amount": "120"})
        data = self.client.get("/api/expenses/").json()
        self.assertTrue(data["exceeded"])
        self.post("/api/expenses/", {"action": "delete", "id": data["expenses"][0]["id"]})
        self.assertEqual(self.client.get("/api/expenses/").json()["total"], "0.00")
        self.post("/api/expenses/", {"action": "reset"})
        self.assertIsNone(self.client.get("/api/expenses/").json()["budget"])

    def test_valid_image_demo_does_not_claim_recognition(self):
        output = io.BytesIO()
        Image.new("RGB", (8, 8), "white").save(output, format="PNG")
        data = self.post(
            "/api/detect-food/",
            {"image": "data:image/png;base64," + base64.b64encode(output.getvalue()).decode()},
        ).json()
        self.assertTrue(data["success"])
        self.assertIn("not classified", data["dish"]["description"])

    @override_settings(MYBUD_MODE="live", GEMINI_API_KEY="", GEMINI_MODEL="")
    def test_live_mode_requires_configuration(self):
        response = self.post("/api/chat/", {"message": "Hello"})
        self.assertEqual(response.status_code, 503)
        self.assertFalse(response.json()["success"])

    @override_settings(
        MYBUD_MODE="live", GEMINI_API_KEY="test-placeholder", GEMINI_MODEL="configured-model"
    )
    @patch(
        "main.services.assistant.generate_live",
        side_effect=RuntimeError("private provider details"),
    )
    def test_provider_failure_is_not_success(self, _provider):
        response = self.post("/api/chat/", {"message": "Hello"})
        self.assertEqual(response.status_code, 502)
        self.assertNotIn("private provider details", response.content.decode())

    @override_settings(
        MYBUD_MODE="live", GEMINI_API_KEY="test-placeholder", GEMINI_MODEL="configured-model"
    )
    @patch(
        "main.services.assistant.generate_live",
        return_value={"response": "Connected test response"},
    )
    def test_mocked_live_contract(self, _provider):
        response = self.post("/api/chat/", {"message": "Hello"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["mode"], "live")

    @override_settings(
        MYBUD_MODE="live", GEMINI_API_KEY="test-placeholder", GEMINI_MODEL="configured-model"
    )
    @patch("main.services.assistant.generate_live", return_value={"recipes": "invalid shape"})
    def test_bad_provider_schema_rejected(self, _provider):
        response = self.post("/api/recipes/", {"ingredients": ["rice"]})
        self.assertEqual(response.status_code, 502)

    @override_settings(
        MYBUD_MODE="live", GEMINI_API_KEY="test-placeholder", GEMINI_MODEL="configured-model"
    )
    @patch("main.services.assistant.generate_live", side_effect=ValueError("private parse details"))
    def test_provider_parse_error_is_sanitized(self, _provider):
        response = self.post("/api/chat/", {"message": "Hello"})
        self.assertEqual(response.status_code, 502)
        self.assertNotIn("private parse details", response.content.decode())

    @override_settings(
        MYBUD_MODE="live", GEMINI_API_KEY="test-placeholder", GEMINI_MODEL="configured-model"
    )
    @patch(
        "main.services.assistant.generate_live",
        return_value={"response": "ok", "mode": "demo", "success": False},
    )
    def test_provider_cannot_override_response_envelope(self, _provider):
        response = self.post("/api/chat/", {"message": "Hello"})
        self.assertEqual(response.status_code, 502)

    def test_corrupt_png_checksum_is_a_client_error(self):
        image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/l9sAAAAASUVORK5CYII="
        response = self.post("/api/detect-food/", {"image": "data:image/png;base64," + image})
        self.assertEqual(response.status_code, 400)
