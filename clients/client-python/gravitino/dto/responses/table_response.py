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
from typing import Optional

from dataclasses_json import config

from gravitino.dto.rel.table_dto import TableDTO
from gravitino.dto.responses.base_response import BaseResponse


@dataclass
class TableResponse(BaseResponse):
    """Represents a response containing table information."""

    _table: Optional[TableDTO] = field(
        default=None, metadata=config(field_name="table")
    )

    def table(self) -> TableDTO:
        """Returns the table DTO."""
        return self._table

    def validate(self):
        """Validates the response."""
        super().validate()
        if self._table is not None and hasattr(self._table, "validate"):
            self._table.validate()
