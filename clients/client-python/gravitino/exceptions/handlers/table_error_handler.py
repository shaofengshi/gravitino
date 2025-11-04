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

from gravitino.exceptions.base import (
    IllegalArgumentException,
    NoSuchSchemaException,
    NoSuchTableException,
    TableAlreadyExistsException,
)
from gravitino.exceptions.handlers.error_handler import ErrorHandler


class TableErrorHandler(ErrorHandler):
    """Error handler for table operations."""

    def handle(self, error_response):
        """Handle table-related errors."""
        error_type = error_response.type()
        error_message = error_response.message()

        if error_type == "NoSuchSchemaException":
            raise NoSuchSchemaException(error_message)
        if error_type == "NoSuchTableException":
            raise NoSuchTableException(error_message)
        if error_type == "TableAlreadyExistsException":
            raise TableAlreadyExistsException(error_message)
        if error_type == "IllegalArgumentException":
            raise IllegalArgumentException(error_message)

        super().handle(error_response)


# Global instance
TABLE_ERROR_HANDLER = TableErrorHandler()
