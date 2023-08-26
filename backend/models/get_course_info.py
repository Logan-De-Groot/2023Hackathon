import csv
import sys 

csv.field_size_limit(sys.maxsize)

def main_loop():

    with open('degree_major_data.csv', 'r') as csvfile:

        reader = csv.reader(csvfile)
        
        # Read the header (if any)
        header = next(reader)
        print("Header:", header)
        
        # Read the rest of the lines
        for row in reader:
            print(row)
            break

    
main_loop()