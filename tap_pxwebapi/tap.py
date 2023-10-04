"""pxwebapi tap class."""

from __future__ import annotations

from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers

# TODO: Import your custom stream types here:
from tap_pxwebapi import streams


class Tappxwebapi(Tap):
    """pxwebapi tap class."""

    name = "tap-pxwebapi"

    # TODO: Update this section with the actual config values you expect:
    config_jsonschema = th.PropertiesList(
        th.Property(
            "base_url",
            th.StringType,
            default="https://data.ssb.no/api/v0/",
            description="Base API URL",
        ),
        th.Property(
            "tables",
            th.ArrayType(
                th.ObjectType(
                    th.Property(
                        "table_id",
                        th.StringType,
                    ),
                    th.Property(
                        "table_name",
                        th.StringType,
                    ),
                    th.Property(
                        "select",
                        th.ArrayType(
                            th.ObjectType(
                                th.Property(
                                    "column",
                                    th.StringType,
                                ),
                                th.Property(
                                    "values",
                                    th.ArrayType(th.StringType),
                                )
                            )
                        )
                    )
                )
            ),
            required=True,
            description="Tables to read",
        )
    ).to_dict()

    def discover_streams(self) -> list[streams.TablesStream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.
        """

        for table in self.config["tables"]:
            yield streams.TablesStream(
                tap=self,
                table_config=table
            )


if __name__ == "__main__":
    Tappxwebapi.cli()
