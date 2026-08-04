import json
import os

def main():
    osm_extract = None
    with open('osm_extract.geojson') as f:
        osm_extract = json.load(f)
    
    os.makedirs('data/source', exist_ok=True)
    for feature in osm_extract['features']:
        feature['id'] = feature['properties']['id']
        filename = f'node-{feature["id"]}.geojson'
        with open(f'data/source/{filename}', 'w') as f:
            json.dump(feature, f, indent=2)

if __name__ == '__main__':
    main()