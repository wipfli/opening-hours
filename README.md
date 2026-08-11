# opening-hours
Read restaurant websites and extract opening hours in the OpenStreetMap format

## Usage

Query OpenStreetMap with https://overpass-turbo.eu to extract some restaurants, see [overpass-turbo.query](overpass-turbo.query) for a query which extracts restaurants that have a website and opening hours in OpenStreetMap.

Store the overpass results as GeoJSON in `overpass-turbo-results.geojson`.

Split the overpass geojson into multiple single feature files with

```
uv run python split_overpass_results.py
```

This will create a folder called `data/source` where each OpenStreetMap feature will be in an individual GeoJSON file.

Iterate over the features and scrape their websites with:

```
uv run python fetch_all_websites.py
```

This will create a folder called `data/text` where each website will be in a separate text file. If the scraping fails, the suffix will be `-err.txt` and the file content will be the error message.

Now parse the websites to extract opening hours with:

```
uv run python parse_all_texts.py
```

This will create a folder called `data/parsed` where each parsed website will be in a different text file. The last line will contain either a valid OpenStreetMap opening hours string or the word UNSURE.

The `data` folder structure is:

```
data
├── source
│   ├── node-9811058009.geojson
│   ├── node-983601215.geojson
│   ├── node-983601220.geojson
│   └── node-9844600412.geojson
├── text
│   ├── node-9811058009.txt
│   ├── node-983601215-err.txt
│   ├── node-983601220.txt
│   └── node-9844600412.txt
└── parsed
    ├── node-9811058009.txt
    ├── node-983601220.txt
    └── node-9844600412.txt
```

Example of a parsed output file:

```
Looking at the opening hours for QQ Sushi Zürich (Stampfenbachstrasse):

- MO–FR lunch: 11:30–14:30
- FR dinner: 17:30–23:00
- MO–DO dinner: 17:30–22:00
- SA: 11:30–23:00
- SO & Feiertag: 17:30–22:00

Let me parse this carefully:
- Mo-Do: 11:30-14:30, 17:30-22:00
- Fr: 11:30-14:30, 17:30-23:00
- Sa: 11:30-23:00
- Su: 17:30-22:00

Mo-Th: 11:30-14:30, 17:30-22:00
Fr: 11:30-14:30, 17:30-23:00
Sa: 11:30-23:00
Su: 17:30-22:00

Mo-Do 11:30-14:30,17:30-22:00; Fr 11:30-14:30,17:30-23:00; Sa 11:30-23:00; Su 17:30-22:00
```

## How This Works

The website text is sent to and LLM with the instruction to extract opening hours if possible.

Some OpenStreetMap tags are added to the prompt to give a little bit more context. For example the `addr:street` tag can be helpful if a restaurant has multiple locations and a single website which lists the hours for all locations.

The prompt, defined in [parse_text.py](parse_text.py), tries to cover some typical failure scenarios. For example a website might have multiple hours which are inconsistent, it might not have any hours at all, or it might only display the hours for the current day and say something like "open daily". In all those cases the LLM is instructed to return the word UNSURE. The main goal here is to produce only an opening hours string if there is a high chance that it is correct. Correct here means that the LLM either returns UNSURE or an accurate opening hours string. Returning UNSURE although a human can extract an accurate hours string from the website counts as correct as well.

The script uses the [llm](https://pypi.org/project/llm/) library to query LLMs. It can be configured to work with a variety providers.

Initial testing with 500+ restaurant websites in Zürich suggests that most of the time cost-efficient models such as Anthropic's [Haiku](https://www.anthropic.com/claude/haiku) are sufficient to create a correct result. However, there are cases where frontier models such as Anthropic's [Sonnet](https://www.anthropic.com/claude/sonnet) produce better results. This can be both avoid speculation and returning UNSURE where needed, and returning accurate opening hours strings where Haiku made a mistake.

All files in the `data/parsed` folder were verified by hand to be correct. Going forward one can use them to benchmark models and prompts.


## License

The code is licensed as BSD-3, see [LICENSE.md](LICENSE.md).

Features in the `data` folder are extracted from OpenStreetMap licensed as ODbL, copyright OpenStreetMap contributors.

```
uv run uvicorn validator:app --reload
```