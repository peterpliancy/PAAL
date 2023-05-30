import pandas as pd
import os
import datetime
from jinja2 import Template

# Load data from CSV
date_string = datetime.date.today().strftime("%m-%d-%Y")
csv_file = os.path.expanduser("~/Desktop/PAAL/PAAL in Progress/" + date_string + " - Audit/PAAL.csv")
data = pd.read_csv(csv_file)

# Replace 'checkmark', '████', and '✔' with NaN, then drop the columns where all values are NaN
data.replace(['checkmark', '████', '✔'], pd.NA, inplace=True)
data.dropna(axis=1, how='all', inplace=True)

# Preparing data: separating issues for each endpoint and each column
endpoint_tables = {}
for endpoint in data['Endpoint Name'].unique():
    endpoint_data = data[data['Endpoint Name'] == endpoint]
    # Only consider columns where there is at least one non-NA value and it's not 'Time Audit'
    endpoint_data = endpoint_data.dropna(axis=1, how='all').drop(columns=['Time Audit'], errors='ignore')
    endpoint_tables[endpoint] = endpoint_data.to_html(index=False)

column_tables = {}
for column in data.columns[1:]:
    column_data = data[data[column].notna()][['Endpoint Name', column]]
    column_data.index = range(1, len(column_data) + 1)
    column_tables[column] = column_data.to_html(index_names=False)

# HTML template as a string
template_string = """
<html>
<head>
    <style>
        th, td { text-align: left; }
    </style>
</head>
<body>
    <h2>Select Endpoint</h2>
    <select id="endpointSelect" onchange="changeEndpoint()">
        <option selected="true" disabled="disabled">Select An Endpoint To View All Scanned Issues</option>
        {% for endpoint in endpoint_tables.keys() %}
            <option value="{{ endpoint }}">{{ endpoint }}</option>
        {% endfor %}
    </select>
    <div id="endpointTable">{{ endpoint_tables[endpoint_tables.keys()[0]]|safe }}</div>

    <h2>Select Issue</h2>
    <select id="columnSelect" onchange="changeColumn()">
        <option selected="true" disabled="disabled">Select An Issue To View All Affected Endpoints</option>
        {% if endpoint_tables|length > 0 %}
            {% for column in column_tables.keys() %}
                <option value="{{ column }}">{{ column }}</option>
            {% endfor %}
        {% else %}
            <option disabled="disabled">No Endpoints Available</option>
        {% endif %}
    </select>
    <div id="columnTable">{{ column_tables[column_tables.keys()[0]]|safe }}</div>

    <script>
        var endpoint_tables = {{ endpoint_tables|tojson }};
        var column_tables = {{ column_tables|tojson }};

        function changeEndpoint() {
            var endpoint = document.getElementById("endpointSelect").value;
            document.getElementById("endpointTable").innerHTML = endpoint_tables[endpoint];
        }

        function changeColumn() {
            var column = document.getElementById("columnSelect").value;
            document.getElementById("columnTable").innerHTML = column_tables[column];
        }
    </script>
</body>
</html>
"""

template = Template(template_string)

# Render HTML
html = template.render(endpoint_tables=endpoint_tables, column_tables=column_tables)

# Define path to save the report
report_path = os.path.dirname(csv_file)

# Save HTML to a file
with open(os.path.join(report_path, "PAAL.html"), 'w') as f:
    f.write(html)
