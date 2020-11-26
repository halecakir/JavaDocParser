import pandas as pd
import subprocess

df = pd.read_csv("links.csv")
for _, row in df.iterrows():
    if row["Status"] == "OK":
        url = row["Additional Links"]
        list_files = subprocess.call(["wget", "--no-parent", "--recursive", "--level=inf", "--page-requisites", "--wait=1", url], cwd="JavaDocs")

