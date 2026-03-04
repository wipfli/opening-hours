import llm

def parse_text(model, website_text, tags):
    tag_lines = []
    for tag in tags.keys():
        tag_lines.append(f'- {tag}={tags[tag]}')

    prompt = f"""Extract the OpenStreetMap `opening_hours` string from the website content below.

Instructions:
- Prioritize quality over speculation.
- Only return an OpenStreetMap opening hours string if you are absolutely confident that it is correct.
- Do not use ticks around the opening hours string, just put the text on the line without anything around it.
- Only the last line of your output matters. If you need to correct yourself, put the correct answer on the last line of your output. 
- Use the OpenStreetMap tags below to find the hours if there are multiple locations or venues on one site.
- Always state on which days of the week the hours apply.
- If the venue is closed on certain days, use the word "off". Example "Sa-Su off".
- Use OpenStreetMap's 2-letter day abbreviations: Mo, Tu, We, Th, Fr, Sa, Su.
- If a venue is only open by appointment on certain days, you MUST exclude these days from the opening hours string.
- Some websites use JavaScript to show only the hours for the current day. If you think this could be the case, you MUST return "UNSURE" on the last line.
- If there are signs of a permanent future closure, return "UNSURE" on the last line.
- If no hours are found in the website, return "UNSURE" on the last line.
- If you are unsure what to do, return "UNSURE" on the last line.
- If you find contradicting opening hours, return "UNSURE" on the last line.
- Your last output line MUST be either a valid opening hours string or the word "UNSURE". It is NEVER your explanation.

The venue has these OpenStreetMap tags:
{'\n'.join(tag_lines)}

Website content:
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
    model = 'claude-opus-4.6'
    tags = {
        'amenity': 'restaurant',
        'wheelchair': 'yes',
    }
    result = parse_text(model, website_text, tags)
    print(result)