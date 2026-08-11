import json
from glob import glob
import os

import fetch_text

def main():
    filepaths = sorted(glob('data/source/*'))
    
    os.makedirs('data/text', exist_ok=True)
    for i in range(0, len(filepaths)):
        filepath = filepaths[i]
        feature = None
        with open(filepath) as f:
            feature = json.load(f)
        url = feature['properties']['website']
        print(f'{i} / {len(filepaths)}', url)
        error_filepath = f'data/text/{feature["id"]}-err.txt'
        success_filepath = f'data/text/{feature["id"]}.txt'
        if os.path.isfile(error_filepath) or os.path.isfile(success_filepath):
            print('Already done. Skipping...')
            continue
        err, text = fetch_text.fetch_text(url)
        if err is not None:
            print(f'err\n{err}')
            with open(error_filepath, 'w') as f:
                f.write(err)
        else:
            print(f'text\n{text}')
            with open(success_filepath, 'w') as f:
                f.write(text)

if __name__ == '__main__':
    main()