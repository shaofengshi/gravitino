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
from dataclasses import dataclass, field
from typing import Optional

from dataclasses_json import DataClassJsonMixin, config

from gravitino.api.rel.types.type import Type
from gravitino.dto.rel.column_dto import ColumnDTO
from gravitino.dto.rel.expressions.function_expression_dto import FunctionExpressionDTO


class TableUpdateRequest(ABC, DataClassJsonMixin):
    """Base class for table update requests."""

    @dataclass
    class RenameTableRequest(DataClassJsonMixin):
        """Request to rename a table."""

        _type: str = field(
            default="rename", metadata=config(field_name="@type")
        )
        _new_name: str = field(metadata=config(field_name="newName"))
        _new_schema_name: Optional[str] = field(
            default=None,
            metadata=config(field_name="newSchemaName", exclude=lambda value: value is None),
        )

        def __init__(self, new_name: str, new_schema_name: Optional[str] = None):
            self._new_name = new_name
            self._new_schema_name = new_schema_name

    @dataclass
    class UpdateTableCommentRequest(DataClassJsonMixin):
        """Request to update table comment."""

        _type: str = field(
            default="updateComment", metadata=config(field_name="@type")
        )
        _new_comment: str = field(metadata=config(field_name="newComment"))

        def __init__(self, new_comment: str):
            self._new_comment = new_comment

    @dataclass
    class SetTablePropertyRequest(DataClassJsonMixin):
        """Request to set table property."""

        _type: str = field(
            default="setProperty", metadata=config(field_name="@type")
        )
        _property: str = field(metadata=config(field_name="property"))
        _value: str = field(metadata=config(field_name="value"))

        def __init__(self, property_name: str, value: str):
            self._property = property_name
            self._value = value

    @dataclass
    class RemoveTablePropertyRequest(DataClassJsonMixin):
        """Request to remove table property."""

        _type: str = field(
            default="removeProperty", metadata=config(field_name="@type")
        )
        _property: str = field(metadata=config(field_name="property"))

        def __init__(self, property_name: str):
            self._property = property_name

    @dataclass
    class AddTableColumnRequest(DataClassJsonMixin):
        """Request to add table column."""

        _type: str = field(
            default="addColumn", metadata=config(field_name="@type")
        )
        _field_name: list[str] = field(metadata=config(field_name="fieldName"))
        _data_type: Type = field(metadata=config(field_name="dataType"))
        _comment: Optional[str] = field(
            default=None,
            metadata=config(field_name="comment", exclude=lambda value: value is None),
        )
        _position: Optional[ColumnDTO.ColumnPosition] = field(
            default=None,
            metadata=config(field_name="position", exclude=lambda value: value is None),
        )
        _nullable: bool = field(default=True, metadata=config(field_name="nullable"))
        _auto_increment: bool = field(
            default=False, metadata=config(field_name="autoIncrement")
        )
        _default_value: Optional[FunctionExpressionDTO] = field(
            default=None,
            metadata=config(field_name="defaultValue", exclude=lambda value: value is None),
        )

        def __init__(
            self,
            field_name: list[str],
            data_type: Type,
            comment: Optional[str] = None,
            position: Optional[ColumnDTO.ColumnPosition] = None,
            nullable: bool = True,
            auto_increment: bool = False,
            default_value: Optional[FunctionExpressionDTO] = None,
        ):
            self._field_name = field_name
            self._data_type = data_type
            self._comment = comment
            self._position = position
            self._nullable = nullable
            self._auto_increment = auto_increment
            self._default_value = default_value

    @dataclass
    class RenameTableColumnRequest(DataClassJsonMixin):
        """Request to rename table column."""

        _type: str = field(
            default="renameColumn", metadata=config(field_name="@type")
        )
        _old_field_name: list[str] = field(metadata=config(field_name="oldFieldName"))
        _new_field_name: str = field(metadata=config(field_name="newFieldName"))

        def __init__(self, old_field_name: list[str], new_field_name: str):
            self._old_field_name = old_field_name
            self._new_field_name = new_field_name

    @dataclass
    class UpdateTableColumnDefaultValueRequest(DataClassJsonMixin):
        """Request to update table column default value."""

        _type: str = field(
            default="updateColumnDefaultValue", metadata=config(field_name="@type")
        )
        _field_name: list[str] = field(metadata=config(field_name="fieldName"))
        _new_default_value: FunctionExpressionDTO = field(
            metadata=config(field_name="newDefaultValue")
        )

        def __init__(self, field_name: list[str], new_default_value: FunctionExpressionDTO):
            self._field_name = field_name
            self._new_default_value = new_default_value

    @dataclass
    class UpdateTableColumnTypeRequest(DataClassJsonMixin):
        """Request to update table column type."""

        _type: str = field(
            default="updateColumnType", metadata=config(field_name="@type")
        )
        _field_name: list[str] = field(metadata=config(field_name="fieldName"))
        _new_data_type: Type = field(metadata=config(field_name="newDataType"))

        def __init__(self, field_name: list[str], new_data_type: Type):
            self._field_name = field_name
            self._new_data_type = new_data_type

    @dataclass
    class UpdateTableColumnCommentRequest(DataClassJsonMixin):
        """Request to update table column comment."""

        _type: str = field(
            default="updateColumnComment", metadata=config(field_name="@type")
        )
        _field_name: list[str] = field(metadata=config(field_name="fieldName"))
        _new_comment: str = field(metadata=config(field_name="newComment"))

        def __init__(self, field_name: list[str], new_comment: str):
            self._field_name = field_name
            self._new_comment = new_comment

    @dataclass
    class UpdateTableColumnPositionRequest(DataClassJsonMixin):
        """Request to update table column position."""

        _type: str = field(
            default="updateColumnPosition", metadata=config(field_name="@type")
        )
        _field_name: list[str] = field(metadata=config(field_name="fieldName"))
        _new_position: ColumnDTO.ColumnPosition = field(
            metadata=config(field_name="newPosition")
        )

        def __init__(self, field_name: list[str], new_position: ColumnDTO.ColumnPosition):
            self._field_name = field_name
            self._new_position = new_position

    @dataclass
    class DeleteTableColumnRequest(DataClassJsonMixin):
        """Request to delete table column."""

        _type: str = field(
            default="deleteColumn", metadata=config(field_name="@type")
        )
        _field_name: list[str] = field(metadata=config(field_name="fieldName"))
        _if_exists: bool = field(metadata=config(field_name="ifExists"))

        def __init__(self, field_name: list[str], if_exists: bool):
            self._field_name = field_name
            self._if_exists = if_exists

    @dataclass
    class UpdateTableColumnNullabilityRequest(DataClassJsonMixin):
        """Request to update table column nullability."""

        _type: str = field(
            default="updateColumnNullability", metadata=config(field_name="@type")
        )
        _field_name: list[str] = field(metadata=config(field_name="fieldName"))
        _nullable: bool = field(metadata=config(field_name="nullable"))

        def __init__(self, field_name: list[str], nullable: bool):
            self._field_name = field_name
            self._nullable = nullable

    @dataclass
    class UpdateColumnAutoIncrementRequest(DataClassJsonMixin):
        """Request to update column auto increment."""

        _type: str = field(
            default="updateColumnAutoIncrement", metadata=config(field_name="@type")
        )
        _field_name: list[str] = field(metadata=config(field_name="fieldName"))
        _auto_increment: bool = field(metadata=config(field_name="autoIncrement"))

        def __init__(self, field_name: list[str], auto_increment: bool):
            self._field_name = field_name
            self._auto_increment = auto_increment