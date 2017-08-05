import sys
import getopt
import utils.utils as ut
import pandas as pd
import numpy as np
from loader.distance_mtr import DiffMatrix
from dominance.dominance_tools import RFDDiscovery


class RFDExtractor:
	args = None
	debug_mode = False
	'''Command-Line arguments.'''
	separator_character = None
	'''The character used to separate values within the CSV file.'''
	csv_file = None
	'''The CSV file path.'''
	has_header = None
	semantic = None
	has_date_time = None
	'''Columns containing date-time values.'''
	missing = None
	index_column = None
	human_readable = None
	# ==========================================================================
	half_sides_specifications = None
	distance_matrix = None
	rfd_data_frame_list = None
	rfd_dictionary_list = None

	def __init__(self, args, debug_mode=False) -> None:
		super().__init__()
		self.args = args
		self.debug_mode = debug_mode
		self.separator_character, self.csv_file, self.has_header, self.semantic, self.has_date_time, self.missing, \
		self.index_column, self.human_readable, self.half_sides_specifications = self.extract_args(self.args)

		try:
			self.check_correctness(self.has_date_time, self.half_sides_specifications, self.index_column)
		except getopt.GetoptError as gex:
			self.usage()
			print(str(gex))
			sys.exit(1)
		except AssertionError as aex:
			self.usage()
			print(str(aex))
			sys.exit(1)

		if self.half_sides_specifications is None:
			self.usage()
		elif isinstance(self.half_sides_specifications, list):
			if isinstance(self.has_header, int) and not self.has_header:
				self.distance_matrix = DiffMatrix(self.csv_file,
												  sep=self.separator_character,
												  index_col=self.index_column,
												  semantic=self.semantic,
												  missing=self.missing,
												  datetime=self.has_date_time)
			else:  # has header
				self.distance_matrix = DiffMatrix(self.csv_file,
												  sep=self.separator_character,
												  first_col_header=self.has_header,
												  semantic=self.semantic,
												  index_col=self.index_column,
												  missing=self.missing,
												  datetime=self.has_date_time)

			self.rfd_data_frame_list = list()
			for combination in self.half_sides_specifications:
				combination_distance_matrix = self.distance_matrix.split_sides(combination)
				'''with ut.timeit_context("RFD Discover time for Combination {}".format(str(combination))):'''
				rfd_discovery = RFDDiscovery(combination_distance_matrix)
				self.rfd_data_frame_list.append(
					rfd_discovery.get_rfds(rfd_discovery.standard_algorithm, combination))

				if self.debug_mode:
					print("\nCombination:", combination)
					if self.human_readable:
						self.print_human(self.rfd_data_frame_list[-1])
					else:
						print(self.rfd_data_frame_list[-1])

	def __str__(self) -> str:
		return "{}\n\t{}\n\t{}\n\t{}\n\t{}\n\t{}\n\t{}\n\t{}\n\t{}\n\t{}\n" \
			.format(self.__class__.__name__,
					"args: {}".format(self.args)
					, "separator_character: {}".format(self.separator_character)
					, "csv_file: {}".format(self.csv_file)
					, "has_header: {}".format(self.has_header)
					, "semantic: {}".format(self.semantic)
					, "has_date_time: {}".format(self.has_date_time)
					, "missing: {}".format(self.missing)
					, "index_column: {}".format(self.index_column)
					, "human_readable: {}".format(self.human_readable)
					)

	# delegate methods
	def extract_args(self, args):
		"""
		Given the list of command line parameters, it extracts the parameters given according to the format
		described in the Usage section of the README.
		If some parameter cannot be interpreted, then the function will raise an AssertionError.
		If the path of the CSV is missing or is not valid, the programm will print an error message and it will end.
		With the help option, it will print on the standard output the help about the execution of this program.
		:param args: list of command line argument given at the startup
		:type args: list
		:return: list of parameters extracted
		:rtype: tuple
		:raise: AssertionError
		"""
		try:
			# Default values
			c_sep, has_header, semantic, has_dt, missing, ic, human = '', 0, True, False, "?", False, False
			csv_file = ''
			left_half_side = []
			right_half_side = []
			options, args = getopt.getopt(args, "c:r:l:s:hm:d:vi:", ["semantic", "help", "human"])
			for option, arg in options:
				if option == '-v':
					print("rdf-discovery version 0.0.1")
					sys.exit(0)
				if option == '-c':
					csv_file = arg
				elif option == '-r':
					right_half_side = [int(arg)]
					if len(right_half_side) > 1:
						print("You can specify at most 1 RHS attribute")
						sys.exit(-1)
				elif option == '-l':
					left_half_side = [int(_) for _ in arg.split(',')]
				elif option == '-s':
					c_sep = arg
				elif option == '-h':
					has_header = 0
				elif option == '--semantic':
					semantic = True
				elif option == '-m':
					missing = arg
				elif option == '-d':
					has_dt = [int(_) for _ in arg.split(',')]
				elif option == '-i':
					ic = int(arg)
				elif option == '--human':
					human = True
				elif option == '--help':
					self.usage()
					sys.exit(0)
				else:
					assert False, "unhandled option"
		except getopt.GetoptError as getopt_err:
			print(getopt_err)
			self.usage()
			sys.exit(2)
		except TypeError as t_err:
			print("Error while trying to convert a string to numeric: {}".format(str(t_err)))
			sys.exit(-1)
		except Exception as ex:
			print("Error while trying to extract arguments: {}".format(str(ex)))
			sys.exit(-1)
		# understanding
		try:
			c_sep_, has_header_ = self.extract_sep_n_header(c_sep, csv_file, has_header)
			if c_sep == '':
				c_sep = c_sep_
			if has_header is None:
				has_header = has_header_
			cols_count = ut.get_cols_count(csv_file, c_sep)
			half_sides_specifications = self.extract_hss(cols_count, left_half_side, right_half_side)
		except Exception as ex:
			print("Error while trying to understand arguments: {}".format(str(ex)))
			sys.exit(-1)
		return c_sep, csv_file, has_header, semantic, has_dt, missing, ic, human, half_sides_specifications

	def extract_hss(self, cols_count, lhs, rhs):
		# You cannot have len(rhs) > 1, don't check it
		"""
		Given the lhs and rhs from the command line parameters, and the column's number of the dataset,
		it creates various combinations of rhs and lhs according to the format of this two parameters.
		If the format of this two parameters is not accordant with the possible combination on rhs and lhs in the
		command line arguments described by the README, the program will print an error message and it will end.
		The program return a list of dict, where each dict contains the indexes of the attributes on the lhs with the key
		'lhs' and the index of the attribute on the rhs with the key 'rhs'.
		:param cols_count: the column's number
		:type cols_count: int
		:param lhs: list of a valid columns' indexes containing the dataset's attributes positioned in the lhs
		:type lhs: list
		:param rhs: list of a valid column's index containing the dataset's attribute positioned in the rhs
		:type rhs: list
		:return: one or more combination of attribute in the rhs and lhs
		:rtype: list
		"""
		if rhs == [] and lhs == []:  # each combination case
			hss = ut.get_hs_combination(cols_count)
		elif rhs == [] and not lhs == []:  # error case
			print("You have to specify at least one RHS attribute")
			sys.exit(-1)
		elif not rhs == [] and lhs == []:  # only rhs specified case
			cols_index = list(range(cols_count))
			if not rhs[0] in cols_index:
				print("RHS index is out of bound. Specify a valid value")
				sys.exit(-1)
			hss = list()
			hss.append({'rhs': rhs, 'lhs': cols_index[:rhs[0]] + cols_index[rhs[0] + 1:]})
		else:
			hss = list()
			hss.append({'rhs': rhs, 'lhs': lhs})
		return hss

	def extract_sep_n_header(self, c_sep, csv_file, has_header):
		"""
		Given a correct path to a CSV file containing the dataset, the separator and the presence or not of the header
		given by the command line arguments, this function will try to infer the separator and/or the presence
		of the header in the dataset if they was not specified in the command line arguments.
		:param c_sep: the separator extracted from the command line argument
		:type c_sep: str
		:param csv_file: a correct path to a CSV file containing a valid dataset
		:type csv_file: str
		:param has_header: indicate the presence or not of a column header in the CSV
		:type has_header: int
		:return: the separator used in the CSV and the value 0 if the CSV has an header, None otherwise
		:rtype: tuple
		"""
		if c_sep == '' and has_header is None:
			c_sep, has_header = ut.check_sep_n_header(csv_file)
		elif c_sep != '' and has_header is None:
			has_header = ut.check_sep_n_header(csv_file)[1]
		elif c_sep == '' and has_header is not None:
			c_sep = ut.check_sep_n_header(csv_file)[0]
		return c_sep, has_header

	def check_correctness(self, has_dt, hss, index_col):
		"""
		Verify the correctness of the columns' indexes given for the division in
		rhs and lhs and of the index indicating the key's column.
		If some index is out of bound, the function will raise an getopt.GetoptError.
		If there are some indexes repeated, the program will raise an AssertionError.
		:param has_dt: value containing indexes of columns containing date, False otherwise
		:type has_dt: list or bool
		:param hss: dict containing the division in rhs and lhs
		:type hss: dict
		:param index_col: index of the column containing the dataset's primary key
		:type index_col: int
		:raises getopt.GetoptError, AssertionError
		"""
		max_index = max(hss[0]['rhs'] + hss[0]['lhs'])
		unique_index_count = sum([1 for i in set(hss[0]['rhs'] + hss[0]['lhs'])])
		# check has header
		if index_col:
			if index_col < 0:
				raise AssertionError("Index of a column cannot be less than 0")
			if index_col > max_index and len(hss[0]['lhs']) >= 1:
				raise getopt.GetoptError("Index col is out of bound")
		# check date
		if has_dt is not False:
			if max(has_dt) > max_index and len(hss[0]['lhs']) >= 1:
				raise getopt.GetoptError("Datetime index is out of bound")
		# check non repeated index
		index_count = sum([1 for i in hss[0]['rhs'] + hss[0]['lhs']])
		if index_count != unique_index_count:
			raise AssertionError("Repeated index error")

	def usage(self):
		"""
		Print the usage message, describing the correct format for a correct program execution. For each
		argument in the command line arguments, the message will show a short description of it.
		"""
		usage_str = """
	    python {} -c <csv-file> [options]

	    -c <your-csv>: is the path of the dataset on which you want to discover RFDs;
	    Options:

	    -v : display version number;
	    -s <sep>: the separation char used in your CSV file. If you don't provide this, rfd-discovery tries to infer it for you;
	    -h: Indicate that CSV file has the header row. If you don't provide this, rdf-discovery tries to infer it for you.
	    -r <rhs_index>: is the column number of the RHS attribute. It must be a valid integer.
	            You can avoid to specify it only if you don't specify LHS attributes (we'll find RFDs using each attribute as RHS and the remaining as LHS);
	    -l <lhs_index_1, lhs_index_2, ...,lhs_index_k>: column index of LHS' attributes indexes separated by commas (e.g. 1,2,3). You can avoid to specify them:
	            if you don't specify RHS' attribute index we'll find RFDs using each attribute as RHS and the remaining as LHS;
	            if you specify a valid RHS index we'll assume your LHS as the remaining attributes;
	    -i <index_col>: the column which contains the primary key of the dataset.
	            Specifying it, this will not calculate as distance. NOTE: index column should contains unique values;
	    -d <datetime columns>: a list of columns, separated by commas, which values are in datetime format.
	            Specifying this, rfd-discovery can depict distance between two date in time format (e.g. ms, sec, min);
	    --semantic: use semantic distance on Wordnet for string; For more info here;
	    --human: print the RFDs to the standard output in a human readable form;
	    --help: show help. \n
	    """
		print(usage_str.format(sys.argv[0]))

	def print_human(self, rfd_data_frame: pd.DataFrame):
		"""
		Given a valid pandas data frame containing the found RFDs, it prints this RFDs on the standard output in a human readable
		form using the following format:
		attr1(<=threshold1),..., attrn(<=thresholdn) -> RHS(<=rhs_threshold)
		:param rfd_data_frame: data frame containing the RFDs
		:type rfd_data_frame: pandas.core.frame.DataFrame
		"""
		string = ""
		for index, row in rfd_data_frame.iterrows():
			string += "".join(
				["" if np.isnan(row[col]) else "{}(<= {}), ".format(rfd_data_frame.columns[col],
																	round(row[col], ndigits=2))
				 # it starts from 1 and not 0 'cause at position 0 there is the RHS
				 for col in range(1, len(row))
				 ]
			)

			string += "-> {}(<= {})".format(rfd_data_frame.columns[0], round(row[0], ndigits=2))
			string += "\n"
		print(string)

	def get_rfd_dictionary_list(self):
		if self.rfd_dictionary_list is None:
			self.rfd_dictionary_list = list()

			for rfd_data_frame in self.rfd_data_frame_list:
				for _, row in rfd_data_frame.iterrows():
					rfd_dictionary = {}
					for col in range(0, len(row)):
						rfd_dictionary[rfd_data_frame.columns[col]] = round(row[col], ndigits=2)

					self.rfd_dictionary_list.append(rfd_dictionary)

		return self.rfd_dictionary_list
