import re
import csv

def dms_to_decimal(dms_string):
    """
    Convert degrees, minutes, seconds to decimal degrees.
    Handles various quote formats: ', '', ", ""
    """
    if not dms_string or dms_string.strip() == '':
        return None
    
    # Clean up the string
    dms_string = dms_string.strip()
    
    # Pattern to match different formats:
    # 33°47'40''N (double single quotes for seconds)
    # 32°19'12.8"N (double quote for seconds)
    patterns = [
        r"(\d+)°(\d+)'([\d.]+)''([NSEW])",  # Double single quotes
        r"(\d+)°(\d+)'([\d.]+)\"([NSEW])",  # Double quote
        r"(\d+)°(\d+)'([\d.]+)'([NSEW])",   # Single quote
    ]
    
    match = None
    for pattern in patterns:
        match = re.search(pattern, dms_string)
        if match:
            break
    
    if not match:
        print(f"Could not parse: {dms_string}")
        return None
    
    degrees = int(match.group(1))
    minutes = int(match.group(2))
    seconds = float(match.group(3))
    direction = match.group(4)
    
    # Convert to decimal
    decimal = degrees + minutes/60 + seconds/3600
    
    # Make negative for South and West
    if direction in ['S', 'W']:
        decimal = -decimal
    
    return round(decimal, 8)

def convert_coordinates_file(input_file, output_file):
    """
    Convert a CSV file of DMS coordinates to decimal format.
    """
    converted_coords = []
    
    with open(input_file, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter='\t')
        header = next(reader)  # Skip header
        
        for row in reader:
            if len(row) >= 2 and row[0].strip() and row[1].strip():
                lat_dms = row[0].strip()
                lng_dms = row[1].strip()
                
                lat_decimal = dms_to_decimal(lat_dms)
                lng_decimal = dms_to_decimal(lng_dms)
                
                if lat_decimal is not None and lng_decimal is not None:
                    converted_coords.append([lat_decimal, lng_decimal])
    
    # Write to output file
    with open(output_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Latitude', 'Longitude'])
        writer.writerows(converted_coords)
    
    return converted_coords

def convert_coordinate_string(lat_dms, lng_dms):
    """
    Convert individual coordinate strings to decimal.
    """
    lat_decimal = dms_to_decimal(lat_dms)
    lng_decimal = dms_to_decimal(lng_dms)
    return lat_decimal, lng_decimal

def convert_firetower_csv(input_file, output_file=None):
    """
    Convert the miss-firetower.csv file coordinates from DMS to decimal format.
    
    Args:
        input_file: Path to the input CSV file
        output_file: Path to the output CSV file. If None, will overwrite the input file.
    """
    if output_file is None:
        output_file = input_file
    
    with open(input_file, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        
        rows = []
        conversion_count = 0
        error_count = 0
        
        for row in reader:
            # Convert latitude
            if row['latitude'] and row['latitude'].strip():
                lat_decimal = dms_to_decimal(row['latitude'].strip())
                if lat_decimal is not None:
                    row['latitude'] = str(lat_decimal)
                    conversion_count += 1
                else:
                    print(f"Warning: Could not convert latitude for {row['objectid']}: {row['latitude']}")
                    error_count += 1
            
            # Convert longitude
            if row['longitude'] and row['longitude'].strip():
                lng_decimal = dms_to_decimal(row['longitude'].strip())
                if lng_decimal is not None:
                    row['longitude'] = str(lng_decimal)
                    conversion_count += 1
                else:
                    print(f"Warning: Could not convert longitude for {row['objectid']}: {row['longitude']}")
                    error_count += 1
            
            rows.append(row)
    
    # Write the converted data to output file
    with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"Conversion complete!")
    print(f"Successfully converted {conversion_count} coordinate values")
    print(f"Errors encountered: {error_count}")
    print(f"Output saved to: {output_file}")
    
    return rows

# Example usage and direct processing:
if __name__ == "__main__":
    # Convert the miss-firetower.csv file
    input_file = "_data/miss-firetower.csv"
    output_file = "_data/miss-firetower-decimal.csv"
    
    print("Converting miss-firetower.csv coordinates to decimal format...")
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    print()
    
    try:
        converted_data = convert_firetower_csv(input_file, output_file)
        
        # Show a few examples of the conversion
        print("\nSample conversions (first 5 rows):")
        for i, row in enumerate(converted_data[:5]):
            if row['latitude'] and row['longitude']:
                print(f"{row['objectid']}: {row['latitude']}, {row['longitude']}")
        
    except FileNotFoundError:
        print(f"Error: Could not find {input_file}")
        print("Make sure you're running this script from the correct directory.")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*50)
    
    # Test with sample coordinates for verification
    test_coords = [
        ("33°47'40''N", "89°05'27''W"),
        ("33°08'03''N", "88°51'07''W"),
        ("32°19'12.8\"N", "89°40'01.0\"W")
    ]
    
    print("Sample conversions for verification:")
    for lat_dms, lng_dms in test_coords:
        lat_dec, lng_dec = convert_coordinate_string(lat_dms, lng_dms)
        print(f"{lat_dms} {lng_dms} → {lat_dec}, {lng_dec}")