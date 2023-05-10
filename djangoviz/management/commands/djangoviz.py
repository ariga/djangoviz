import json
from collections import deque
from io import StringIO

from django.apps import apps
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.migrations.loader import MigrationLoader
from graphqlclient import GraphQLClient

HOST = "https://gh.atlasgo.cloud"
API_ENDPOINT = f"{HOST}/api/query"
UI_ENDPOINT = f"{HOST}/explore"
VERSION = "0.0.1"


def _order_migrations_by_dependency():
    connection = connections["default"]
    loader = MigrationLoader(connection)
    graph = loader.graph

    # Get all nodes in the graph
    all_nodes = graph.nodes

    # Generate a plan for all nodes
    plan = graph._generate_plan(nodes=all_nodes, at_end=True)
    return plan


def _get_db_driver():
    database_engine = settings.DATABASES.get("default", {}).get("ENGINE")
    if database_engine is None:
        raise KeyError(...)
    engine_parts = database_engine.split(".")
    if "mysql" in engine_parts:
        return "MYSQL"
    if "postgresql" in engine_parts:
        return "POSTGRES"
    if "sqlite3" in engine_parts:
        return "SQLITE"
    raise Exception(f"Error reading database driver: {database_engine}")


def _share_visualization(client, ext_id):
    mutation = """
    mutation ShareVisualization($fromID: String!) {
        shareVisualization(input: {fromID: $fromID}) {
            success
        }
    }
    """
    variables = {
        "fromID": ext_id,
    }

    result = client.execute(mutation, variables)
    try:
        result_json = json.loads(result)
    except json.JSONDecodeError:
        raise CustomGraphQLError(f"Error in GraphQL query: {result}")
    if "errors" in result_json:
        raise CustomGraphQLError(f"Error in GraphQL query: {result_json['errors']}")
    return result_json.get("data", {}).get("shareVisualization", {}).get("success")


def _visualize_schema(client, schema, driver):
    mutation = """
    mutation Visualize($text: String!, $driver: Driver!) {
        visualize(input: {text: $text, driver: $driver, dryRun: false, type: HCL}) {
            node {
                extID
            }
        }
    }
    """

    variables = {"text": schema, "driver": driver}

    result = client.execute(mutation, variables)
    try:
        result_json = json.loads(result)
    except json.JSONDecodeError:
        raise CustomGraphQLError(f"Error in GraphQL query: {result}")
    if "errors" in result_json:
        raise CustomGraphQLError(f"Error in GraphQL query: {result_json['errors']}")
    ext_id = (
        result_json.get("data", {}).get("visualize", {}).get("node", {}).get("extID")
    )
    return ext_id


def _get_atlas_schema(client, schema, driver):
    mutation = """
        mutation Visualize($text: String!, $driver: Driver!) {
            visualize(input: {text: $text, driver: $driver, dryRun: true, type: SQL}) {
                node {
                    hcl
                }
            }
        }
        """

    variables = {"text": schema, "driver": driver}

    result = client.execute(mutation, variables)
    try:
        result_json = json.loads(result)
    except json.JSONDecodeError:
        raise CustomGraphQLError(f"Error in GraphQL query: {result}")
    if "errors" in result_json:
        raise CustomGraphQLError(f"Error in GraphQL query: {result_json['errors']}")
    schema = result_json.get("data", {}).get("visualize", {}).get("node", {}).get("hcl")
    return schema


class Command(BaseCommand):
    help = "Lists all migration names per app and their content"

    def handle(self, *args, **options):
        db_driver = _get_db_driver()
        migrations = self._get_migrations()
        if migrations == "":
            self.stdout.write(self.style.ERROR("no migrations found"))
            return
        client = GraphQLClient(endpoint=API_ENDPOINT)
        client.inject_token("user-agent", f"djangoviz/{VERSION}")
        try:
            atlas_schema = _get_atlas_schema(client, migrations, db_driver)
            if atlas_schema is None:
                self.stdout.write(self.style.ERROR("atlas schema was not created"))
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR("failed to compute atlas schema"))
            self.stderr.write(str(e))
            return
        try:
            ext_id = _visualize_schema(client, atlas_schema, db_driver)
            if not ext_id:
                self.stdout.write(
                    self.style.ERROR("schema visualization was not created")
                )
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR("failed to visualize schema"))
            self.stderr.write(str(e))
            return
        try:
            if not _share_visualization(client, ext_id):
                self.stdout.write(
                    self.style.ERROR("schema visualization was not shared")
                )
                return
            self.stdout.write(
                self.style.SUCCESS(
                    f"Visualization is shared here: {UI_ENDPOINT}/{ext_id}"
                )
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR("failed to share visualization"))
            self.stderr.write(str(e))
            return

    def _get_migrations(self):
        migration_loader = MigrationLoader(None, ignore_no_migrations=True)
        migration_loader.load_disk()
        migrations = ""
        ordered_migrations = _order_migrations_by_dependency()
        for app_name, migration_name in ordered_migrations:
            try:
                out = StringIO()
                call_command(
                    "sqlmigrate",
                    app_name,
                    migration_name,
                    stdout=out,
                    stderr=StringIO(),
                )
                migrations += out.getvalue()
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"failed to get migration {app_name} {migration_name}"
                    )
                )
        return migrations


class CustomGraphQLError(Exception):
    ...
