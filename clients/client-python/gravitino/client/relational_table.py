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

from gravitino.api.rel.column import Column
from gravitino.api.rel.expressions.distributions.distribution import Distribution
from gravitino.api.rel.expressions.sorts.sort_order import SortOrder
from gravitino.api.rel.expressions.transforms.transform import Transform
from gravitino.api.rel.indexes.index import Index
from gravitino.api.rel.table import Table
from gravitino.dto.audit_dto import AuditDTO
from gravitino.dto.rel.table_dto import TableDTO
from gravitino.namespace import Namespace
from gravitino.utils import HTTPClient


class RelationalTable(Table):  # pylint: disable=too-many-instance-attributes
    """
    A relational table implementation that represents a table in a relational catalog.
    """

    def __init__(
        self,
        namespace: Namespace,
        name: str,
        columns: List[Column],
        comment: Optional[str] = None,
        properties: Optional[Dict[str, str]] = None,
        partitioning: Optional[List[Transform]] = None,
        distribution: Optional[Distribution] = None,
        sort_orders: Optional[List[SortOrder]] = None,
        indexes: Optional[List[Index]] = None,
        audit: Optional[AuditDTO] = None,
        rest_client: HTTPClient = None,
    ):
        self._namespace = namespace
        self._name = name
        self._columns = columns or []
        self._comment = comment
        self._properties = properties or {}
        self._partitioning = partitioning or []
        self._distribution = distribution
        self._sort_orders = sort_orders or []
        self._indexes = indexes or []
        self._audit = audit
        self._rest_client = rest_client

    @classmethod
    def from_dto(
        cls,
        namespace: Namespace,
        table_dto: TableDTO,
        rest_client: HTTPClient,
    ) -> "RelationalTable":
        """Create a RelationalTable from a TableDTO."""
        return cls(
            namespace=namespace,
            name=table_dto.name(),
            columns=table_dto.columns(),
            comment=table_dto.comment(),
            properties=table_dto.properties(),
            partitioning=table_dto.partitioning(),
            distribution=table_dto.distribution(),
            sort_orders=table_dto.sort_order(),
            indexes=table_dto.index(),
            audit=table_dto.audit_info(),
            rest_client=rest_client,
        )

    def name(self) -> str:
        """Gets name of the table."""
        return self._name

    def columns(self) -> List[Column]:
        """Gets the columns of the table."""
        return self._columns

    def comment(self) -> Optional[str]:
        """Gets the comment of the table."""
        return self._comment

    def properties(self) -> Dict[str, str]:
        """Gets the properties of the table."""
        return self._properties

    def partitioning(self) -> List[Transform]:
        """Gets the physical partitioning of the table."""
        return self._partitioning

    def sort_order(self) -> List[SortOrder]:
        """Gets the sort order of the table."""
        return self._sort_orders

    def distribution(self) -> Optional[Distribution]:
        """Gets the distribution of the table."""
        return self._distribution

    def index(self) -> List[Index]:
        """Gets the indexes of the table."""
        return self._indexes

    def audit_info(self) -> AuditDTO:
        """Gets the audit information of the table."""
        return self._audit
