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

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from dataclasses_json import DataClassJsonMixin, config

from gravitino.dto.rel.column_dto import ColumnDTO
from gravitino.dto.rel.distribution_dto import DistributionDTO
from gravitino.dto.rel.indexes.index_dto import IndexDTO
from gravitino.dto.rel.partitioning.partitioning import Partitioning
from gravitino.dto.rel.sort_order_dto import SortOrderDTO
from gravitino.utils.precondition import Precondition


@dataclass
class TableCreateRequest(DataClassJsonMixin):
    """Represents a request to create a table."""

    _name: str = field(metadata=config(field_name="name"))
    _comment: Optional[str] = field(
        default=None,
        metadata=config(field_name="comment", exclude=lambda value: value is None),
    )
    _columns: List[ColumnDTO] = field(metadata=config(field_name="columns"))
    _properties: Optional[Dict[str, str]] = field(
        default=None,
        metadata=config(field_name="properties", exclude=lambda value: value is None),
    )
    _sort_orders: Optional[List[SortOrderDTO]] = field(
        default=None,
        metadata=config(field_name="sortOrders", exclude=lambda value: value is None),
    )
    _distribution: Optional[DistributionDTO] = field(
        default=None,
        metadata=config(field_name="distribution", exclude=lambda value: value is None),
    )
    _partitioning: Optional[List[Partitioning]] = field(
        default=None,
        metadata=config(field_name="partitioning", exclude=lambda value: value is None),
    )
    _indexes: Optional[List[IndexDTO]] = field(
        default=None,
        metadata=config(field_name="indexes", exclude=lambda value: value is None),
    )

    def __init__(
        self,
        name: str,
        comment: Optional[str] = None,
        columns: List[ColumnDTO] = None,
        properties: Optional[Dict[str, str]] = None,
        sort_orders: Optional[List[SortOrderDTO]] = None,
        distribution: Optional[DistributionDTO] = None,
        partitioning: Optional[List[Partitioning]] = None,
        indexes: Optional[List[IndexDTO]] = None,
    ):
        self._name = name
        self._comment = comment
        self._columns = columns or []
        self._properties = properties
        self._sort_orders = sort_orders
        self._distribution = distribution
        self._partitioning = partitioning
        self._indexes = indexes

    def validate(self):
        """Validates the request."""
        Precondition.check_argument(
            self._name is not None and self._name.strip(),
            "name cannot be null or empty",
        )
        Precondition.check_argument(
            self._columns is not None and len(self._columns) > 0,
            "columns cannot be null or empty",
        )