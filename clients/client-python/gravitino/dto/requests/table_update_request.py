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

from abc import ABC
from typing import Optional

from dataclasses_json import DataClassJsonMixin

from gravitino.api.rel.types.type import Type
from gravitino.api.rel.table_change import TableChange
from gravitino.dto.rel.expressions.func_expression_dto import FuncExpressionDTO


class TableUpdateRequest(ABC):
    """Base class for table update requests."""

    class RenameTableRequest(DataClassJsonMixin):
        """Request to rename a table."""

        def __init__(self, new_name: str, new_schema_name: Optional[str] = None):
            self._new_name = new_name
            self._new_schema_name = new_schema_name
            self._type = "rename"

    class UpdateTableCommentRequest(DataClassJsonMixin):
        """Request to update table comment."""

        def __init__(self, new_comment: str):
            self._new_comment = new_comment
            self._type = "updateComment"

    class SetTablePropertyRequest(DataClassJsonMixin):
        """Request to set table property."""

        def __init__(self, property_name: str, value: str):
            self._property = property_name
            self._value = value
            self._type = "setProperty"

    class RemoveTablePropertyRequest(DataClassJsonMixin):
        """Request to remove table property."""

        def __init__(self, property_name: str):
            self._property = property_name
            self._type = "removeProperty"

    class AddTableColumnRequest(
        DataClassJsonMixin
    ):  # pylint: disable=too-many-instance-attributes
        """Request to add table column."""

        def __init__(
            self,
            field_name: list[str],
            data_type: Type,
            comment: Optional[str] = None,
            position: Optional[TableChange.ColumnPosition] = None,
            nullable: bool = True,
            auto_increment: bool = False,
            default_value: Optional[FuncExpressionDTO] = None,
        ):
            self._field_name = field_name
            self._data_type = data_type
            self._comment = comment
            self._position = position
            self._nullable = nullable
            self._auto_increment = auto_increment
            self._default_value = default_value
            self._type = "addColumn"

    class RenameTableColumnRequest(DataClassJsonMixin):
        """Request to rename table column."""

        def __init__(self, old_field_name: list[str], new_field_name: str):
            self._old_field_name = old_field_name
            self._new_field_name = new_field_name
            self._type = "renameColumn"

    class UpdateTableColumnDefaultValueRequest(DataClassJsonMixin):
        """Request to update table column default value."""

        def __init__(self, field_name: list[str], new_default_value: FuncExpressionDTO):
            self._field_name = field_name
            self._new_default_value = new_default_value
            self._type = "updateColumnDefaultValue"

    class UpdateTableColumnTypeRequest(DataClassJsonMixin):
        """Request to update table column type."""

        def __init__(self, field_name: list[str], new_data_type: Type):
            self._field_name = field_name
            self._new_data_type = new_data_type
            self._type = "updateColumnType"

    class UpdateTableColumnCommentRequest(DataClassJsonMixin):
        """Request to update table column comment."""

        def __init__(self, field_name: list[str], new_comment: str):
            self._field_name = field_name
            self._new_comment = new_comment
            self._type = "updateColumnComment"

    class UpdateTableColumnPositionRequest(DataClassJsonMixin):
        """Request to update table column position."""

        def __init__(
            self, field_name: list[str], new_position: TableChange.ColumnPosition
        ):
            self._field_name = field_name
            self._new_position = new_position
            self._type = "updateColumnPosition"

    class DeleteTableColumnRequest(DataClassJsonMixin):
        """Request to delete table column."""

        def __init__(self, field_name: list[str], if_exists: bool):
            self._field_name = field_name
            self._if_exists = if_exists
            self._type = "deleteColumn"

    class UpdateTableColumnNullabilityRequest(DataClassJsonMixin):
        """Request to update table column nullability."""

        def __init__(self, field_name: list[str], nullable: bool):
            self._field_name = field_name
            self._nullable = nullable
            self._type = "updateColumnNullability"

    class UpdateColumnAutoIncrementRequest(DataClassJsonMixin):
        """Request to update column auto increment."""

        def __init__(self, field_name: list[str], auto_increment: bool):
            self._field_name = field_name
            self._auto_increment = auto_increment
            self._type = "updateColumnAutoIncrement"
