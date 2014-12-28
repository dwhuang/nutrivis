nutrivis
========

食品營養成分資料視覺化

Files
--
  - `parse.py` generates JSON files from raw data (csv)
  - `index.html` visualizes the JSON files using d3.js
  - `nutrition.csv` is the raw data file from http://data.fda.gov.tw/frontsite/data/DataAction.do?method=doDetail&infoId=20
  
Usage
--
  1. run `python parse.py json` to generate `food.json` and `meta.json`
  2. view `index.html`
  
