import re

def parse_golf_text(text):
    # Splitting the text by occurrences of two newlines followed by a number and a period
    pattern = re.compile(r'\n\n(\d+)\. ')
    sections = pattern.split(text.strip())
    
    # Initialize an empty dictionary for parsed data
    parsed_data = {}
    
    # Skip the first split as it is before the first number and is not needed
    for index in range(1, len(sections), 2):
        image_num = sections[index].strip()  # Get the image number
        description = sections[index + 1].split('\n\n')[0].strip()  # Get the description up to the next double newline
        parsed_data[f'image_{image_num}'] = description

    # Extract overall feedback, if present, after the last numbered section
    overall_feedback = sections[-1].split('\n\n')[-1].strip() if len(sections) > 1 else ""

    return parsed_data, overall_feedback
