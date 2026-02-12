"""
Climate dataset fetchers.

Each fetcher returns a list of positive real numbers ready for Benford analysis.
Raw data is cached to data/sources/<test_id>.json.
"""

import json
import os
import requests
import time

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "sources")


def _cache_path(test_id):
    return os.path.join(DATA_DIR, f"{test_id}.json")


def _load_cache(test_id):
    path = _cache_path(test_id)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return None


def _save_cache(test_id, data, metadata=None):
    os.makedirs(DATA_DIR, exist_ok=True)
    payload = {"test_id": test_id, "n": len(data), "values": data}
    if metadata:
        payload["metadata"] = metadata
    with open(_cache_path(test_id), "w") as f:
        json.dump(payload, f)
    return data


def fetch_wildfire_acreage(use_cache=True, max_records=None):
    """
    Fetch individual wildfire sizes (acres) from NIFC ArcGIS Feature Service.

    Uses the InterAgencyFirePerimeterHistory dataset which has GIS_ACRES.
    Paginated queries to the ArcGIS REST API.
    """
    test_id = "wildfire_acreage"

    if use_cache:
        cached = _load_cache(test_id)
        if cached:
            print(f"[{test_id}] Loaded {cached['n']} values from cache")
            return cached["values"]

    print(f"[{test_id}] Fetching from NIFC ArcGIS API...")

    base_url = (
        "https://services3.arcgis.com/T4QMspbfLg3qTGWY/arcgis/rest/services/"
        "InterAgencyFirePerimeterHistory_All_Years_View/FeatureServer/0/query"
    )

    all_acres = []
    offset = 0
    batch_size = 2000
    max_total = max_records or 500000

    while offset < max_total:
        params = {
            "where": "GIS_ACRES > 0",
            "outFields": "GIS_ACRES",
            "returnGeometry": "false",
            "f": "json",
            "resultOffset": offset,
            "resultRecordCount": batch_size,
            "orderByFields": "OBJECTID",
        }

        try:
            resp = requests.get(base_url, params=params, timeout=60)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"[{test_id}] API error at offset {offset}: {e}")
            break

        features = data.get("features", [])
        if not features:
            break

        batch = [f["attributes"]["GIS_ACRES"] for f in features if f["attributes"].get("GIS_ACRES")]
        all_acres.extend(batch)

        print(f"[{test_id}] Fetched {len(all_acres)} records so far...")

        # Check if there are more records
        if not data.get("exceededTransferLimit", False) and len(features) < batch_size:
            break

        offset += batch_size
        time.sleep(0.5)  # Be nice to the API

    # Filter to positive values
    values = [x for x in all_acres if isinstance(x, (int, float)) and x > 0]

    print(f"[{test_id}] Total: {len(values)} positive fire size records")

    _save_cache(test_id, values, metadata={
        "source": "NIFC InterAgencyFirePerimeterHistory",
        "field": "GIS_ACRES",
        "unit": "acres",
        "api": base_url,
    })

    return values


# Registry of all fetchers
FETCHERS = {
    "wildfire_acreage": fetch_wildfire_acreage,
}


def fetch_dataset(test_id, **kwargs):
    """Fetch a dataset by test_id."""
    fetcher = FETCHERS.get(test_id)
    if not fetcher:
        raise ValueError(f"No fetcher implemented for '{test_id}'. Available: {list(FETCHERS.keys())}")
    return fetcher(**kwargs)
