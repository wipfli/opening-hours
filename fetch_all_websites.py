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
        err, text = fetch_text.fetch_text(url)
        if err is not None:
            print(f'err\n{err}')
            with open(f'data/text/{feature["id"]}-err.txt', 'w') as f:
                f.write(err)
        else:
            print(f'text\n{text}')
            with open(f'data/text/{feature["id"]}.txt', 'w') as f:
                f.write(text)
        print()

if __name__ == '__main__':
    main()