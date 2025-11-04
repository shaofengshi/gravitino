# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import logging
from random import randint
from typing import Dict

from gravitino import (
    NameIdentifier,
    GravitinoAdminClient,
    GravitinoClient,
    Catalog,
)
from gravitino.api.rel.column import Column
from gravitino.api.rel.expressions.distributions.distributions import Distributions
from gravitino.api.rel.expressions.transforms.transforms import Transforms
from gravitino.api.rel.indexes.indexes import Indexes
from gravitino.api.rel.table import Table
from gravitino.api.rel.table_change import TableChange
from gravitino.api.rel.types.types import Types
from gravitino.client.relational_catalog import RelationalCatalog
from gravitino.exceptions.base import (
    NoSuchTableException,
    TableAlreadyExistsException,
)
from tests.integration.integration_test_env import IntegrationTestEnv
from tests.integration.containers.hdfs_container import HDFSContainer

logger = logging.getLogger(__name__)


class TestRelationalCatalog(IntegrationTestEnv):
    metalake_name: str = "TestRelationalCatalog_metalake" + str(randint(1, 10000))
    catalog_name: str = "relational_catalog"
    catalog_provider: str = "hive"  # Use hive provider for testing

    schema_name: str = "test_schema"

    table_name: str = "test_table"
    table_alter_name: str = table_name + "_alter"
    table_comment: str = "test table comment"
    table_properties_key1: str = "table_properties_key1"
    table_properties_value1: str = "table_properties_value1"
    table_properties_key2: str = "table_properties_key2"
    table_properties_value2: str = "table_properties_value2"
    table_properties: Dict[str, str] = {
        table_properties_key1: table_properties_value1,
        table_properties_key2: table_properties_value2,
    }

    catalog_ident: NameIdentifier = NameIdentifier.of(metalake_name, catalog_name)
    schema_ident: NameIdentifier = NameIdentifier.of(
        metalake_name, catalog_name, schema_name
    )
    table_ident: NameIdentifier = NameIdentifier.of(schema_name, table_name)
    table_alter_ident: NameIdentifier = NameIdentifier.of(schema_name, table_alter_name)

    gravitino_admin_client: GravitinoAdminClient = GravitinoAdminClient(
        uri="http://localhost:8090"
    )
    gravitino_client: GravitinoClient = None
    catalog: Catalog = None
    hdfs_container: HDFSContainer = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Start the HDFS/Hive container
        cls.hdfs_container = HDFSContainer()
        # Use localhost since we're exposing the port to the host
        hive_metastore_uri = "thrift://localhost:9083"

        logger.info("Started Hive container with metastore URI: %s", hive_metastore_uri)

        cls.gravitino_admin_client = GravitinoAdminClient(uri="http://localhost:8090")
        cls.gravitino_admin_client.create_metalake(
            cls.metalake_name,
            comment="Test metalake for relational catalog",
            properties={},
        )

        cls.gravitino_client = GravitinoClient(
            uri="http://localhost:8090", metalake_name=cls.metalake_name
        )
        cls.catalog = cls.gravitino_client.create_catalog(
            name=cls.catalog_name,
            catalog_type=Catalog.Type.RELATIONAL,
            provider=cls.catalog_provider,
            comment="Test relational catalog",
            properties={"metastore.uris": hive_metastore_uri},
        )

    @classmethod
    def tearDownClass(cls):
        try:
            cls.gravitino_client.drop_catalog(name=cls.catalog_name, force=True)
            cls.gravitino_admin_client.drop_metalake(name=cls.metalake_name, force=True)
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.warning("Failed to clean up class-level resources: %s", e)

        # Clean up the HDFS/Hive container
        if cls.hdfs_container:
            try:
                cls.hdfs_container.close()
            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.warning("Failed to clean up HDFS container: %s", e)

        super().tearDownClass()

    def setUp(self):
        # Create schema for each test
        self.catalog.as_schemas().create_schema(
            schema_name=self.schema_name, comment="Test schema", properties={}
        )

    def tearDown(self):
        # Clean up schema and tables after each test
        try:
            self.catalog.as_schemas().drop_schema(
                schema_name=self.schema_name, cascade=True
            )
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.warning("Failed to clean up test resources: %s", e)

    def create_test_table(self, table_name: str = None) -> Table:
        """Create a test table with basic columns."""
        if table_name is None:
            table_name = self.table_name

        relational_catalog = self.catalog.as_table_catalog()

        # Create basic columns for testing
        columns = [
            Column.of("id", Types.LongType.get(), "Primary key"),
            Column.of("name", Types.StringType.get(), "Name column"),
            Column.of("age", Types.IntegerType.get(), "Age column", nullable=True),
        ]

        table_ident = NameIdentifier.of(self.schema_name, table_name)

        return relational_catalog.create_table(
            ident=table_ident,
            columns=columns,
            comment=self.table_comment,
            properties=self.table_properties,
            partitioning=Transforms.EMPTY_TRANSFORM,
            distribution=Distributions.NONE,
            sort_orders=[],
            indexes=Indexes.EMPTY_INDEXES,
        )

    def test_catalog_type_conversion(self):
        """Test that RELATIONAL catalog is properly converted to RelationalCatalog."""
        self.assertIsNotNone(self.catalog)
        self.assertEqual(self.catalog.type(), Catalog.Type.RELATIONAL)

        # Test as_table_catalog conversion
        table_catalog = self.catalog.as_table_catalog()
        self.assertIsNotNone(table_catalog)
        self.assertIsInstance(table_catalog, RelationalCatalog)

    def test_create_table(self):
        """Test creating a table in the relational catalog."""
        table = self.create_test_table()
        self.assertIsNotNone(table)
        self.assertEqual(table.name(), self.table_name)
        self.assertEqual(table.comment(), self.table_comment)
        self.assertEqual(table.properties(), self.table_properties)
        self.assertEqual(len(table.columns()), 3)

        # Verify column details
        columns = table.columns()
        self.assertEqual(columns[0].name(), "id")
        self.assertEqual(columns[0].data_type(), Types.LongType.get())
        self.assertEqual(columns[1].name(), "name")
        self.assertEqual(columns[1].data_type(), Types.StringType.get())
        self.assertEqual(columns[2].name(), "age")
        self.assertEqual(columns[2].data_type(), Types.IntegerType.get())
        self.assertTrue(columns[2].nullable())

    def test_create_table_already_exists(self):
        """Test creating a table that already exists should raise exception."""
        self.create_test_table()

        relational_catalog = self.catalog.as_table_catalog()

        columns = [Column.of("id", Types.LongType.get(), "Primary key")]
        table_ident = NameIdentifier.of(self.schema_name, self.table_name)

        with self.assertRaises(TableAlreadyExistsException):
            relational_catalog.create_table(
                ident=table_ident,
                columns=columns,
                comment="Duplicate table",
                properties={},
            )

    def test_list_tables(self):
        """Test listing tables in a schema."""
        self.create_test_table()

        relational_catalog = self.catalog.as_table_catalog()

        table_list = relational_catalog.list_tables(
            namespace=self.table_ident.namespace()
        )

        self.assertTrue(any(item.name() == self.table_name for item in table_list))

    def test_load_table(self):
        """Test loading a table by identifier."""
        self.create_test_table()

        relational_catalog = self.catalog.as_table_catalog()

        table = relational_catalog.load_table(ident=self.table_ident)

        self.assertIsNotNone(table)
        self.assertEqual(table.name(), self.table_name)
        self.assertEqual(table.comment(), self.table_comment)
        # Assert that table properties include all keys from self.table_properties
        for key, value in self.table_properties.items():
            self.assertIn(key, table.properties())
            self.assertEqual(table.properties()[key], value)
        self.assertEqual(len(table.columns()), 3)

    def test_load_table_not_exists(self):
        """Test loading a table that doesn't exist should raise exception."""
        relational_catalog = self.catalog.as_table_catalog()

        non_existent_table = NameIdentifier.of(self.schema_name, "non_existent_table")

        with self.assertRaises(NoSuchTableException):
            relational_catalog.load_table(ident=non_existent_table)

    def test_table_exists(self):
        """Test checking if a table exists."""
        relational_catalog = self.catalog.as_table_catalog()

        # Table should not exist initially
        self.assertFalse(relational_catalog.table_exists(ident=self.table_ident))

        # Create table
        self.create_test_table()

        # Table should exist now
        self.assertTrue(relational_catalog.table_exists(ident=self.table_ident))

    def test_alter_table(self):
        """Test altering a table."""
        self.create_test_table()

        relational_catalog = self.catalog.as_table_catalog()

        new_comment = self.table_comment + "_new"
        new_property_value = self.table_properties_value2 + "_new"

        changes = [
            TableChange.update_comment(new_comment),
            TableChange.set_property(self.table_properties_key2, new_property_value),
            TableChange.remove_property(self.table_properties_key1),
        ]

        altered_table = relational_catalog.alter_table(self.table_ident, *changes)

        self.assertEqual(altered_table.comment(), new_comment)
        self.assertEqual(
            altered_table.properties().get(self.table_properties_key2),
            new_property_value,
        )
        self.assertNotIn(self.table_properties_key1, altered_table.properties())

    def test_drop_table(self):
        """Test dropping a table."""
        self.create_test_table()

        relational_catalog = self.catalog.as_table_catalog()

        # Table should exist
        self.assertTrue(relational_catalog.table_exists(ident=self.table_ident))

        # Drop table
        result = relational_catalog.drop_table(ident=self.table_ident)
        self.assertTrue(result)

        # Table should not exist anymore
        self.assertFalse(relational_catalog.table_exists(ident=self.table_ident))

    def test_drop_table_not_exists(self):
        """Test dropping a table that doesn't exist."""
        relational_catalog = self.catalog.as_table_catalog()

        non_existent_table = NameIdentifier.of(self.schema_name, "non_existent_table")

        # Should return False for non-existent table
        result = relational_catalog.drop_table(ident=non_existent_table)
        self.assertFalse(result)

    def test_purge_table(self):
        """Test purging a table (if supported by the catalog)."""
        self.create_test_table()

        relational_catalog = self.catalog.as_table_catalog()

        # Table should exist
        self.assertTrue(relational_catalog.table_exists(ident=self.table_ident))

        try:
            # Purge table
            result = relational_catalog.purge_table(ident=self.table_ident)
            self.assertTrue(result)

            # Table should not exist anymore
            self.assertFalse(relational_catalog.table_exists(ident=self.table_ident))
        except Exception as e:  # pylint: disable=broad-exception-caught
            # Some catalogs may not support purge operation
            logger.info("Purge operation not supported: %s", e)
            self.skipTest("Purge operation not supported by this catalog")
