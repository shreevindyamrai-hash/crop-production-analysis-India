# Crop Production Analysis in India

## Project Overview

This project analyses crop production data from India to identify leading crops, compare average crop yields across states, examine seasonal production patterns, and explore yearly trends.

## Objectives

- Identify the top 10 crops by total production.
- Compare average production per hectare across states.
- Analyse crop production across different seasons.
- Examine yearly production and area trends.
- Clean raw data and generate a report based on the analysis.

## Technologies Used

- Python
- Pandas
- SQL (SQLite)
- Matplotlib

## Data Cleaning

The Python script standardises text fields, converts numerical columns, removes rows with missing required numerical values, filters invalid area and production values, removes duplicate rows, and excludes extreme yield values above the 99.5th percentile.

## Analysis and Outputs

The project generates:

- `top_crops.png` — top crops by total production
- `state_yield.png` — states ranked by average yield
- `season.png` — production by season
- `yearly_trend.png` — yearly production trend
- `yearly_summary.csv` — yearly totals, area, and record counts
- `cleaned_data.csv` — cleaned dataset
- `crops.db` — SQLite database
- `insights.md` — automatically generated findings

## How to Run

1. Install Python.
2. Install the required libraries:

   `python -m pip install pandas matplotlib`

3. Place the dataset CSV in the project directory.
4. Run:

   `python crop_analysis.py crop_production.csv`

5. Open the generated `output` folder.

## Findings

Add three to four observations after reviewing the generated charts and validating the yearly data. Include only findings supported by the analysis.

## Limitations

- Extreme yield values are excluded using a percentile-based threshold.
- Average yield is calculated as the mean of record-level production-to-area ratios.
- Differences in data coverage across years may affect comparisons of yearly totals.
- The analysis identifies patterns in the dataset but does not establish the causes of those patterns.