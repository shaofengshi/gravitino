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

from typing import Dict, List, Optional

from gravitino.api.catalog import Catalog
from gravitino.api.rel.column import Column
from gravitino.api.rel.expressions.distributions.distribution import Distribution
from gravitino.api.rel.expressions.distributions.distributions import Distributions
from gravitino.api.rel.expressions.sorts.sort_order import SortOrder
from gravitino.api.rel.expressions.transforms.transform import Transform
from gravitino.api.rel.expressions.transforms.transforms import Transforms
from gravitino.api.rel.indexes.index import Index
from gravitino.api.rel.indexes.indexes import Indexes
from gravitino.api.rel.table import Table
from gravitino.api.rel.table_change import TableChange
from gravitino.client.base_schema_catalog import BaseSchemaCatalog
from gravitino.client.relational_table import RelationalTable
from gravitino.dto.audit_dto import AuditDTO
from gravitino.dto.requests.table_create_request import TableCreateRequest
from gravitino.dto.requests.table_update_request import TableUpdateRequest
from gravitino.dto.requests.table_updates_request import TableUpdatesRequest
from gravitino.dto.responses.drop_response import DropResponse
from gravitino.dto.responses.entity_list_response import EntityListResponse
from gravitino.dto.responses.table_response import TableResponse
from gravitino.exceptions.base import (
    IllegalArgumentException,
    NoSuchSchemaException,
    NoSuchTableException,
    TableAlreadyExistsException,
)
from gravitino.exceptions.handlers.table_error_handler import TABLE_ERROR_HANDLER
from gravitino.name_identifier import NameIdentifier
from gravitino.namespace import Namespace
from gravitino.rest.rest_utils import encode_string
from gravitino.utils import HTTPClient


class RelationalCatalog(BaseSchemaCatalog):
    """
    Relational catalog is a catalog implementation that supports relational database like metadata
    operations, for example, schemas and tables list, creation, update and deletion. A Relational
    catalog is under the metalake.
    """

    def __init__(
        self,
        namespace: Namespace,
        name: str,
        catalog_type: Catalog.Type,
        provider: str,
        comment: str = None,
        properties: Dict[str, str] = None,
        audit: AuditDTO = None,
        rest_client: HTTPClient = None,
    ):
        super().__init__(
            catalog_namespace=namespace,
            name=name,
            catalog_type=catalog_type,
            provider=provider,
            comment=comment,
            properties=properties,
            audit=audit,
            rest_client=rest_client,
        )

    def as_table_catalog(self) -> "RelationalCatalog":
        """Return this catalog as a table catalog."""
        return self

    def list_tables(self, namespace: Namespace) -> List[NameIdentifier]:
        """List all the tables under the given Schema namespace.

        Args:
            namespace: The namespace to list the tables under it. This namespace should have 1 level,
                      which is the schema name.

        Returns:
            A list of NameIdentifier of the tables under the given namespace.

        Raises:
            NoSuchSchemaException: if the schema with specified namespace does not exist.
        """
        self._check_table_namespace(namespace)

        full_namespace = self._get_table_full_namespace(namespace)
        resp = self.rest_client.get(
            self._format_table_request_path(full_namespace),
            error_handler=TABLE_ERROR_HANDLER,
        )
        entity_list_response = EntityListResponse.from_json(resp.body, infer_missing=True)
        entity_list_response.validate()

        return [
            NameIdentifier.of(ident.namespace().level(2), ident.name())
            for ident in entity_list_response.identifiers()
        ]

    def load_table(self, ident: NameIdentifier) -> Table:
        """Load the table with specified identifier.

        Args:
            ident: The identifier of the table to load, which should be "schema.table" format.

        Returns:
            The Table with specified identifier.

        Raises:
            NoSuchTableException: if the table with specified identifier does not exist.
        """
        self._check_table_name_identifier(ident)

        full_namespace = self._get_table_full_namespace(ident.namespace())
        resp = self.rest_client.get(
            self._format_table_request_path(full_namespace) + "/" + encode_string(ident.name()),
            error_handler=TABLE_ERROR_HANDLER,
        )
        table_response = TableResponse.from_json(resp.body, infer_missing=True)
        table_response.validate()

        return RelationalTable.from_dto(full_namespace, table_response.table(), self.rest_client)

    def table_exists(self, ident: NameIdentifier) -> bool:
        """Check if a table exists using an NameIdentifier.

        Args:
            ident: A table identifier.

        Returns:
            true If the table exists, false otherwise.
        """
        try:
            self.load_table(ident)
            return True
        except NoSuchTableException:
            return False

    def create_table(
        self,
        ident: NameIdentifier,
        columns: List[Column],
        comment: Optional[str] = None,
        properties: Optional[Dict[str, str]] = None,
        partitioning: Optional[List[Transform]] = None,
        distribution: Optional[Distribution] = None,
        sort_orders: Optional[List[SortOrder]] = None,
        indexes: Optional[List[Index]] = None,
    ) -> Table:
        """Create a new table with specified identifier, columns, comment and properties.

        Args:
            ident: The identifier of the table, which should be "schema.table" format.
            columns: The columns of the table.
            comment: The comment of the table.
            properties: The properties of the table.
            partitioning: The partitioning of the table.
            distribution: The distribution of the table.
            sort_orders: The sort orders of the table.
            indexes: The indexes of the table.

        Returns:
            The created Table.

        Raises:
            NoSuchSchemaException: if the schema with specified namespace does not exist.
            TableAlreadyExistsException: if the table with specified identifier already exists.
        """
        self._check_table_name_identifier(ident)

        # Convert to DTOs
        from gravitino.dto.rel.column_dto import ColumnDTO
        from gravitino.dto.rel.distribution_dto import DistributionDTO
        from gravitino.dto.rel.indexes.index_dto import IndexDTO
        from gravitino.dto.rel.partitioning.partitioning import Partitioning
        from gravitino.dto.rel.sort_order_dto import SortOrderDTO

        column_dtos = [self._to_column_dto(col) for col in columns] if columns else []
        sort_order_dtos = [self._to_sort_order_dto(so) for so in sort_orders] if sort_orders else None
        distribution_dto = self._to_distribution_dto(distribution) if distribution else None
        partitioning_dtos = [self._to_partitioning_dto(p) for p in partitioning] if partitioning else None
        index_dtos = [self._to_index_dto(idx) for idx in indexes] if indexes else None

        req = TableCreateRequest(
            name=ident.name(),
            comment=comment,
            columns=column_dtos,
            properties=properties,
            sort_orders=sort_order_dtos,
            distribution=distribution_dto,
            partitioning=partitioning_dtos,
            indexes=index_dtos,
        )
        req.validate()

        full_namespace = self._get_table_full_namespace(ident.namespace())
        resp = self.rest_client.post(
            self._format_table_request_path(full_namespace),
            json=req,
            error_handler=TABLE_ERROR_HANDLER,
        )
        table_response = TableResponse.from_json(resp.body, infer_missing=True)
        table_response.validate()

        return RelationalTable.from_dto(full_namespace, table_response.table(), self.rest_client)

    def alter_table(self, ident: NameIdentifier, *changes: TableChange) -> Table:
        """Alter the table with specified identifier by applying the changes.

        Args:
            ident: The identifier of the table, which should be "schema.table" format.
            changes: Table changes to apply to the table.

        Returns:
            The altered Table.

        Raises:
            NoSuchTableException: if the table with specified identifier does not exist.
            IllegalArgumentException: if the changes are invalid.
        """
        self._check_table_name_identifier(ident)

        reqs = [self._to_table_update_request(change) for change in changes]
        updates_request = TableUpdatesRequest(reqs)
        updates_request.validate()

        full_namespace = self._get_table_full_namespace(ident.namespace())
        resp = self.rest_client.put(
            self._format_table_request_path(full_namespace) + "/" + encode_string(ident.name()),
            updates_request,
            error_handler=TABLE_ERROR_HANDLER,
        )
        table_response = TableResponse.from_json(resp.body, infer_missing=True)
        table_response.validate()

        return RelationalTable.from_dto(full_namespace, table_response.table(), self.rest_client)

    def drop_table(self, ident: NameIdentifier) -> bool:
        """Drop the table with specified identifier.

        Args:
            ident: The identifier of the table, which should be "schema.table" format.

        Returns:
            true if the table is dropped successfully, false if the table does not exist.
        """
        self._check_table_name_identifier(ident)

        full_namespace = self._get_table_full_namespace(ident.namespace())
        resp = self.rest_client.delete(
            self._format_table_request_path(full_namespace) + "/" + encode_string(ident.name()),
            error_handler=TABLE_ERROR_HANDLER,
        )
        drop_response = DropResponse.from_json(resp.body, infer_missing=True)
        drop_response.validate()
        return drop_response.dropped()

    def purge_table(self, ident: NameIdentifier) -> bool:
        """Purge the table with specified identifier.

        Args:
            ident: The identifier of the table, which should be "schema.table" format.

        Returns:
            true if the table is purged successfully, false if the table does not exist.

        Raises:
            UnsupportedOperationException: if the catalog does not support purging tables.
        """
        self._check_table_name_identifier(ident)

        full_namespace = self._get_table_full_namespace(ident.namespace())
        params = {"purge": "true"}
        resp = self.rest_client.delete(
            self._format_table_request_path(full_namespace) + "/" + encode_string(ident.name()),
            params=params,
            error_handler=TABLE_ERROR_HANDLER,
        )
        drop_response = DropResponse.from_json(resp.body, infer_missing=True)
        drop_response.validate()
        return drop_response.dropped()

    def _format_table_request_path(self, ns: Namespace) -> str:
        """Format the table request path."""
        schema_ns = Namespace.of(ns.level(0), ns.level(1))
        return (
            self.format_schema_request_path(schema_ns)
            + "/"
            + encode_string(ns.level(2))
            + "/tables"
        )

    def _check_table_namespace(self, namespace: Namespace):
        """Check whether the namespace of a table is valid, which should be "schema"."""
        Namespace.check(
            namespace is not None and namespace.length() == 1,
            f"Table namespace must be non-null and have 1 level, the input namespace is {namespace}",
        )

    def _check_table_name_identifier(self, ident: NameIdentifier):
        """Check whether the NameIdentifier of a table is valid."""
        NameIdentifier.check(ident is not None, "NameIdentifier must not be null")
        NameIdentifier.check(
            ident.name() is not None and ident.name().strip(),
            "NameIdentifier name must not be empty",
        )
        self._check_table_namespace(ident.namespace())

    def _get_table_full_namespace(self, table_namespace: Namespace) -> Namespace:
        """Get the full namespace of the table with the given table's short namespace (schema name)."""
        return Namespace.of(
            self._catalog_namespace.level(0), self.name(), table_namespace.level(0)
        )

    def _to_table_update_request(self, change: TableChange) -> TableUpdateRequest:
        """Convert a TableChange to a TableUpdateRequest."""
        if isinstance(change, TableChange.RenameTable):
            return TableUpdateRequest.RenameTableRequest(
                change.new_name(), change.new_schema_name()
            )
        elif isinstance(change, TableChange.UpdateComment):
            return TableUpdateRequest.UpdateTableCommentRequest(change.new_comment())
        elif isinstance(change, TableChange.SetProperty):
            return TableUpdateRequest.SetTablePropertyRequest(change.property(), change.value())
        elif isinstance(change, TableChange.RemoveProperty):
            return TableUpdateRequest.RemoveTablePropertyRequest(change.property())
        elif isinstance(change, TableChange.AddColumn):
            return TableUpdateRequest.AddTableColumnRequest(
                change.field_name(),
                change.data_type(),
                change.comment(),
                change.position(),
                change.nullable(),
                change.auto_increment(),
                change.default_value(),
            )
        elif isinstance(change, TableChange.RenameColumn):
            return TableUpdateRequest.RenameTableColumnRequest(
                change.field_name(), change.new_name()
            )
        elif isinstance(change, TableChange.UpdateColumnDefaultValue):
            return TableUpdateRequest.UpdateTableColumnDefaultValueRequest(
                change.field_name(), change.new_default_value()
            )
        elif isinstance(change, TableChange.UpdateColumnType):
            return TableUpdateRequest.UpdateTableColumnTypeRequest(
                change.field_name(), change.new_data_type()
            )
        elif isinstance(change, TableChange.UpdateColumnComment):
            return TableUpdateRequest.UpdateTableColumnCommentRequest(
                change.field_name(), change.new_comment()
            )
        elif isinstance(change, TableChange.UpdateColumnPosition):
            return TableUpdateRequest.UpdateTableColumnPositionRequest(
                change.field_name(), change.position()
            )
        elif isinstance(change, TableChange.DeleteColumn):
            return TableUpdateRequest.DeleteTableColumnRequest(
                change.field_name(), change.if_exists()
            )
        elif isinstance(change, TableChange.UpdateColumnNullability):
            return TableUpdateRequest.UpdateTableColumnNullabilityRequest(
                change.field_name(), change.nullable()
            )
        elif isinstance(change, TableChange.UpdateColumnAutoIncrement):
            return TableUpdateRequest.UpdateColumnAutoIncrementRequest(
                change.field_name(), change.auto_increment()
            )
        else:
            raise ValueError(f"Unknown change type: {type(change).__name__}")

    def _to_column_dto(self, column: Column):
        """Convert a Column to ColumnDTO."""
        # This is a placeholder - actual implementation would depend on the Column structure
        from gravitino.dto.rel.column_dto import ColumnDTO
        return ColumnDTO(
            _name=column.name(),
            _data_type=column.data_type(),
            _comment=column.comment(),
            _nullable=column.nullable(),
            _auto_increment=column.auto_increment(),
            _default_value=column.default_value(),
        )

    def _to_sort_order_dto(self, sort_order: SortOrder):
        """Convert a SortOrder to SortOrderDTO."""
        from gravitino.dto.rel.sort_order_dto import SortOrderDTO
        return SortOrderDTO()  # Placeholder implementation

    def _to_distribution_dto(self, distribution: Distribution):
        """Convert a Distribution to DistributionDTO."""
        from gravitino.dto.rel.distribution_dto import DistributionDTO
        return DistributionDTO()  # Placeholder implementation

    def _to_partitioning_dto(self, partitioning: Transform):
        """Convert a Transform to Partitioning."""
        from gravitino.dto.rel.partitioning.partitioning import Partitioning
        return Partitioning()  # Placeholder implementation

    def _to_index_dto(self, index: Index):
        """Convert an Index to IndexDTO."""
        from gravitino.dto.rel.indexes.index_dto import IndexDTO
        return IndexDTO()  # Placeholder implementation