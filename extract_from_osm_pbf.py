import osmium
import json

class RestaurantHandler(osmium.SimpleHandler):
    def __init__(self):
        super().__init__()
        self.features = []

    def node(self, n):
        tags = n.tags

        if tags.get('amenity') != 'restaurant':
            return

        if 'opening_hours' not in tags:
            return

        if 'website' not in tags:
            return

        lon = n.location.lon
        lat = n.location.lat

        self.features.append({
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [lon, lat]
            },
            'properties': {
                'id': n.id,
                **dict(tags)
            }
        })


def main(input_filepath, output_filepath):
    handler = RestaurantHandler()

    handler.apply_file(input_filepath, locations=True)

    geojson = {
        'type': 'FeatureCollection',
        'features': handler.features
    }

    with open(output_filepath, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, indent=2)


if __name__ == '__main__':
    input_filepath = 'data/switzerland-latest.osm.pbf'
    output_filepath = 'osm_extract.geojson'
    main(input_filepath, output_filepath)