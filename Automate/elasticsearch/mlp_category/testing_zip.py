
from zipfile import ZipFile
import pandas as pd
from pandas.core.base import DataError

with ZipFile("/automate/elasticsearch/mlp_category/te_600_9Cat_df_term_doc.zip", 'r') as fzip:
    data = fzip.read("te_600_9Cat_df_term_doc.csv")
    header = pd.read_csv(data, header=0, nrows=1)
    print(header)