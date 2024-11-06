import re

def parse_golf_text(text):
    pattern = re.compile(r'\n\n(\d+)\. ')
    sections = pattern.split(text.strip())
    
    parsed_data = {}
    swing_phases = {}
    recommendations = []
    
    for index in range(1, len(sections), 2):
        image_num = sections[index].strip()
        content = sections[index + 1].strip()
        
        phase_match = re.search(r'^(Setup|Backswing|Downswing|Impact|Follow-through):', content)
        if phase_match:
            phase = phase_match.group(1).lower().replace('-', '_')
            swing_phases[phase] = content[len(phase_match.group(0)):].strip()
        else:
            parsed_data[f'image_{image_num}'] = content
        
        rec_matches = re.findall(r'Recommendation:?\s*(.*?)(?:\n|$)', content, re.IGNORECASE)
        recommendations.extend(rec_matches)

    overall_feedback = sections[-1].split('\n\n')[-1].strip() if len(sections) > 1 else ""

    return {
        'swing_analysis': parsed_data,
        'swing_phases': swing_phases,
        'recommendations': recommendations,
        'overall_feedback': overall_feedback
    }