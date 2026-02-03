#!/usr/bin/env python3
"""Migration script: SQLite -> MongoDB.

Reads all data from the existing SQLite database and inserts it into MongoDB.
Maps integer IDs to ObjectIds using in-memory dictionaries.

Usage:
    python scripts/migrate_sqlite_to_mongo.py \
        --sqlite-path data/redstone.db \
        --mongodb-uri mongodb://localhost:27017 \
        --db-name redstone_reporter

Order of migration:
    Project -> Epic -> Feature -> TestCaseDefinition -> TestRun -> TestCase (with embedded TestSteps)
"""

import argparse
import asyncio
import sqlite3
import sys
from datetime import datetime
from typing import Dict

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

# Add project root to path
sys.path.insert(0, ".")

from app.models import (
    Project, Epic, Feature, TestCaseDefinition, TestRun, TestCase,
    TestStepEmbed, ALL_DOCUMENT_MODELS
)


def parse_datetime(value):
    """Parse a datetime string from SQLite."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return datetime.utcnow()


async def migrate(sqlite_path: str, mongodb_uri: str, db_name: str):
    """Run the full migration."""
    # Connect to SQLite
    conn = sqlite3.connect(sqlite_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Connect to MongoDB
    client = AsyncIOMotorClient(mongodb_uri)
    db = client[db_name]
    await init_beanie(database=db, document_models=ALL_DOCUMENT_MODELS)

    # ID mapping dictionaries: old int ID -> new ObjectId
    project_map: Dict[int, ObjectId] = {}
    epic_map: Dict[int, ObjectId] = {}
    feature_map: Dict[int, ObjectId] = {}
    definition_map: Dict[int, ObjectId] = {}
    run_map: Dict[int, ObjectId] = {}
    case_map: Dict[int, ObjectId] = {}

    # --- 1. Migrate Projects ---
    print("Migrating Projects...")
    try:
        cursor.execute("SELECT * FROM project")
        rows = cursor.fetchall()
    except sqlite3.OperationalError:
        rows = []
        print("  No 'project' table found, skipping.")

    for row in rows:
        project = Project(
            name=row["name"],
            description=row["description"] if "description" in row.keys() else None,
            created_at=parse_datetime(row["created_at"]) if "created_at" in row.keys() else datetime.utcnow()
        )
        await project.insert()
        project_map[row["id"]] = project.id
    print(f"  Migrated {len(project_map)} projects")

    # --- 2. Migrate Epics ---
    print("Migrating Epics...")
    try:
        cursor.execute("SELECT * FROM epic")
        rows = cursor.fetchall()
    except sqlite3.OperationalError:
        rows = []
        print("  No 'epic' table found, skipping.")

    for row in rows:
        old_project_id = row["project_id"]
        if old_project_id not in project_map:
            print(f"  WARNING: Epic {row['id']} references missing project {old_project_id}, skipping")
            continue
        epic = Epic(
            project_id=project_map[old_project_id],
            name=row["name"],
            description=row["description"] if "description" in row.keys() else None,
            external_ref=row["external_ref"] if "external_ref" in row.keys() else None,
            created_at=parse_datetime(row["created_at"]) if "created_at" in row.keys() else datetime.utcnow()
        )
        await epic.insert()
        epic_map[row["id"]] = epic.id
    print(f"  Migrated {len(epic_map)} epics")

    # --- 3. Migrate Features ---
    print("Migrating Features...")
    try:
        cursor.execute("SELECT * FROM feature")
        rows = cursor.fetchall()
    except sqlite3.OperationalError:
        rows = []
        print("  No 'feature' table found, skipping.")

    for row in rows:
        old_epic_id = row["epic_id"]
        if old_epic_id not in epic_map:
            print(f"  WARNING: Feature {row['id']} references missing epic {old_epic_id}, skipping")
            continue
        feature = Feature(
            epic_id=epic_map[old_epic_id],
            name=row["name"],
            description=row["description"] if "description" in row.keys() else None,
            created_at=parse_datetime(row["created_at"]) if "created_at" in row.keys() else datetime.utcnow()
        )
        await feature.insert()
        feature_map[row["id"]] = feature.id
    print(f"  Migrated {len(feature_map)} features")

    # --- 4. Migrate TestCaseDefinitions ---
    print("Migrating TestCaseDefinitions...")
    try:
        cursor.execute("SELECT * FROM testcasedefinition")
        rows = cursor.fetchall()
    except sqlite3.OperationalError:
        rows = []
        print("  No 'testcasedefinition' table found, skipping.")

    for row in rows:
        old_feature_id = row["feature_id"]
        if old_feature_id not in feature_map:
            print(f"  WARNING: Definition {row['id']} references missing feature {old_feature_id}, skipping")
            continue
        keys = row.keys()
        definition = TestCaseDefinition(
            feature_id=feature_map[old_feature_id],
            title=row["title"],
            description=row["description"] if "description" in keys else None,
            preconditions=row["preconditions"] if "preconditions" in keys else None,
            steps=eval(row["steps"]) if "steps" in keys and row["steps"] else [],
            expected_result=row["expected_result"] if "expected_result" in keys else None,
            priority=row["priority"] if "priority" in keys else "medium",
            is_active=bool(row["is_active"]) if "is_active" in keys else True,
            created_at=parse_datetime(row["created_at"]) if "created_at" in keys else datetime.utcnow(),
            updated_at=parse_datetime(row["updated_at"]) if "updated_at" in keys else datetime.utcnow()
        )
        await definition.insert()
        definition_map[row["id"]] = definition.id
    print(f"  Migrated {len(definition_map)} test case definitions")

    # --- 5. Migrate TestRuns ---
    print("Migrating TestRuns...")
    try:
        cursor.execute("SELECT * FROM testrun")
        rows = cursor.fetchall()
    except sqlite3.OperationalError:
        rows = []
        print("  No 'testrun' table found, skipping.")

    for row in rows:
        keys = row.keys()
        project_id = None
        if "project_id" in keys and row["project_id"] is not None:
            old_pid = row["project_id"]
            project_id = project_map.get(old_pid)

        run = TestRun(
            name=row["name"],
            status=row["status"],
            start_time=parse_datetime(row["start_time"]),
            end_time=parse_datetime(row["end_time"]) if "end_time" in keys else None,
            project_id=project_id
        )
        await run.insert()
        run_map[row["id"]] = run.id
    print(f"  Migrated {len(run_map)} test runs")

    # --- 6. Migrate TestCases (with embedded TestSteps) ---
    print("Migrating TestCases...")
    try:
        cursor.execute("SELECT * FROM testcase")
        case_rows = cursor.fetchall()
    except sqlite3.OperationalError:
        case_rows = []
        print("  No 'testcase' table found, skipping.")

    for row in case_rows:
        old_run_id = row["run_id"]
        if old_run_id not in run_map:
            print(f"  WARNING: TestCase {row['id']} references missing run {old_run_id}, skipping")
            continue

        keys = row.keys()

        # Load steps from teststep table
        steps = []
        try:
            cursor.execute(
                "SELECT * FROM teststep WHERE test_case_id = ? ORDER BY order_index",
                (row["id"],)
            )
            step_rows = cursor.fetchall()
            for s in step_rows:
                steps.append(TestStepEmbed(
                    description=s["description"],
                    status=s["status"],
                    order_index=s["order_index"]
                ))
        except sqlite3.OperationalError:
            pass  # No teststep table

        definition_id = None
        if "definition_id" in keys and row["definition_id"] is not None:
            old_def_id = row["definition_id"]
            definition_id = definition_map.get(old_def_id)

        case = TestCase(
            run_id=run_map[old_run_id],
            name=row["name"],
            status=row["status"],
            duration=row["duration"] if "duration" in keys else None,
            error_message=row["error_message"] if "error_message" in keys else None,
            error_stack=row["error_stack"] if "error_stack" in keys else None,
            screenshot_path=row["screenshot_path"] if "screenshot_path" in keys else None,
            created_at=parse_datetime(row["created_at"]) if "created_at" in keys else datetime.utcnow(),
            definition_id=definition_id,
            steps=steps
        )
        await case.insert()
        case_map[row["id"]] = case.id
    print(f"  Migrated {len(case_map)} test cases")

    # --- Summary ---
    print("\n--- Migration Summary ---")
    print(f"  Projects:            {len(project_map)}")
    print(f"  Epics:               {len(epic_map)}")
    print(f"  Features:            {len(feature_map)}")
    print(f"  TestCaseDefinitions: {len(definition_map)}")
    print(f"  TestRuns:            {len(run_map)}")
    print(f"  TestCases:           {len(case_map)}")
    print("Migration completed successfully!")

    conn.close()
    client.close()


def main():
    parser = argparse.ArgumentParser(description="Migrate SQLite data to MongoDB")
    parser.add_argument(
        "--sqlite-path",
        default="data/redstone.db",
        help="Path to SQLite database file (default: data/redstone.db)"
    )
    parser.add_argument(
        "--mongodb-uri",
        default="mongodb://localhost:27017",
        help="MongoDB connection URI (default: mongodb://localhost:27017)"
    )
    parser.add_argument(
        "--db-name",
        default="redstone_reporter",
        help="MongoDB database name (default: redstone_reporter)"
    )
    args = parser.parse_args()

    asyncio.run(migrate(args.sqlite_path, args.mongodb_uri, args.db_name))


if __name__ == "__main__":
    main()
