import json
import responses
from tap_pxwebapi.tap import Tappxwebapi
import re
SAMPLE_CONFIG = {
    "tables": [
        {
            "table_name": "test_table",
            "table_id": "13861",
            "select": [
                {
                    "code": "NACE2007",
                    "values": ["A-Z","A","B","C"]
                }
            ]
        }
    ],
}

# SAMPLE_REQUEST = {
#     "query": [
#       {
#         "code": "NACE2007",
#         "selection": {
#           "filter": "item",
#           "values": ["A-Z","A","B","C"]
#         }
#       },
#       {
#         "code": "Tid",
#         "selection": {
#           "filter": "item",
#           "values": ["2016","2017","2018","2019","2020","2021","2022"]
#         }
#       }
#     ],
#     "response": {
#       "format": "json-stat2"
#     }
#   }

SCHEMA_RESPONSE_TXT = open(
    "tests/schema_responses/13861.json"
).read()

DATA_RESPONSE_TXT = open(
    "tests/data_responses/13861.json"
).read()

SCHEMA_RESPONSE = json.loads(SCHEMA_RESPONSE_TXT)
DATA_RESPONSE = json.loads(DATA_RESPONSE_TXT)


@responses.activate
def test_stuff(capsys):

    responses.add_callback(
        responses.POST,
        re.compile(r"https://data.ssb.no/api/v0/en/table/13861"),
        callback=lambda _: (200, {}, DATA_RESPONSE_TXT),
    )

    schema = responses.add(
        responses.GET,
        "https://data.ssb.no/api/v0/en/table/13861",
        json=SCHEMA_RESPONSE,
        status=200
    )

    tap1 = Tappxwebapi(config=SAMPLE_CONFIG)
    _ = tap1.streams["test_table"].sync(None)

    captured = capsys.readouterr()
    all_stdout = captured.out.strip()
    stdout_parts = all_stdout.split("\n")

    json_messages = [json.loads(line) for line in stdout_parts]
    data_records = [msg for msg in json_messages if msg.get("type") == "RECORD"]
    schema_records = [msg for msg in json_messages if msg.get("type") == "SCHEMA"]

    assert len(data_records) == 4*2*7
    assert schema.call_count == 1
