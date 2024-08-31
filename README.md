## How to use the scripts?
- Create a virtual environment using `venv`
```
python -m venv venv
```

- Install the requirements
```
pip install -r requirements.txt
```

- To download the data run `get_data.py`
```
python get_data.py
```

- Along with downloading the data it will generate `data_info.json` that stores 
  dataset information

- Run analysis on the datasets using `analysis.py`. To run with small portion of
  the dataset use the `data_info_smol.json`
```
python analysis.py data_info.json
```



