import tempfile
import requests
import os
import pandas as pd

gp_details = ['https://www.opendata.nhs.scot/dataset/f23655c3-6e23-4103-a511-a80d998adb90/resource/1a15cb34-fcf9-4d3f-ad63-1ba3e675fbe2/download/practice_contactdetails_oct2022-open-data.csv',
              'https://www.opendata.nhs.scot/dataset/f23655c3-6e23-4103-a511-a80d998adb90/resource/5273d444-5a79-4fad-a518-119a368e2161/download/practice_contactdetails_jul2022-open-data.csv',
              'https://www.opendata.nhs.scot/dataset/f23655c3-6e23-4103-a511-a80d998adb90/resource/8175c9ac-6953-4636-b151-f3946ef0fb80/download/practice_contactdetails_apr2022-open-data.csv',
              'https://www.opendata.nhs.scot/dataset/f23655c3-6e23-4103-a511-a80d998adb90/resource/1f76c338-7890-4ee7-b1bd-4d837cc1d50a/download/practice_contactdetails_jan2022.csv'
              ]

    # GP details csvs
temp_dir_gp = tempfile.mkdtemp()
for url in gp_details:
    filename = url.split("/")[-1]
    csv_path = os.path.join(temp_dir_gp, filename)
    response = requests.get(url)
    if response.status_code == 200:
        with open(csv_path, "wb") as file:
            file.write(response.content)
        print(f"CSV file saved successfully in: {csv_path}")
    else:
        print(f"Failed to download {url}")

for file in os.listdir(temp_dir_gp):
    test = pd.read_csv(csv_path)
    print(test.head(2))

