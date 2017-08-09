class Mapper:
    '''
    O(N) Diff_Matrix 2 CSV row index mapping.
    Mapping has been made using a dictionary with (N(N-1))/2 entries, one for each row of the diff_matrix.
    Time & space complexity are O(N) 'cause each entry is computed just one time in constant time.
    '''

    CSV_ROWS = None
    '''
    The number of rows (excluding the header) in the CSV file.
    '''
    diff_to_csv = None
    '''
    Dictionary to map from a diff matrix index to the corresponding CSV row index (starting from 0) in the DataFrame.
    '''

    def __init__(self, CSV_ROWS):
        '''
        :param CSV_ROWS: The number of rows (excluding the header) in the CSV file.
        '''
        self.CSV_ROWS = CSV_ROWS
        self.diff_to_csv = {}
        number_of_groups = self.CSV_ROWS - 1

        global_index = 0
        for group in range(0, number_of_groups):
            group_diff_rows = CSV_ROWS - group - 1
            current_real = real_zero = CSV_ROWS - group_diff_rows

            for local_index in range(0, group_diff_rows):
                self.diff_to_csv[global_index] = current_real
                global_index += 1
                current_real += 1
