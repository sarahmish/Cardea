from __future__ import absolute_import
import pandas as pd

class fhirbase(object):
    
    def set_attributes(self, dict_values):
        for attr,_ in self.__dict__.items():
            if attr in dict_values.keys():
                self.__dict__[str(attr)] = dict_values[str(attr)]

    def get_dataframe(self):
        dataframe = {}
        for attr, value in self.__dict__.items():
            if value is not None and attr != 'resourceType':
                dataframe[attr] = value

        return pd.DataFrame(dataframe)

    def assert_type(self):
        pass

    def get_relationships(self):
        return []