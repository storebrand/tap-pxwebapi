# ⚠️ This repository is no longer being maintained
Storebrand have moved on from Meltano, and we're therefore no longer maintaining this repository. 

# tap-pxwebapi

`tap-pxwebapi` is a Singer tap for the PxWebApi used by statistical agencies in Norway, Sweden, Denmark and possibly some other countries to disseminate official statistics.

Because the API has no pagination and a max cell count, some tables might be hard to sync. There are some solutions to this that could be implemented in the tap, but most of them are difficult to implement.

Currently, the only way to handle this is to split up a table into multiple streams, using the select functionality to load only a subset of values for each table.

Initial sync might be very difficult for the same reason. Some workarounds are on the way.


Built with the [Meltano Tap SDK](https://sdk.meltano.com) for Singer Taps.

## Installation

Install from GitHub:

```bash
pipx install git+https://github.com/radbrt/tap-pxwebapi.git@main
```

## Capabilities

* `catalog`
* `state`
* `discover`
* `about`
* `stream-maps`
* `schema-flattening`


## Configuration

In order to configure this tap correctly, a general knowledge of the PxWebApi is probably necessary. See the documentation at https://www.ssb.no/api/pxwebapi (or similar pages for the Swedish and Danish statistical agencies).

### Accepted Config Options

| Setting             | Required | Default | Description |
|:--------------------|:--------:|:-------:|:------------|
| base_url            | False    | https://data.ssb.no/api/v0/ | Base API URL |
| tables              | True     | None    | Tables to read |
| stream_maps         | False    | None    | Config object for stream maps capability. For more information check out [Stream Maps](https://sdk.meltano.com/en/latest/stream_maps.html). |
| stream_map_config   | False    | None    | User-defined config values to be used within map expressions. |
| flattening_enabled  | False    | None    | 'True' to enable schema flattening and automatically expand nested properties. |
| flattening_max_depth| False    | None    | The max depth to flatten schemas. |



The tables key contains a list of tables to sync. For columns where only specific values are needed, use the `select` key to filter the request. Columns that are omitted will, depending on the type of column, either return all values or return the top-level value. Details about this can be found in the API documentation: https://www.ssb.no/api/pxwebapi.

example config:

```yaml
    config:
      tables:
      - table_name: example_table
        table_id: '11618'
        select:
        - code: 'Region'
          values:
          - '30'
```

In this example, we sync table 11618 to a destination table `example_table`. We filter the Region column to only request region '30'. The code name is taken from the `code` key of the metadata, and the values from the `values` array. See the table metadata for reference: https://data.ssb.no/api/v0/no/table/11618

```
tap-pxwebapi --about --format=markdown
```

A full list of supported settings and capabilities for this
tap is available by running:

```bash
tap-pxwebapi --about
```

### Configure using environment variables

This Singer tap will automatically import any environment variables within the working directory's
`.env` if the `--config=ENV` is provided, such that config values will be considered if a matching
environment variable is set either in the terminal context or in the `.env` file.

### Source Authentication and Authorization

<!--
Developer TODO: If your tap requires special access on the source system, or any special authentication requirements, provide those here.
-->

## Usage

You can easily run `tap-pxwebapi` by itself or in a pipeline using [Meltano](https://meltano.com/).

### Executing the Tap Directly

```bash
tap-pxwebapi --version
tap-pxwebapi --help
tap-pxwebapi --config CONFIG --discover > ./catalog.json
```

## Developer Resources

Follow these instructions to contribute to this project.

### Initialize your Development Environment

```bash
pipx install poetry
poetry install
```

### Create and Run Tests

Create tests within the `tests` subfolder and
  then run:

```bash
poetry run pytest
```

You can also test the `tap-pxwebapi` CLI interface directly using `poetry run`:

```bash
poetry run tap-pxwebapi --help
```

### Testing with [Meltano](https://www.meltano.com)

_**Note:** This tap will work in any Singer environment and does not require Meltano.
Examples here are for convenience and to streamline end-to-end orchestration scenarios._

<!--
Developer TODO:
Your project comes with a custom `meltano.yml` project file already created. Open the `meltano.yml` and follow any "TODO" items listed in
the file.
-->

Next, install Meltano (if you haven't already) and any needed plugins:

```bash
# Install meltano
pipx install meltano
# Initialize meltano within this directory
cd tap-pxwebapi
meltano install
```

Now you can test and orchestrate using Meltano:

```bash
# Test invocation:
meltano invoke tap-pxwebapi --version
# OR run a test `elt` pipeline:
meltano elt tap-pxwebapi target-jsonl
```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the SDK to
develop your own taps and targets.
