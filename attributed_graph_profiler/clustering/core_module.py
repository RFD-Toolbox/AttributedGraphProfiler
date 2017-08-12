import sys
import os
import pandas as pandas
import numpy as np
from attributed_graph_profiler.clustering.mapping import Mapper


class core_module:
    rfds = None
    diff_function = None
    groups = None
    mapping_dict = None
    csv_data_frame = None
    csv_headers = None

    def __init__(self, rfds, groups, mapping_dict, csv_data_frame):
        self.rfds = rfds
        self.groups
        self.mapping_dict = mapping_dict
        self.csv_data_frame = csv_data_frame
        diff = lambda l1, l2: [x for x in l1 if x not in l2]
        csv_headers = list(csv_data_frame)

    def __run(self):
        for rfd_dic in self.rfds:
            print("RFD:", rfd_dic)
            self.__rfd_core(rfd_dic)

    def __rfd_core(self, rfd_dic):
        keys = rfd_dic.keys()
        print("Keys:", keys)
        rhs_header_value = self.diff_function(self.csv_headers, keys)
        print("RHS_Header:", rhs_header_value[0])
        length = len(rhs_header_value)
        rfd_dic[rhs_header_value[0]] = rfd_dic.pop("RHS")
        print("RFD after POP:", rfd_dic)

        for key, group in self.groups.items():
            print("\nGroup{}\n".format(key), group)
            self.__group_core(key, group, rfd_dic)

    def __group_core(self, key, group, rfd_dic):
        print("\nGroup{}\n".format(key), group)

        query = ' and '.join(['{} <= {}'.format(k, v) for k, v in rfd_dic.items() if not np.isnan(v)])
        my_set = group.query(query)

        print("SET{}\n".format(key), my_set)
        set_indexes = my_set.index.tolist()
        print("Set_Indexes:", set_indexes)

        mapped_set_indexes = list()
        mapped_set_indexes.append(key)
        for index in set_indexes:
            mapped_set_indexes.append(self.mapping_dict[index])

        print("MappedSetIndexes:", mapped_set_indexes)

        for row in mapped_set_indexes:
            print(pandas.DataFrame(self.csv_data_frame.loc[row]).T)
