"""Deployment boundaries checked without contacting a hosted database."""

import base64
import json
import os
import subprocess
import sys
from pathlib import Path

from django.test import SimpleTestCase, override_settings


class DeploymentTests(SimpleTestCase):
    def settings_process(self, **values):
        environment = {
            key: value
            for key, value in os.environ.items()
            if key not in {"DATABASE_URL", "VERCEL", "DJANGO_DEBUG", "DJANGO_SECRET_KEY"}
        }
        environment.update(DJANGO_DEBUG="false", DJANGO_SECRET_KEY="x" * 64, **values)
        return subprocess.run(
            [
                sys.executable,
                "-c",
                "import json;from project.settings import DATABASES;print(json.dumps(DATABASES['default']))",
            ],
            cwd=Path(__file__).resolve().parents[1],
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_hosted_url_selects_postgresql_with_tls(self):
        response = self.settings_process(
            DATABASE_URL="postgresql://demo:sample%2Fpassword@db.example.invalid:5432/mybud?sslmode=require",
            VERCEL="1",
        )
        self.assertEqual(response.returncode, 0, response.stderr)
        config = json.loads(response.stdout)
        self.assertEqual(config["ENGINE"], "django.db.backends.postgresql")
        self.assertEqual(config["PASSWORD"], "sample/password")
        self.assertEqual(config["OPTIONS"]["sslmode"], "require")
        self.assertEqual(config["CONN_MAX_AGE"], 0)

    def test_serverless_deployment_rejects_missing_persistent_database(self):
        response = self.settings_process(VERCEL="1")
        self.assertNotEqual(response.returncode, 0)
        self.assertIn("DATABASE_URL", response.stderr)

    def test_hosted_url_preserves_stronger_tls_verification(self):
        for sslmode in ("verify-ca", "verify-full"):
            with self.subTest(sslmode=sslmode):
                response = self.settings_process(
                    DATABASE_URL=f"postgresql://demo:password@db.example.invalid:5432/mybud?sslmode={sslmode}",
                    VERCEL="1",
                )
                self.assertEqual(response.returncode, 0, response.stderr)
                config = json.loads(response.stdout)
                self.assertEqual(config["OPTIONS"]["sslmode"], sslmode)

    def test_serverless_deployment_rejects_sqlite_url(self):
        response = self.settings_process(DATABASE_URL="sqlite:///temporary.sqlite3", VERCEL="1")
        self.assertNotEqual(response.returncode, 0)
        self.assertIn("PostgreSQL", response.stderr)

    @override_settings(MYBUD_MAX_IMAGE_MB=3)
    def test_hosted_image_limit_is_disclosed_and_enforced(self):
        from main.services.assistant import prepare

        response = self.client.get("/recipe/")
        self.assertContains(response, "up to 3 MB")
        payload = base64.b64encode(b"x" * (3 * 1024 * 1024 + 1)).decode()
        with self.assertRaisesRegex(ValueError, "3 MB"):
            prepare("detect-food", {"image": payload})
