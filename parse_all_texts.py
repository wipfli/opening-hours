from glob import glob
import json
import os
from multiprocessing import Pool

import parse_text

def single(text_filepath, model):
    print(text_filepath)
    
    if text_filepath.endswith('-err.txt'):
        print('err website, skipping...')
        return

    filename = text_filepath.replace('data/text/', '')
    output_filepath = f'data/parsed/{filename}'

    if os.path.isfile(output_filepath):
        print('already done, skipping...')
        return

    feature = None
    with open(f'data/source/node-{filename.replace(".txt", ".geojson")}') as f:
        feature = json.load(f)

    website_text = None
    with open(text_filepath) as f:
        website_text = f.read()

    tags = feature['properties']
    
    parsed = parse_text.parse_text(model, website_text, tags)

    with open(output_filepath, 'w') as f:
        f.write(parsed)

def main():
    filepaths = sorted(glob('data/text/*'))
    model = 'openrouter/qwen/qwen3.8-max'
    os.makedirs('data/parsed', exist_ok=True)

    argument_tuples = [(filepath, model) for filepath in filepaths]
    with Pool(10) as pool:
        pool.starmap(single, argument_tuples, chunksize=1)

if __name__ == '__main__':
    main()
