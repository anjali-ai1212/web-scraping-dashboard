import os
import pandas as pd


def export_csv(data):

    df = pd.DataFrame(data)

    path = os.path.join("exports", "csv", "scraped_data.csv")

    df.to_csv(path, index=False)

    return path


def export_excel(data):

    df = pd.DataFrame(data)

    path = os.path.join("exports", "excel", "scraped_data.xlsx")

    df.to_excel(path, index=False)

    return path


def export_json(data):

    df = pd.DataFrame(data)

    path = os.path.join("exports", "json", "scraped_data.json")

    df.to_json(path, orient="records", indent=4)

    return path