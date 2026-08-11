import llm
import json

def parse_text(model, website_text, tags):

    if len(website_text) > 5_000:
        return 'LENGTH_LIMIT_EXCEEDED'

    tag_lines = ''
    for tag in tags.keys():
        tag_lines += f'- {tag}={tags[tag]}\n'

    prompt = f"""You are an information extraction system.

Your task is to determine the regular opening hours of exactly one OpenStreetMap venue from the website text.

The venue has the following OpenStreetMap tags:

{tag_lines}

Instructions:

1. The website may contain information about multiple locations, food trucks, catering, delivery services, events, or businesses.
   Only extract opening hours that clearly belong to the venue matching the OpenStreetMap tags.

2. Find the regular weekly opening hours.
   Ignore:
   - holiday hours
   - temporary changes
   - event schedules
   - reservation times
   - delivery hours
   - kitchen hours
   - breakfast/lunch specials
   - opening dates
   - "today's hours" unless the full weekly schedule is given

3. Convert the extracted schedule into valid OpenStreetMap opening_hours syntax.

4. Every day of the week must be accounted for.
   Days when the venue is closed must be written using "off".
   Example:
   Mo-Fr 11:00-14:00; Sa-Su off

5. If any guessing would be required, return UNSURE.
   This includes:
   - no opening hours found
   - multiple conflicting schedules
   - multiple possible matching venues
   - incomplete weekly schedule
   - uncertain conversion to OSM syntax
   - indications that the venue has permanently closed

6. Think through the extraction internally, but DO NOT output your reasoning.

Output requirements:

- Output exactly ONE line.
- The line must contain either:
    - a valid OpenStreetMap opening_hours string
    - UNSURE
- Do not output any explanation or additional text.

Website text:

{website_text}
"""
    model = llm.get_model(model)
    response = model.prompt(prompt)
    return response.text()

if __name__ == '__main__':
    website_text = '''
        TAKE AWAYMENU
        Some text describing the restaurant.
        Öffnungszeiten
        Montag - Samstag
        11:00- 22:00 Uhr
        Sonntag  12:00 - 22:00 Uhr
        Zollstrasse 56
        8005 Zürich
    '''
    model = 'openrouter/qwen/qwen3.8-max'
    tags = {
        'amenity': 'restaurant',
        'wheelchair': 'yes',
    }
    response = parse_text(model, website_text, tags)
    print(response)