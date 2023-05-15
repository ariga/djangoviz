import json
from io import StringIO
from unittest.mock import MagicMock, patch, call

from django.core import management
from django.core.management.base import BaseCommand
from django.test import TransactionTestCase


class CommandTests(TransactionTestCase):
    @patch("djangoviz.management.commands.djangoviz.GraphQLClient")
    def test_command(self, mock_client):
        mutation1 = """
        mutation Visualize($text: String!, $driver: Driver!) {
            visualize(input: {text: $text, driver: $driver, dryRun: true, type: SQL}) {
                node {
                    hcl
                }
            }
        }
        """
        mutation2 = """
    mutation Visualize($text: String!, $driver: Driver!) {
        visualize(input: {text: $text, driver: $driver, dryRun: false, type: HCL}) {
            node {
                extID
            }
        }
    }
    """
        mutation3 = """
    mutation ShareVisualization($fromID: String!) {
        shareVisualization(input: {fromID: $fromID}) {
            success
        }
    }
    """
        mocked_atlas_schema = """
schema "test_schema" {}
table "test_table" {
  schema = schema.test_schema
  column "id" {
    type = int
  }
}
"""
        mocked_responses = [
            json.dumps({"data": {"visualize": {"node": {"hcl": mocked_atlas_schema}}}}),
            json.dumps({"data": {"visualize": {"node": {"extID": "first_extID"}}}}),
            json.dumps({"data": {"shareVisualization": {"success": True}}}),
        ]
        mock_execute = MagicMock(side_effect=mocked_responses)
        mock_client.return_value.execute = mock_execute
        out = StringIO()
        management.call_command("djangoviz", stdout=out)
        sql_statements = (
            'BEGIN;\n--\n-- Create model PriceHistory\n--\nCREATE TABLE "app1_pricehistory" ("id" integer NOT NULL '
            'PRIMARY KEY AUTOINCREMENT, "date" datetime NOT NULL, "price" decimal NOT NULL, "volume" integer unsigned '
            'NOT NULL CHECK ("volume" >= 0));\nCOMMIT;\nBEGIN;\n--\n-- Create model PriceHistory\n--\nCREATE TABLE '
            '"app2_pricehistory" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "date" datetime NOT NULL, '
            '"price" decimal NOT NULL, "volume" integer unsigned NOT NULL CHECK ("volume" >= 0));\nCOMMIT;\n'
        )
        mock_execute.assert_has_calls(
            [
                call(mutation1, {"text": sql_statements, "driver": "SQLITE"}),
                call(mutation2, {"text": mocked_atlas_schema, "driver": "SQLITE"}),
                call(mutation3, {"fromID": "first_extID"}),
            ]
        )

        expected_output = (
            BaseCommand().style.SUCCESS(
                f"Here is a public link to your schema visualization: https://gh.atlasgo.cloud/explore/first_extID"
            )
            + "\n"
        )
        self.assertEquals(out.getvalue(), expected_output)
