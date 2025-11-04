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

import unittest
from unittest.mock import Mock

from gravitino.api.catalog import Catalog
from gravitino.client.dto_converters import DTOConverters
from gravitino.client.relational_catalog import RelationalCatalog
from gravitino.dto.audit_dto import AuditDTO
from gravitino.dto.catalog_dto import CatalogDTO
from gravitino.namespace import Namespace
from gravitino.utils import HTTPClient


class TestRelationalCatalog(unittest.TestCase):
    """Unit tests for RelationalCatalog."""

    def setUp(self):
        self.mock_client = Mock(spec=HTTPClient)
        self.namespace = Namespace.of("test_metalake")
        self.audit = AuditDTO(
            _creator="test_user",
            _create_time="2023-01-01T00:00:00Z",
            _last_modifier="test_user",
            _last_modified_time="2023-01-01T00:00:00Z",
        )

    def test_relational_catalog_creation(self):
        """Test that RelationalCatalog can be created directly."""
        catalog = RelationalCatalog(
            namespace=self.namespace,
            name="test_catalog",
            catalog_type=Catalog.Type.RELATIONAL,
            provider="test_provider",
            comment="Test catalog",
            properties={"key": "value"},
            audit=self.audit,
            rest_client=self.mock_client,
        )

        self.assertIsNotNone(catalog)
        self.assertEqual(catalog.name(), "test_catalog")
        self.assertEqual(catalog.type(), Catalog.Type.RELATIONAL)
        self.assertEqual(catalog.provider(), "test_provider")
        self.assertEqual(catalog.comment(), "Test catalog")
        self.assertEqual(catalog.properties(), {"key": "value"})

    def test_dto_converter_creates_relational_catalog(self):
        """Test that DTOConverters creates RelationalCatalog for RELATIONAL type."""
        catalog_dto = CatalogDTO(
            _name="test_relational_catalog",
            _type=Catalog.Type.RELATIONAL,
            _provider="test_provider",
            _comment="Test relational catalog",
            _properties={"key": "value"},
            _audit=self.audit,
        )

        catalog = DTOConverters.to_catalog(
            "test_metalake", catalog_dto, self.mock_client
        )

        self.assertIsNotNone(catalog)
        self.assertIsInstance(catalog, RelationalCatalog)
        self.assertEqual(catalog.name(), "test_relational_catalog")
        self.assertEqual(catalog.type(), Catalog.Type.RELATIONAL)
        self.assertEqual(catalog.provider(), "test_provider")

    def test_as_table_catalog(self):
        """Test that as_table_catalog returns self."""
        catalog = RelationalCatalog(
            namespace=self.namespace,
            name="test_catalog",
            catalog_type=Catalog.Type.RELATIONAL,
            provider="test_provider",
            audit=self.audit,
            rest_client=self.mock_client,
        )

        table_catalog = catalog.as_table_catalog()
        self.assertIs(table_catalog, catalog)

    def test_namespace_validation(self):
        """Test that namespace validation works correctly."""
        from gravitino.namespace import Namespace
        from gravitino.exceptions.base import IllegalArgumentException

        # Valid namespace (1 level)
        valid_namespace = Namespace.of("schema")
        catalog = RelationalCatalog(
            namespace=self.namespace,
            name="test_catalog",
            catalog_type=Catalog.Type.RELATIONAL,
            provider="test_provider",
            audit=self.audit,
            rest_client=self.mock_client,
        )

        # This should not raise an exception
        catalog._check_table_namespace(valid_namespace)

        # Invalid namespace (0 levels)
        with self.assertRaises(Exception):
            catalog._check_table_namespace(Namespace.empty())

        # Invalid namespace (2 levels)
        with self.assertRaises(Exception):
            catalog._check_table_namespace(Namespace.of("schema", "table"))

    def test_table_identifier_validation(self):
        """Test that table identifier validation works correctly."""
        from gravitino.name_identifier import NameIdentifier
        from gravitino.namespace import Namespace

        catalog = RelationalCatalog(
            namespace=self.namespace,
            name="test_catalog",
            catalog_type=Catalog.Type.RELATIONAL,
            provider="test_provider",
            audit=self.audit,
            rest_client=self.mock_client,
        )

        # Valid identifier
        valid_ident = NameIdentifier.of("schema", "table")
        catalog._check_table_name_identifier(valid_ident)  # Should not raise

        # Invalid identifier (None)
        with self.assertRaises(Exception):
            catalog._check_table_name_identifier(None)

        # Invalid identifier (empty name)
        invalid_ident = NameIdentifier.of("schema", "")
        with self.assertRaises(Exception):
            catalog._check_table_name_identifier(invalid_ident)

    def test_get_table_full_namespace(self):
        """Test that table full namespace is constructed correctly."""
        catalog = RelationalCatalog(
            namespace=self.namespace,
            name="test_catalog",
            catalog_type=Catalog.Type.RELATIONAL,
            provider="test_provider",
            audit=self.audit,
            rest_client=self.mock_client,
        )

        table_namespace = Namespace.of("schema")
        full_namespace = catalog._get_table_full_namespace(table_namespace)

        expected = Namespace.of("test_metalake", "test_catalog", "schema")
        self.assertEqual(full_namespace, expected)

    def test_format_table_request_path(self):
        """Test that table request path is formatted correctly."""
        catalog = RelationalCatalog(
            namespace=self.namespace,
            name="test_catalog",
            catalog_type=Catalog.Type.RELATIONAL,
            provider="test_provider",
            audit=self.audit,
            rest_client=self.mock_client,
        )

        full_namespace = Namespace.of("test_metalake", "test_catalog", "test_schema")
        path = catalog._format_table_request_path(full_namespace)

        expected = "api/metalakes/test_metalake/catalogs/test_catalog/schemas/test_schema/tables"
        self.assertEqual(path, expected)


if __name__ == "__main__":
    unittest.main()
