from glob import glob
import json
import os

import parse_text

def main():
    filepaths = sorted(glob('data/text/*'))
    model = 'claude-haiku-4.5'
    # model = 'claude-sonnet-4.6'
    os.makedirs('data/parsed', exist_ok=True)

    for i in range(len(filepaths)):
        print(f'{i} / {len(filepaths)}')
        filepath = filepaths[i]
        if filepath.endswith('-err.txt'):
            print('err website, skipping...')
            continue
        filename = filepath.replace('data/text/', '')
        feature = None
        with open(f'data/source/{filename.replace(".txt", ".geojson")}') as f:
            feature = json.load(f)
        url = feature['properties']['website']

        website_text = None
        with open(filepath) as f:
            website_text = f.read()

        tags = {}
        tag_list = ['name', 'amenity', 'addr:street', 'addr:city']
        print('tags:')
        for tag in tag_list:
            if tag in feature['properties']:
                tags[tag] = feature['properties'][tag]
                print(f'{tag}={feature["properties"][tag]}')
        
        print()
        parsed = parse_text.parse_text(model, website_text, tags)

        print(f'url:\n{url}\n')
        print(f'website_text:\n================\n{website_text}\n================\n')
        print(f'parsed:\n{parsed}')

        with open(f'data/parsed/{filename}', 'w') as f:
            f.write(parsed)

        print('\n\n\n\n')

if __name__ == '__main__':
    main()
