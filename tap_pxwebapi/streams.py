"""Stream type classes for tap-pxwebapi."""

from __future__ import annotations

import typing as t
from pathlib import Path
import hashlib
from singer_sdk import typing as th  # JSON Schema typing helpers
from typing import Any, Callable, Iterable
from tap_pxwebapi.client import pxwebapiStream
import requests
from functools import cached_property

# TODO: Delete this is if not using json files for schema definition
SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")
# TODO: - Override `UsersStream` and `GroupsStream` with your own stream definition.
#       - Copy-paste as many times as needed to create multiple stream types.


class TablesStream(pxwebapiStream):
    """Define custom stream."""

    rest_method = "POST"

    primary_keys = ["_sdc_row_hash"]
    replication_key = "Tid"

    def __init__(self, *args, **kwargs):
        """Custom init to store config"""

        self.table_config = kwargs.pop("table_config")
        self.time_items = None

        super().__init__(*args, **kwargs)


    @property
    def url_base(self) -> str:
        return self.config["base_url"]

    @property
    def path(self) -> str:
        """Return API endpoint path string."""
        return f"en/table/{self.table_config['table_id']}"
    
    @property
    def name(self) -> str:
        """Return a human-readable name for this stream."""
        return self.table_config["table_name"]
    
    @staticmethod
    def json_stat2_to_rows(json_stat2):
        rows = []
        dimensions = json_stat2["dimension"]
        values = json_stat2["value"]
        dimension_keys = list(dimensions.keys())
        
        def recursive_build_row(dim_index, current_row):
            if dim_index == len(dimension_keys):
                current_row["value"] = values[len(rows)]
                rows.append(current_row.copy())
                return

            dim_key = dimension_keys[dim_index]
            dim_values = dimensions[dim_key]["category"]["label"]

            for value_key in dim_values:
                current_row[dim_key] = dim_values[value_key]
                recursive_build_row(dim_index + 1, current_row)

        recursive_build_row(0, {})
        return rows

    @staticmethod
    def create_hash_from_dict(d: dict) -> str:
        """Create a hash from the values of all keys in a dictionary except 'value' and 'extracted_time'."""
        hash_object = hashlib.sha256()
        for key in sorted(d.keys()):
            if key not in ["value"]:
                hash_object.update(str(d[key]).encode())
        return hash_object.hexdigest()

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        json_stat2 = response.json()
        # self.logger.info(f"json_stat2: {json_stat2}")
        rows = self.json_stat2_to_rows(json_stat2)

        for i, row in enumerate(rows):
            hash_object = hashlib.sha256()

            row["_sdc_row_hash"] = self.create_hash_from_dict(row)
            yield row


    def prepare_request_payload(
        self, context: dict | None, next_page_token: _TToken | None
    ) -> dict | None:
        """Prepare the data payload for the REST API request."""

        base_payload = {
            "query": [],
              "response": {
                "format": "json-stat2"
            }
        }

        for select in self.table_config.get("select", []):
            column_payload = {
                "code": select["code"],
                "selection": {
                    "filter": "item",
                    "values": select["values"]
                }
            }
            base_payload["query"].append(column_payload)

        last_time = self.get_starting_replication_key_value(context)
        self.logger.info("last_time: " + str(last_time))

        if not last_time:
            return base_payload
        
        self.logger.info("time_items: " + str(self.time_items))
        
        if len(self.time_items) == 1:
            new_times = [item for item in self.time_items[0]["values"] if item > last_time]
            self.logger.info("new_times: " + str(new_times))

            if not new_times:
                # Difficult to abort the stream here, so we just fetch the latest period again
                self.logger.info("No new times, fetching latest period")
                time_payload = {
                    "code": self.time_items[0]["code"],
                    "selection": {
                        "filter": "item",
                        "values": [last_time]
                    }
                }
            else:
                self.logger.info(f"New times found, fetching new times {new_times}")
                time_payload = {
                    "code": self.time_items[0]["code"],
                    "selection": {
                        "filter": "item",
                        "values": new_times
                    }
                }

            base_payload["query"].append(time_payload)

            self.logger.info("payload: " + str(base_payload))

            return base_payload
        


    @cached_property
    def schema(self) -> th.PropertiesList:
        
        r = requests.get(self.url_base + self.path)
        r.raise_for_status()

        time_variable = [item for item in r.json()["variables"] if item.get("time")]
        self.time_items = time_variable

        properties = th.PropertiesList()
        
        for item in r.json()["variables"]:

            properties.append(
                th.Property(
                    item["code"],
                    th.StringType,
                    description=item["text"],
                    required=False,
                )
            )

        properties.append(
            th.Property(
                "value",
                th.NumberType,
                description="Value",
                required=False,
            )
        )

        properties.append(
            th.Property(
                "_sdc_row_hash",
                th.StringType,
                description="Row number",
                required=True
            )
        )

        return properties.to_dict()


    




