import json
import os

def main():
    overpass_turbo_results = None
    with open('overpass-turbo-results.geojson') as f:
        overpass_turbo_results = json.load(f)
    
    os.makedirs('data/source', exist_ok=True)
    for feature in overpass_turbo_results['features']:
        feature['id'] = feature['id'].replace('/', '-')
        filename = f'{feature["id"]}.geojson'
        with open(f'data/source/{filename}', 'w') as f:
            json.dump(feature, f, indent=2)

if __name__ == '__main__':
    main()