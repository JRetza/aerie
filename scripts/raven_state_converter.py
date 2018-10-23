#!/usr/bin/env python3 -tt
"""
The purpose of this script is given a state that was saved in raven pre-34.8.0
and convert that state to a state that is compatible with Raven2 or 34.8.0 and
beyond.
"""

# Imports
import argparse
import json
import urllib.parse as urlparse
import re
from datetime import datetime


def t_time_to_epoch(t_time):
    # example input: "1993-295T01:00:00.000"
    return datetime.strptime(t_time, "%Y-%jT%H:%M:%S.%f").timestamp()

def convert_color(rgb_color):
    return '#%02x%02x%02x' % tuple(map(int, rgb_color))

def split_units(label_string):
    """Currently UNUSED, but planned to replace `extract_units` and `strip_units`."""
    # The label extends to the first left-parenthesis.
    # The units are between the final pair of parentheses.
    UNITS_REX = r"^(?P<label>[^(]*)(?:\(.+?)?\((?P<units>[^(]*)\)[^)]*$$"

    match = re.search(UNITS_REX, label_string)
    if not match:
        return {"label": label_string.strip(), "units": ""}
    else:
        return {"label": match.group(1).strip(), "units": match.group(2).strip()}

def extract_units(label_string):
    if label_string.endswith(')'):
        return label_string[:label_string.rfind(")")].rsplit("(", 1)[1]
    else:
        return ""

def strip_units(label_string):
    if label_string.endswith(')'):
        label = label_string[:label_string.rfind(")")].split("(", 1)[0]
        label = label.rstrip()
        return label
    else:
        return label_string

def parse_data_source_url(url_str):
    BAND_TYPE_REGEX = r"/api/v2/(?P<file_type>[^_]+)(?:_(?P<band_type>[^-]+))?-(?P<db>[^/]+)/(?P<path>.+)"

    url = urlparse.urlparse(url_str)
    url_path = url.path
    url_qs = urlparse.parse_qs(url.query)

    match = re.search(BAND_TYPE_REGEX, url_path)

    return {
        "file_type": match.group("file_type"),
        "band_type": match.group("band_type"),
        "source_name": match.group("db"),
        "path": "/" + match.group("path"),
        "parameters": url_qs,
    }


def traverse_source_tree(data, predicate, prefix="/"):
    for source in data["sources"]:
        # Determine the path to this node
        path = prefix + source["name"]

        if predicate(source):
            yield path, source

        yield from traverse_source_tree(source, predicate, path + "/")


def source_by(*, band_id):
    def predicate(source):
        return (band_id in source["bandIds"])
    return predicate

def find_tree_sources(data, band):
    sources = []
    for path, _source in traverse_source_tree(data, source_by(band_id=band["id"])):
        sources.append(path)
    return sources

def create_resource_band(raven_one_band, sources, default_band_settings):
    source_info = parse_data_source_url(raven_one_band["url"])

    if "lineColorCustom" in raven_one_band["graphSettings"]:
        color = convert_color(raven_one_band["graphSettings"]["lineColorCustom"])
    else:
        color = default_band_settings["resourceColor"]

    if "fillColorCustom" in raven_one_band["graphSettings"]:
        fillColor = convert_color(raven_one_band["graphSettings"]["fillColorCustom"])
    else:
        fillColor = default_band_settings["resourceFillColor"]

    return {
        "addTo": False,
        "autoScale": True,
        "backgroundColor": "#FFFFFF",
        "color": color,
        "decimate": (source_info["parameters"].get("decimate", ["false"])[0] == "true"),
        "fill": raven_one_band["graphSettings"].get("fill") or False,  # for states
        "fillColor": fillColor,
        "height": raven_one_band["graphSettings"].get("height", 100),
        "heightPadding": raven_one_band["graphSettings"].get("heightPadding", 10),
        "icon": default_band_settings["icon"],
        "interpolation": raven_one_band["graphSettings"].get("interpolation", "linear"),
        "isDuration": False,  # TODO: default (metadata.hasValueType.toLowerCase() === 'duration')
        "isTime": False,      # TODO: default (metadata.hasValueType.toLowerCase() === 'time')
        "label": strip_units(raven_one_band["label"]),  # TODO: default metadata.hasObjectName
        "labelColor": "#000000",
        "labelFont": default_band_settings["labelFont"],
        "labelPin": raven_one_band.get("suffix") or "",
        "labelUnit": extract_units(raven_one_band["label"]),
        "logTicks": raven_one_band["graphSettings"].get("logTicks") or False,
        "maxTimeRange": {
            "start": 0,
            "end": 0,
        },
        "name": raven_one_band["originalName"],  # TODO: default metadata.hasObjectName
        "points": [],
        "scientificNotation": raven_one_band["graphSettings"].get("scientificNotation") or False,
        "showIcon": raven_one_band["graphSettings"].get("iconEnabled") or False,
        "showLabelPin": bool(raven_one_band.get("suffix") or ""),
        "showLabelUnit": True,
        "showTooltip": True,
        "sourceIds": sources,
        "tableColumns": [],
        "type": "resource",
    }

def create_activity_band(raven_one_band, sources, default_band_settings):
    ACTIVITY_STYLES = {
        "bar":  1,
        "line": 2,
        "icon": 3,
    }
    DEFAULT_ACTIVITY_STYLE = 0

    return {
        "activityHeight": raven_one_band["graphSettings"]["activityHeight"],
        "activityStyle": ACTIVITY_STYLES.get(raven_one_band["graphSettings"]["style"], DEFAULT_ACTIVITY_STYLE),
        "addTo": False,
        "alignLabel": 3,
        "backgroundColor": "#FFFFFF",
        "baselineLabel": 3,
        "borderWidth": 1,
        "filterTarget": None,
        "height": raven_one_band["graphSettings"].get("height", 50),
        "heightPadding": raven_one_band["graphSettings"].get("heightPadding", 10),
        "icon": default_band_settings["icon"],
        "label": strip_units(raven_one_band["label"]),
        "labelColor": [0, 0, 0],
        "labelFont": default_band_settings["labelFont"],
        "labelPin": raven_one_band.get("suffix") or "",
        "layout": raven_one_band["graphSettings"]["activityLayout"],
        "legend": raven_one_band.get("legend", ""),
        "maxTimeRange": {
            "start": 0,
            "end": 0,
        },
        "minorLabels": list(filter(None, [raven_one_band["graphSettings"].get("filter")])),
        "name": raven_one_band.get("legend") or "",
        "points": [],
        "showActivityTimes": raven_one_band["graphSettings"].get("showActivityTimes", False),
        "showLabel": True,  # TODO: default !isMessageTypeActivity(legends[legend][0])
        "showLabelPin": bool(raven_one_band.get("suffix") or ""),
        "showTooltip": True,
        "sourceIds": sources,
        "tableColumns": [],
        "trimLabel": raven_one_band["graphSettings"].get("trimLabel", True),
        "type": "activity",
    }

def create_state_band(raven_one_band, sources, default_band_settings):
    return {
        "addTo": False,
        "alignLabel": 3,
        "backgroundColor": "#FFFFFF",
        "baselineLabel": 3,
        "borderWidth": 1,
        "color": default_band_settings["resourceColor"],
        "fill": False,
        "fillColor": default_band_settings["resourceFillColor"],
        "height": raven_one_band["graphSettings"].get("height") or 50,
        "heightPadding": 0,
        "icon": default_band_settings["icon"],
        "isNumeric": False,
        "label": strip_units(raven_one_band["label"]),  # TODO: default metadata.hasObjectName
        "labelColor": raven_one_band["graphSettings"].get("labelColor") or [0, 0, 0],
        "labelFont": default_band_settings["labelFont"],
        "labelPin": raven_one_band.get("suffix") or "",
        "maxTimeRange": {
            "start": 0,
            "end": 0,
        },
        "name": raven_one_band["originalName"],  # TODO: default metadata.hasObjectName
        "possibleStates": [],  # TODO: metadata.hasPossibleStates
        "points": [],
        "showIcon": False,
        "showLabelPin": bool(raven_one_band.get("suffix") or ""),
        "showStateChangeTimes": False,
        "showTooltip": True,
        "sourceIds": sources,
        "tableColumns": [],
        "type": "state",
    }

def create_divider_band(raven_one_band, sources, default_band_settings):
    return {
        "addTo": False,
        "backgroundColor": "#FFFFFF",
        "color": [255, 255, 255],
        "height": raven_one_band["graphSettings"].get("height", 7),
        "heightPadding": 10,
        "label": strip_units(raven_one_band["label"]),
        "labelColor": [0, 0, 0],
        "maxTimeRange": {
            "start": 0,
            "end": 0,
        },
        "name": raven_one_band["label"],
        "points": [],
        "showTooltip": True,
        "sourceIds": sources,
        "tableColumns": [],
        "type": "divider",
    }

def create_wrapper_band(band, *, container_id, sort_order):
    return {
        "compositeAutoScale": True,
        "compositeLogTicks": False,
        "compositeScientificNotation": False,
        "compositeYAxisLabel": False,
        "containerId": container_id,
        "height": band["height"],
        "heightPadding": band["heightPadding"],
        "name": band["name"],
        "overlay": False,
        "showTooltip": band["showTooltip"],
        "sortOrder": sort_order,
        "subBands": [band],
        "type": "composite",
    }


def determine_type_of_source(source):
    # This is just a set of heuristics which we've observed to be correct so far.
    # The "right" way to determine the band type is to ask MPS Server directly
    # and mimic the logic in Raven 2.
    if "url" not in source:
        # Dividers don't have any data sources.
        return "divider"
    elif "activityLayout" in source["graphSettings"]:
        # If it has an activity layout, it's probably really an activity.
        return "activity"
    elif "fill" in source["graphSettings"]:
        # Observationally, only resourecs have "fill", but this is tenuous.
        return "resource"
    else:
        # By process of elimination...
        return "state"

def convert_raven_one_band(raven_one_state, raven_one_band, default_band_settings):
    BAND_BUILDERS = {
        "resource": create_resource_band,
        "activity": create_activity_band,
        "divider": create_divider_band,
        "state": create_state_band,
    }

    band_type = determine_type_of_source(raven_one_band)
    builder = BAND_BUILDERS.get(band_type)
    if not builder:
        raise Exception("Unknown band type \""+band_type+"\"")

    # Identify the sources for this band
    sources = find_tree_sources(raven_one_state, raven_one_band)

    return builder(raven_one_band, sources, default_band_settings)

def convert_raven_one_bands(raven_one_state, default_band_settings):
    CHARTS = [
        ("0", "center"),  # Main Panel
        ("1", "south"),   # South Panel
    ]

    # First, handle all of the top-level bands
    bands = []
    for (containerId, panelId) in CHARTS:
        sort_order = 0
        for raven_one_band in raven_one_state["viewTemplate"]["charts"][panelId]:
            if "overlayBand" not in raven_one_band:
                # Convert the Raven 1 band into a Raven 2 band
                raven_two_band = convert_raven_one_band(raven_one_state, raven_one_band, default_band_settings)

                # Wrap it in a composite band
                top_level_band = create_wrapper_band(raven_two_band,
                    container_id=containerId,
                    sort_order=sort_order)
                sort_order += 1

                bands.append(top_level_band)

    # Next, add all of the overlay bands to their parents
    for (containerId, panelId) in CHARTS:
        for raven_one_band in raven_one_state["viewTemplate"]["charts"][panelId]:
            if "overlayBand" in raven_one_band:
                # Convert the Raven 1 band into a Raven 2 band
                raven_two_band = convert_raven_one_band(raven_one_state, raven_one_band, default_band_settings)

                # Add this band as a subband of its parent
                if raven_one_band.get("suffix") is not None:
                    overlay_band_name = strip_units(raven_one_band["overlayBand"])
                else:
                    overlay_band_name = raven_one_band["overlayBand"]

                for band in bands:
                    if band["name"] == overlay_band_name:
                        # This band is the unoverlaid band's parent
                        band["subBands"].append(raven_two_band)
                        break

    return bands


def tab_source_to_pin(tab_source):
    source_info = parse_data_source_url(tab_source["url"])

    return {
        "name": tab_source["tabName"],
        "sourceId": source_info["path"],
    }


def flatten_band(band):
    if len(band["subBands"]) != 1:
        # Can't flatten overlaid bands
        return band
    else:
        # Copy the first subband and add the container's id and order to it.
        flattened_band = dict(band["subBands"][0])
        flattened_band.update({
            "containerId": band["containerId"],
            "sortOrder": band["sortOrder"],
        })
        return flattened_band


def get_bands(raven_one_state, default_band_settings):
    return [
        flatten_band(band)
        for band in convert_raven_one_bands(raven_one_state, default_band_settings)
    ]

def get_default_band_settings(raven_one_state):
    return {
        "activityLayout": 0,
        "icon": "circle",
        "iconEnabled": False,
        "labelFont": "Georgia",
        "labelFontSize": raven_one_state.get("globalLabelFontSize", 9),
        "labelWidth": raven_one_state.get("bandLabelWidth", 150),
        "resourceColor": "#000000",
        "resourceFillColor": "#000000",
        "showLastClick": False,
        "showTooltip": raven_one_state.get("tooltipEnabled", True),
    }

def get_guides(guides):
    return [
        t_time_to_epoch(guide)
        for guide in guides
    ]

def get_pins(tab_sources):
    return [
        tab_source_to_pin(tab_source)
        for tab_source in tab_sources
        if "home" not in tab_source
    ]

def get_time_range(viewTemplate):
    return {
        "start": t_time_to_epoch(viewTemplate["viewStart"]),
        "end": t_time_to_epoch(viewTemplate["viewEnd"]),
    }

def convert_raven1_state_to_raven2(raven_one_state):
    default_band_settings = get_default_band_settings(raven_one_state["viewTemplate"])
    time_range = get_time_range(raven_one_state["viewTemplate"])

    return {
        "bands":
            get_bands(raven_one_state, default_band_settings),
        "defaultBandSettings":
            default_band_settings,
        "guides":
            get_guides(raven_one_state["viewTemplate"]["guides"]),
        "maxTimeRange":
            time_range,
        "name":
            raven_one_state["name"],
        "pins":
            get_pins(raven_one_state.get("tabSources", [])),
        "version":
            "1.0.0",
        "viewTimeRange":
            time_range,
    }



def option_parser():
  parser = argparse.ArgumentParser(description="""
    Convert a Raven <34.8.0 state to a Raven2 or >=34.8.0 state.
  """)

  parser.add_argument("state_json",
    help="Location of a JSON file containing a Raven state")

  return parser

def main(args):
    # Read in old state
    with open(args.state_json) as f:
        raven_one_state = json.load(f)[0]

    # Convert to new state
    raven_two_state = convert_raven1_state_to_raven2(raven_one_state)

    # Dump new state to stdout
    print(json.dumps(raven_two_state, indent=4, sort_keys=True))

if __name__ == "__main__":
    exit(main(option_parser().parse_args()) or 0)
