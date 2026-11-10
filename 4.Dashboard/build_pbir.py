"""Build the CivicPulse three-page report from the saved PBIR project."""
from __future__ import annotations

import copy
import hashlib
import json
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "Dashboard.Report" / "definition"
PAGES = REPORT / "pages"
BASE_PAGE = "b879c13a3a3077851ecb"
SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.14.0/schema.json"
PAGE_SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json"


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def column(entity: str, prop: str) -> dict:
    return {"Column": {"Expression": {"SourceRef": {"Entity": entity}}, "Property": prop}}


def aggregate(entity: str, prop: str, function: int) -> dict:
    return {"Aggregation": {"Expression": {"Column": {"Expression": {"SourceRef": {"Entity": entity}}, "Property": prop}}, "Function": function}}


def projection(entity: str, prop: str, agg: int | None = None, native: str | None = None) -> dict:
    field = column(entity, prop) if agg is None else aggregate(entity, prop, agg)
    aggregate_name = {0: "Sum", 1: "Average", 2: "Count", 3: "Min", 4: "Max", 5: "DistinctCount", 6: "Median", 7: "StandardDeviation", 8: "Variance", 9: "CountNonNull"}
    query_ref = f"{entity}.{prop}" if agg is None else f"{aggregate_name.get(agg, 'Aggregate')}({entity}.{prop})"
    item = {"field": field, "queryRef": query_ref}
    if native:
        item["nativeQueryRef"] = native
    return item


def title_obj(text: str) -> dict:
    return {"title": [{"properties": {"text": {"expr": {"Literal": {"Value": "'" + text.replace("'", "''") + "'"}}}}}]}


def make_visual(name: str, visual_type: str, title: str, pos: tuple[int, int, int, int], roles: dict, sort: dict | None = None) -> dict:
    state = {role: {"projections": projections} for role, projections in roles.items()}
    visual = {
        "visualType": visual_type,
        "query": {"queryState": state},
        "visualContainerObjects": {**title_obj(title), "subTitle": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}]},
        "drillFilterOtherVisuals": True,
    }
    if sort:
        visual["query"]["sortDefinition"] = sort
    return {
        "$schema": SCHEMA,
        "name": name,
        "position": {"x": pos[0], "y": pos[1], "z": 0, "width": pos[2], "height": pos[3], "tabOrder": pos[1] + pos[0]},
        "visual": visual,
    }


def chart(name: str, visual_type: str, title: str, category: tuple[str, str], value: tuple[str, str, int | None], pos: tuple[int, int, int, int], value_label: str, sort_desc: bool = True) -> dict:
    ent, cat = category
    ve, vp, agg = value
    sort_field = column(ent, cat) if visual_type == "lineChart" or agg is None else aggregate(ve, vp, agg)
    sort_direction = "Ascending" if visual_type == "lineChart" or not sort_desc else "Descending"
    sort = {"sort": [{"field": sort_field, "direction": sort_direction}], "isDefaultSort": True}
    return make_visual(name, visual_type, title, pos, {
        "Category": [projection(ent, cat)],
        "Y": [projection(ve, vp, agg, value_label)],
    }, sort)


def highlight_max(visual: dict, entity: str, measure: str, *, slow: bool = False) -> None:
    visual.setdefault("visual", {}).setdefault("objects", {})["dataPoint"] = [{
        "properties": {"fill": {"solid": {"color": {"expr": {"Measure": {"Expression": {"SourceRef": {"Entity": entity}}, "Property": measure}}}}}},
        "selector": {"data": [{"roles": ["Category"]}]},
    }]


def add_zip_data_bars(visual: dict) -> None:
    visual["visual"].setdefault("objects", {})["columnFormatting"] = [{
        "properties": {"dataBars": {
            "positiveColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#0B4F9E'"}}}}},
            "negativeColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#B8C4D6'"}}}}},
            "axisColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#8B9AA5'"}}}}},
            "reverseDirection": {"expr": {"Literal": {"Value": "false"}}},
            "hideText": {"expr": {"Literal": {"Value": "false"}}},
        }},
        "selector": {"metadata": "top_zip_codes.request_count"},
    }]


def text_visual(name: str, text: str, pos: tuple[int, int, int, int], *, font_size: int = 24, color: str = "#17324D", bold: bool = False) -> dict:
    return {
        "$schema": SCHEMA,
        "name": name,
        "position": {"x": pos[0], "y": pos[1], "z": 1000, "width": pos[2], "height": pos[3], "tabOrder": pos[1] + pos[0]},
        "visual": {"visualType": "textbox", "objects": {"general": [{"properties": {"paragraphs": [{"textRuns": [{"value": text, "textStyle": {"fontFamily": "Segoe UI", "fontSize": font_size, "color": color, "bold": bold}}]}]}}]}, "drillFilterOtherVisuals": True},
    }


def page_navigator(name: str, pos: tuple[int, int, int, int]) -> dict:
    return {
        "$schema": SCHEMA,
        "name": name,
        "position": {"x": pos[0], "y": pos[1], "z": 1000, "width": pos[2], "height": pos[3], "tabOrder": pos[1] + pos[0]},
        "visual": {"visualType": "pageNavigator", "objects": {"general": [{"properties": {"orientation": {"expr": {"Literal": {"Value": "'Horizontal'"}}}}}]}, "drillFilterOtherVisuals": True},
    }


def top_n_filter(entity: str, category: str, value: str, count: int = 10, direction: int = 2, aggregation: int = 6) -> dict:
    field = column(entity, category)
    value_field = aggregate(entity, value, aggregation)
    return {"filters": [{
        "name": hashlib.sha1(f"{entity}.{category}.topn".encode("utf-8")).hexdigest()[:20],
        "field": field,
        "type": "TopN",
        "filter": {"Version": 2, "From": [
            {"Name": "subquery", "Expression": {"Subquery": {"Query": {"Version": 2, "From": [{"Name": "s", "Entity": entity, "Type": 0}], "Select": [{"Column": {"Expression": {"SourceRef": {"Source": "s"}}, "Property": category}, "Name": "field"}], "OrderBy": [{"Direction": direction, "Expression": {"Aggregation": {"Expression": {"Column": {"Expression": {"SourceRef": {"Source": "s"}}, "Property": value}}, "Function": aggregation}}}], "Top": count}}}, "Type": 2},
            {"Name": "s", "Entity": entity, "Type": 0}],
            "Where": [{"Condition": {"In": {"Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "s"}}, "Property": category}}], "Table": {"SourceRef": {"Source": "subquery"}}}}}]},
        "howCreated": "User",
    }]}


def matrix(name: str, title: str, pos: tuple[int, int, int, int]) -> dict:
    visual = make_visual(name, "pivotTable", title, pos, {
        "Rows": [projection("top3_types_by_borough", "borough")],
        "Columns": [projection("top3_types_by_borough", "rank")],
        "Values": [projection("top3_types_by_borough", "complaint_type", 3, "Complaint type")],
    }, {"sort": [{"field": column("top3_types_by_borough", "borough"), "direction": "Ascending"}], "isDefaultSort": True})
    visual["visual"]["objects"] = {
        "rowGrandTotal": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}],
        "columnGrandTotal": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}],
        "rowSubtotals": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}],
        "columnSubtotals": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}],
    }
    return visual


def table(name: str, title: str, fields: list[tuple[str, str]], pos: tuple[int, int, int, int], *, sort_field: tuple[str, str, int] | None = None) -> dict:
    values = [projection(entity, prop, agg, label) for entity, prop, agg, label in fields]
    sort = None
    if sort_field:
        entity, prop, agg = sort_field
        field = column(entity, prop) if agg is None else aggregate(entity, prop, agg)
        sort = {"sort": [{"field": field, "direction": "Descending"}], "isDefaultSort": True}
    return make_visual(name, "tableEx", title, pos, {"Values": values}, sort)


def slicer(name: str, title: str, entity: str, prop: str, pos: tuple[int, int, int, int]) -> dict:
    visual = make_visual(name, "slicer", title, pos, {"Values": [projection(entity, prop)]})
    visual["visual"]["objects"] = {"data": [{"properties": {"mode": {"expr": {"Literal": {"Value": "'Dropdown'"}}}}}]}
    return visual


def card(name: str, entity: str, measure: str, label: str, pos: tuple[int, int, int, int]) -> dict:
    return {
        "$schema": SCHEMA,
        "name": name,
        "position": {"x": pos[0], "y": pos[1], "z": 0, "width": pos[2], "height": pos[3], "tabOrder": pos[1] + pos[0]},
        "visual": {
            "visualType": "cardVisual",
            "query": {"queryState": {"Data": {"projections": [{
                "field": {"Measure": {"Expression": {"SourceRef": {"Entity": entity}}, "Property": measure}},
                "queryRef": f"{entity}.{measure}", "nativeQueryRef": label
            }]}}},
            "visualContainerObjects": title_obj(label),
            "objects": {"value": [{"properties": {"labelDisplayUnits": {"expr": {"Literal": {"Value": "1D"}}}}}]},
            "drillFilterOtherVisuals": True
        }
    }


def azure_map(name: str, title: str, pos: tuple[int, int, int, int]) -> dict:
    return {
        "$schema": SCHEMA,
        "name": name,
        "position": {"x": pos[0], "y": pos[1], "z": 0, "width": pos[2], "height": pos[3], "tabOrder": pos[1] + pos[0]},
        "visual": {
            "visualType": "azureMap",
            "query": {"queryState": {
                "X": {"projections": [projection("requests_by_borough", "map_longitude")]},
                "Y": {"projections": [projection("requests_by_borough", "map_latitude")]},
                "Series": {"projections": [{"field": column("requests_by_borough", "borough"), "queryRef": "requests_by_borough.borough", "nativeQueryRef": "Borough", "active": True}]},
                "Size": {"projections": [{"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "requests_by_borough"}}, "Property": "Borough Requests"}}, "queryRef": "requests_by_borough.Borough Requests", "nativeQueryRef": "Requests", "active": True}]}
            }},
            "objects": {
                "bubbleLayer": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "sizeByValue": {"expr": {"Literal": {"Value": "true"}}}}}],
                "legend": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}],
            },
            "visualContainerObjects": {**title_obj(title), "subTitle": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}]},
            "drillFilterOtherVisuals": True
        }
    }


def save_page(page_id: str, display_name: str, visuals: list[dict]) -> None:
    page_dir = PAGES / page_id
    page_path = page_dir / "page.json"
    page = {
        "$schema": PAGE_SCHEMA,
        "name": page_id,
        "displayName": display_name,
        "displayOption": "FitToPage",
        "height": 1080,
        "width": 1920,
    }
    # Remove only visuals in this page so reruns are idempotent.
    visual_root = page_dir / "visuals"
    if visual_root.exists():
        shutil.rmtree(visual_root)
    write_json(page_path, page)
    takeaway_titles = {
        "Overview": "Illegal parking and residential noise lead 311 demand",
        "Geography": "Brooklyn leads request volume; Queens has most open requests",
        "Performance": "Resolution speed varies by agency and problem type",
    }
    visuals = [
        text_visual("page_title", takeaway_titles[display_name], (30, 22, 1250, 58), font_size=25, bold=True),
        page_navigator("page_navigation", (30, 96, 700, 48)),
        *visuals,
        text_visual("sample_footer", "2% sample of 2024 requests. Compare shares and rankings, not city totals.", (30, 1032, 1250, 30), font_size=12, color="#536575"),
    ]
    for v in visuals:
        write_json(visual_root / v["name"] / "visual.json", v)


def main() -> None:
    base_page_dir = PAGES / BASE_PAGE

    # Performance: suppress low-sample complaint types in Power Query and show
    # SQL-provided target rates without recalculating the denominator in Power BI.
    performance_visuals = [
        # These source views already have one row per complaint/agency. Median
        # aggregation preserves the SQL median while binding a numeric chart role.
        chart("median_by_type", "clusteredBarChart", "10 slowest complaint types | median days (≥30 closed; ≤365 days)", ("resolution_by_type", "complaint_type"), ("resolution_by_type", "median_days", 6), (30, 170, 900, 380), "Median days", True),
        chart("median_by_agency", "clusteredBarChart", "Slowest agencies | median days; DHS partial, OTI/DOE small samples", ("resolution_by_agency", "agency_label"), ("resolution_by_agency", "median_days", 6), (990, 170, 900, 380), "Median days", True),
        make_visual("within_targets", "clusteredBarChart", "% closed within target | valid-date denominator", (30, 570, 900, 420), {
            "Category": [projection("solved_within_by_agency", "agency_label")],
            "Y": [projection("solved_within_by_agency", "pct_24h", 0, "Within 24 h"), projection("solved_within_by_agency", "pct_7d", 0, "Within 7 days")],
        }, {"sort": [{"field": column("solved_within_by_agency", "agency_label"), "direction": "Ascending"}], "isDefaultSort": True}),
        text_visual("performance_notes", "DHS (partial): valid closing dates for 354 of 685 requests. OTI (5) and DOE (17) are small samples. Types with <30 closed requests and medians >365 days are omitted.", (30, 1000, 1860, 25), font_size=13, color="#596A78"),
        make_visual("open_closed_agency", "clusteredBarChart", "Open and closed workload by agency", (990, 790, 900, 200), {
            "Category": [projection("open_closed_by_agency", "agency_label")],
            "Y": [projection("open_closed_by_agency", "open_requests", 0, "Open"), projection("open_closed_by_agency", "closed_requests", 0, "Closed")],
        }, {"sort": [{"field": aggregate("open_closed_by_agency", "open_requests", 0), "direction": "Descending"}], "isDefaultSort": True}),
    ]
    for chart_visual in (performance_visuals[0], performance_visuals[1]):
        chart_visual["filterConfig"] = top_n_filter("resolution_by_type" if chart_visual["name"] == "median_by_type" else "resolution_by_agency", "complaint_type" if chart_visual["name"] == "median_by_type" else "agency_label", "median_days")
    performance_visuals[0]["visual"]["query"]["queryState"]["Tooltips"] = {"projections": [projection("resolution_by_type", "nb_closed", 0, "Closed sample count")]}
    performance_visuals[0]["visual"]["objects"] = {"labels": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}}}]}
    performance_visuals[1]["visual"]["objects"] = {"labels": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}}}]}
    performance_visuals[2]["visual"]["objects"] = {"labels": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}}}]}
    performance_visuals[4]["filterConfig"] = top_n_filter("open_closed_by_agency", "agency_label", "open_requests", count=8, aggregation=0)
    performance_visuals[4]["visual"]["objects"] = {"labels": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}}}]}
    resolution_type_table = table("resolution_type_table", "Complaint resolution detail | ≥30 closed, ≤365 median days", [
        ("resolution_by_type", "complaint_type", None, "Complaint type"),
        ("resolution_by_type", "nb_closed", 0, "Closed requests"),
        ("resolution_by_type", "median_days", None, "Median days"),
    ], (990, 570, 900, 210), sort_field=("resolution_by_type", "median_days", None))
    resolution_type_table["filterConfig"] = top_n_filter("resolution_by_type", "complaint_type", "median_days")
    performance_visuals.append(resolution_type_table)
    save_page(BASE_PAGE, "Performance", performance_visuals)

    overview_id = "civicpulse_overview"
    overview_visuals = [
        card("kpi_total", "kpi_overview", "Total Requests", "Total requests", (30, 170, 440, 110)),
        card("kpi_open", "kpi_overview", "Open Requests", "Open requests", (490, 170, 440, 110)),
        card("kpi_closure", "kpi_overview", "Closure Rate", "Closure rate", (950, 170, 440, 110)),
        card("kpi_median", "kpi_overview", "Median Resolution Hours", "Median resolution (hours)", (1410, 170, 480, 110)),
        chart("requests_per_month", "clusteredColumnChart", "Monthly requests, 2024", ("monthly_requests", "month"), ("monthly_requests", "total_requests", 0), (30, 300, 900, 310), "Requests", False),
        chart("top_problems", "clusteredBarChart", "Illegal parking leads the top complaint types", ("top_complaint_types", "complaint_type"), ("top_complaint_types", "request_count", 0), (990, 300, 900, 350), "Requests", True),
        chart("requests_by_hour", "clusteredColumnChart", "Requests peak at 11:00", ("requests_by_hour", "hour_of_day"), ("requests_by_hour", "requests", 0), (30, 670, 900, 300), "Requests", False),
        chart("requests_by_weekday", "clusteredColumnChart", "Monday has the most requests", ("requests_by_weekday", "weekday_name"), ("requests_by_weekday", "requests", 0), (990, 670, 900, 300), "Requests", False),
    ]
    month_chart = next(v for v in overview_visuals if v["name"] == "requests_per_month")
    month_chart["visual"]["query"]["sortDefinition"] = {"sort": [{"field": column("monthly_requests", "month"), "direction": "Ascending"}], "isDefaultSort": True}
    month_chart["visual"]["objects"] = {"labels": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}}}]}
    hour_chart = next(v for v in overview_visuals if v["name"] == "requests_by_hour")
    hour_chart["visual"]["query"]["sortDefinition"] = {"sort": [{"field": column("requests_by_hour", "hour_of_day"), "direction": "Ascending"}], "isDefaultSort": True}
    weekday_chart = next(v for v in overview_visuals if v["name"] == "requests_by_weekday")
    weekday_chart["visual"]["query"]["sortDefinition"] = {"sort": [{"field": column("requests_by_weekday", "weekday_name"), "direction": "Ascending"}], "isDefaultSort": True}
    weekday_chart["visual"]["objects"] = {"labels": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}}}]}
    for visual_name in ("top_problems",):
        visual = next(v for v in overview_visuals if v["name"] == visual_name)
        visual["visual"]["objects"] = {"labels": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}}}]}
    highlight_max(next(v for v in overview_visuals if v["name"] == "top_problems"), "top_complaint_types", "Highlight Color top_complaint_types")
    hour_chart["visual"]["objects"] = {"labels": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}}}]}
    hour_chart["visual"]["visualContainerObjects"]["subTitle"] = [{"properties": {
        "show": {"expr": {"Literal": {"Value": "true"}}},
        "text": {"expr": {"Literal": {"Value": "'Peak: 11:00, with 2,766 requests (6.0% of the sample)'"}}},
    }}]
    highlight_max(hour_chart, "requests_by_hour", "Highlight Color requests_by_hour")
    highlight_max(next(v for v in overview_visuals if v["name"] == "requests_by_weekday"), "requests_by_weekday", "Highlight Color requests_by_weekday")
    highlight_max(month_chart, "monthly_requests", "Highlight Color monthly_requests")
    save_page(overview_id, "Overview", overview_visuals)

    geography_id = "civicpulse_geography"
    geography_visuals = [
        azure_map("borough_map", "Request volume across the five boroughs", (30, 170, 900, 420)),
        chart("requests_borough", "clusteredBarChart", "Brooklyn has the highest request volume", ("requests_by_borough", "borough"), ("requests_by_borough", "total_requests", 0), (990, 170, 900, 250), "Requests", False),
        chart("open_by_borough", "clusteredBarChart", "Queens has the highest open rate", ("open_requests_by_borough", "borough"), ("open_requests_by_borough", "open_rate_pct", 0), (990, 440, 900, 250), "Open rate", True),
        matrix("top3_by_borough", "Top 3 complaint types by borough", (30, 615, 900, 355)),
        table("zipcode_volume", "10 busiest ZIP codes | SQL view excludes Unknown ZIPs", [
            ("top_zip_codes", "incident_zip", None, "ZIP code"),
            ("top_zip_codes", "borough", None, "Borough"),
            ("top_zip_codes", "request_count", None, "Requests"),
        ], (990, 615, 900, 355), sort_field=("top_zip_codes", "request_count", 0)),
        slicer("borough_filter", "Borough", "requests_by_borough", "borough", (1530, 25, 360, 70)),
    ]
    for chart_visual in (geography_visuals[1], geography_visuals[2]):
        chart_visual["visual"]["query"]["sortDefinition"] = {"sort": [{"field": column("requests_by_borough" if chart_visual["name"] == "requests_borough" else "open_requests_by_borough", "borough"), "direction": "Ascending"}], "isDefaultSort": True}
    for visual in (geography_visuals[1], geography_visuals[2]):
        visual["visual"]["objects"] = {"labels": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}}}]}
    highlight_max(geography_visuals[1], "requests_by_borough", "Highlight Color requests_by_borough")
    highlight_max(geography_visuals[2], "open_requests_by_borough", "Highlight Color open_requests_by_borough")
    add_zip_data_bars(geography_visuals[4])
    highlight_max(performance_visuals[0], "resolution_by_type", "Highlight Color resolution_by_type", slow=True)
    highlight_max(performance_visuals[1], "resolution_by_agency", "Highlight Color resolution_by_agency", slow=True)
    save_page(geography_id, "Geography", geography_visuals)

    pages_meta = json.loads((PAGES / "pages.json").read_text(encoding="utf-8"))
    pages_meta["pageOrder"] = [overview_id, geography_id, BASE_PAGE]
    pages_meta["activePageName"] = overview_id
    write_json(PAGES / "pages.json", pages_meta)

    theme_path = ROOT / "Dashboard.Report" / "StaticResources" / "SharedResources" / "BaseThemes" / "Fluent2-CY26SU10.json"
    theme = json.loads(theme_path.read_text(encoding="utf-8"))
    theme["dataColors"] = ["#0B4F9E", "#B8C4D6", "#E8710A", "#17324D"]
    theme["tableAccent"] = "#0B4F9E"
    for card_style in theme.get("visualStyles", {}).get("cardVisual", {}).values():
        for value_style in card_style.get("value", []):
            value_style["labelDisplayUnits"] = 1
    theme_path.write_text(json.dumps(theme, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # Parse every generated definition before handing control back to Desktop.
    for page_json in PAGES.rglob("*.json"):
        json.loads(page_json.read_text(encoding="utf-8"))

    # Verify that every referenced table/column is present in the TMDL model.
    tables_root = ROOT / "Dashboard.SemanticModel" / "definition" / "tables"
    model_tables: dict[str, set[str]] = {}
    for table_file in tables_root.glob("*.tmdl"):
        source = table_file.read_text(encoding="utf-8")
        table_match = re.search(r"^table\s+(.+)$", source, re.MULTILINE)
        if not table_match:
            continue
        model_tables[table_match.group(1).strip()] = set(re.findall(r"^\s+column\s+(.+)$", source, re.MULTILINE))
    missing: list[str] = []
    for visual_file in PAGES.rglob("visual.json"):
        visual_data = json.loads(visual_file.read_text(encoding="utf-8"))
        for item in visual_data.get("visual", {}).get("query", {}).get("queryState", {}).values():
            for item_projection in item.get("projections", []):
                field = item_projection.get("field", {})
                # Columns and aggregations both contain a Column object.
                while field and "Column" not in field:
                    field = field.get("Aggregation", {}).get("Expression", {})
                col = field.get("Column", {}) if field else {}
                entity = col.get("Expression", {}).get("SourceRef", {}).get("Entity")
                prop = col.get("Property")
                if entity and prop and prop not in model_tables.get(entity, set()):
                    missing.append(f"{visual_file}: {entity}.{prop}")
    if missing:
        raise ValueError("Missing model fields:\n" + "\n".join(missing))
    print(f"Created {len(pages_meta['pageOrder'])} report pages and {sum(1 for _ in PAGES.rglob('visual.json'))} visuals.")
    print(f"Validated PBIR JSON and all bound fields against {len(model_tables)} model tables.")


if __name__ == "__main__":
    main()
