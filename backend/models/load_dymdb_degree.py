import boto3
import csv
import dotenv
# Initialize a session using Amazon DynamoDB
session = boto3.session.Session(region_name='ap-southeast-2', aws_secret_access_key=dotenv.get_key('.env', 'AWS_SECRET_ACCESS_KEY'), aws_access_key_id=dotenv.get_key('.env', 'AWS_ACCESS_KEY_ID'))
dynamodb = session.resource('dynamodb')
table_list = dynamodb.tables.all()
print(table_list)
for table in table_list:
    print(table.name)
# Specify your DynamoDB table
table = dynamodb.Table('degree')

# Open your CSV file
with open('table_data.csv', 'r') as csv_file:
    csv_reader = csv.reader(csv_file)

    items = []
    seen_degrees = []
    for index, row in enumerate(csv_reader):
        if index == 0:
            continue
        line = row[3]
        line = line.split(",")[-1]

        major_code = line.split("=")[-1]

        core_degree = major_code[-4:]


        degree = row[0]
        major = row[2]
        url = row [3]
        degree_type = row[4]

        item = {
            'degree': core_degree,
            'degree_title': degree,
            'url': url,
            'degree_type': degree_type
        }
        if core_degree not in seen_degrees:
            seen_degrees.append(core_degree)
            items.append(item)
    
    with table.batch_writer() as batch:
        for item in items:
            batch.put_item(Item=item)
            print("100 items done")
            items = []
 

print("CSV data loaded into DynamoDB table!")
