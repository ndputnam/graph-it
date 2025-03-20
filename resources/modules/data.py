from ast import literal_eval
from copy import deepcopy
from os import listdir
from typing import Tuple, Union

import numpy as np
from numpy import array
from pandas import DataFrame
from pyarrow.parquet import read_table


class Data:
    def __init__(self, base_data):
        """
        Manage plot map data,
         of a Pandas Dataframe,
         or dictionary of Numpy arrays,
         from a saved parquet file.
        """
        from resources.modules.utility import save_data_as_parquet
        self.save_pqt = save_data_as_parquet
        self.pqt_sources:list[str] = self.update_dict()
        self.formated_data:DataFrame = base_data

    def update_dict(self) -> list[str]:
        """
        Load the names of all saved parquet data files into a reference dictionary.
        :return: List of parquet sources available.
        """
        self.pqt_sources = [pqt[:-4] for pqt in listdir('saved/data')]
        self.pqt_sources.insert(0, '')
        return self.pqt_sources

    def get_df(self, pqt_id:int) -> Tuple[Union[DataFrame, dict[np.ndarray]], str]:
        """
        Create plot map data,
         of a Pandas Dataframe,
         or dictionary of Numpy arrays,
         from module dict.
        :param pqt_id: Index reference of parquet data source name.
        :return: Data: Pandas Dataframe or dict of Numpy arrays.
                 Name: Name of parquet data source without file extension.
        """
        name = self.pqt_sources[pqt_id]
        table = read_table('saved/data/%s.pqt' % name)
        meta = {key.decode(): value.decode() for key, value in table.schema.metadata.items()}
        np_shape = literal_eval(meta['shape'])
        if np_shape:
            np_dict = table.to_pydict()
            i = 0
            print('shape in get df in data: %s' % np_shape)
            for col in np_dict:
                np_dict[col] = array(np_dict[col]).reshape(np_shape[i])
                i += 1
            return np_dict, name
        else:
            df = table.to_pandas()
            return df, name

    def merge_dfs(self, df1:DataFrame, df2:DataFrame, on_column:str) -> Union[DataFrame, None]:
        """
        Combine two Dataframes,
         on a specific column,
         with a defined how method.
        :param df1: Primary data from plot map.
        :param df2: Additional data wanting to merge with.
        :param on_column: Common column between both data objects to be merged on.
        :return: If not failed, new Pandas Dataframe that has been merged
        """
        if isinstance(df1, DataFrame) and isinstance(df2, DataFrame):
            df = df1.merge(df2, on=on_column, how='outer')
            self.save_pqt(df, 'modified_data')
            return df
        return None

    def set_upper_range(self, column:str, limit:int):
        """
        Limit formated data to a specific size.
        Can be applied to a specific column or to the whole Dataframe.
        :param column: If given, column to limit.
        :param limit: Length to limit to.
        """
        if column in ['All Columns', '']:
            self.formated_data = self.formated_data.copy().head(limit)
        else:
            self.formated_data[column] = self.formated_data[column].copy().head(limit)

    def save_formated(self, name:str) -> DataFrame:
        """
        Saves formated data to a parquet data source.
        :param name: Name for data source to be saved as.
        :return: Copy of formated data.
        """
        self.save_pqt(self.formated_data, name)
        return deepcopy(self.formated_data)