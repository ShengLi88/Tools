import struct
from itertools import chain, repeat
import pyodbc
from azure.identity import AzureCliCredential
import csv

def get_azure_token():
    credential = AzureCliCredential()
    token_object = credential.get_token("https://database.windows.net//.default")
    token_as_bytes = bytes(token_object.token, "UTF-8")
    encoded_bytes = bytes(chain.from_iterable(zip(token_as_bytes, repeat(0))))
    return struct.pack("<i", len(encoded_bytes)) + encoded_bytes

def connect_to_db():
    sql_endpoint = "gjamxl5dmx2uxcko3nno57teoe-jpj7zafdbg2ebjyavlqztppakq.datawarehouse.fabric.microsoft.com"
    database = "BronzeRawDataWarehouse"
    connection_string = f"Driver={{ODBC Driver 18 for SQL Server}};Server={sql_endpoint},1433;Database={database};Encrypt=Yes;TrustServerCertificate=No"
    attrs_before = {1256: get_azure_token()}
    return pyodbc.connect(connection_string, attrs_before=attrs_before)

def export_to_csv(data, columns, filename='query_results.csv'):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(columns)   # Write header
        writer.writerows(data)     # Write data rows
    print(f"Results exported to {filename}")

# SQL Queries
query1 = """
SELECT *
FROM [BronzeRawDataWarehouse].[dbo].[measurements_series] ms
WHERE ms.timestamp > '2025-04-09'
ORDER BY ms.timestamp DESC
"""

query2 = """
SELECT ms.timestamp, msv.id AS seq, ms.dut_sn, ms.dut_pn, ms.id, msv.value
FROM [BronzeRawDataWarehouse].[dbo].[measurements_series] ms
INNER HASH JOIN [BronzeRawDataWarehouse].[dbo].[measurements_series_values] msv
    ON ms.timestamp = msv.measurement_timestamp
    AND ms.dut_sn = msv.dut_sn
WHERE (ms.id = 'HeatingSeriesPowerCreatedTestSystem' OR ms.id = 'HeatingSeriesPowerConsumedTestSystem')
    AND ms.timestamp > '2025-04-09'
    AND ms.dut_pn = '7593-9908-1302'
ORDER BY ms.timestamp ASC, msv.id ASC
OPTION (HASH JOIN)
"""

query3 = """
SELECT ms.timestamp, msv.id AS seq, ms.dut_sn, ms.dut_pn, ms.id, msv.value
FROM [BronzeRawDataWarehouse].[dbo].[measurements_series] ms
INNER HASH JOIN [BronzeRawDataWarehouse].[dbo].[measurements_series_values] msv
    ON ms.timestamp = msv.measurement_timestamp
    AND ms.dut_sn = msv.dut_sn
WHERE (ms.id = 'HeatingSeriesPowerCreatedTestSystem' OR ms.id = 'HeatingSeriesPowerConsumedTestSystem')
    AND ms.timestamp > '2025-03-09'
ORDER BY ms.timestamp ASC, msv.id ASC
OPTION (HASH JOIN)
"""

# Execute Query and Export Results
connection = connect_to_db()
cursor = connection.cursor()
cursor.execute(query3)
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
export_to_csv(rows, columns)

# Close Connection
cursor.close()
connection.close()