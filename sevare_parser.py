import sys
import argparse
import os
import numpy as np

# SEVARE PARSER 2.0 - adapted to new table forms
# Format of short datatable:
#
# program;c.domain;adv.model;protocol;partysize;comp.time(s);comp.peakRAM(MiB);bin.filesize(MiB);input_size;runtime_internal(s);runtime_external(s);peakRAM(MiB);jobCPU(%);P0commRounds;P0dataSent(MB);ALLdataSent(MB)
#   0         1       2         3         4          5               6                7            8 + n        9 + n                  10 + n          11 + n      12 + n     13 + n

# REQUIREMENTS:
# - The table MUST NOT contain lines with equal values of the variable array (see variable_array) - this only happens
# if the protocol was run multiple times for same parameter values in the same run
# - For 3D plots:

def get_sorting(row):
    return row[sorting_index]


# This function will write the interpolation function at the end of each file contained in file_array
# is_linear indicates if all files should be interpolated linearly or not (true=linear interpolation)
def interpolate_file(file_, degree):
    x = []
    y = []
    # fill up x and y
    d = file_.readlines()
    for lin in range(len(d)):
        dd = d[lin].split('\t')
        x.append(float(dd[0]))
        y.append(float(dd[1][0:len(dd[1])-1]))
    if x == [] or y == []:
        return [0, 0]
    return np.polyfit(x, y, degree)


# Input: protocol, String
# Output: Integer (-1 -> did not find protocol, 0 -> mal_dis, 1 -> mal_hon, 2 -> semi_dis, 3 -> semi_hon)
def get_security_class(protocol):
    protocols_mal_dis = ["mascot", "lowgear", "highgear", "chaigear", "cowgear", "spdz2k", "tinier", "real-bmr"]
    protocols_mal_hon = ["hemi", "semi", "temi", "soho", "semi2k", "semi-bmr", "semi-bin"]
    protocols_semi_dis = ["sy-shamir", "malicious-shamir", "malicious-rep-field", "ps-rep-field", "sy-rep-field",
                          "brain", "malicious-rep-ring",
                          "ps-rep-ring", "sy-rep-ring", "malicious-rep-bin", "malicious-ccd", "ps-rep-bin",
                          "mal-shamir-bmr", "mal-rep-bmr"]
    protocols_semi_hon = ["atlas", "shamir", "replicated-field", "replicated-ring", "shamir-bmr", "rep-bmr",
                          "replicated-bin", "ccd"]
    if protocol in protocols_mal_dis:
        return 0
    if protocol in protocols_mal_hon:
        return 1
    if protocol in protocols_semi_dis:
        return 2
    if protocol in protocols_semi_hon:
        return 3


# ----- ARGUMENTS --------
parser = argparse.ArgumentParser(
    description='This program parses the measurement folder outputted by sevare-bench (version from 11/22).')

parser.add_argument('filename', type=str, help='Required, name of the folder (normally a date).')

parser.add_argument('-s', type=str, required=False,
                    help='(Optional) When set the table will be sorted by this parameter beforehand.')

args = parser.parse_args()

filename = args.filename

if filename[len(args.filename)-1] != '/':
    filename += '/'

# ------- PARSING ---------

# file reader for the database - throws FileNotFoundError if file doesn't exist
f = open(filename + "data/E31_short_results.csv")

if not os.path.exists(filename + "parsed"):
    os.mkdir(filename + "parsed")

info_file_2D = open(filename + "parsed/info2D.txt", "a")

header = f.readline().split(';')

runtime_index = -1
protocol_index = -1
sorting_index = -1

variable_array = ["latencies(ms)", "bandwidths(Mbs)", "packetdrops(%)", "freqs(GHz)", "quotas(%)", "cpus", "input_size"]  # Names from the table!
var_name_array = ["Lat_", "Bdw_", "Pdr_", "Frq_", "Quo_", "Cpu_", "Set_"]  # HAS TO MATCH ABOVE ARRAY - values are hardcoded within script!
var_val_array = [None] * len(variable_array)  # used to store changing variables
index_array = [-1] * len(variable_array)
datafile_array = [None] * len(variable_array)

# Get indexes of demanded columns
for i in range(len(header)):
    # Indexes of variables
    for j in range(len(index_array)):
        if header[i] == variable_array[j]:
            index_array[j] = i

    if header[i] == "runtime_internal(s)":  # Name from the table
        runtime_index = i
    elif header[i] == "protocol":  # Name from the table
        protocol_index = i
    # Sorting index
    if header[i] == args.s:
        sorting_index = i


# Uses simple get_sorting function to sort
if sorting_index != -1:
    dataset_array = sorted(dataset_array, key=get_sorting)

if not os.path.exists(filename + "parsed/2D"):
    os.mkdir(filename + "parsed/2D")

if not os.path.exists(filename + "parsed/3D"):
    os.mkdir(filename + "parsed/3D")

# Create array of dataset
f.readline().split(';')
protocol = ""
protocols = []

dataset = f.readlines()
dataset_array = []
for li in dataset:
    dataset_array.append(li.split(';'))

# - - - - - - - 2D Plotting - - - - - - - -
# Go through dataset for each variable
for i in range(len(index_array)):
    # Only parse for variables that are measured in the table
    if index_array[i] == -1:
        continue

    print(str(i) + " Iteration")
    # If table only contains one protocol
    protocol = None

    for line in dataset_array:
        # Sometimes the last line of the table is \n
        if line[0] == "\n":
            continue

        # When a new protocol is parsed
        if protocol != line[protocol_index]:
            # Update protocol
            protocol = line[protocol_index]
            protocols.append(protocol)

            # Create 2D file descriptor
            datafile2D = open(filename + "parsed/2D/" + var_name_array[i] + protocol + ".txt", "a", 1)

            # Fill up the var_val array with initial values of every other configured parameter - have to be fix (controlled variables)
            for j in range(len(index_array)):
                if index_array[j] != -1 and i != j:
                    var_val_array[j] = line[index_array[j]]
                else:
                    var_val_array[j] = None # may be inefficient
            print(protocol + str(var_name_array[i]) + str(var_val_array))

        # Only parse line when it shows the initial values of controlled variables
        if all((var_val_array[j] is None or var_val_array[j] == line[index_array[j]]) for j in range(len(index_array))):
            datafile2D.write(line[index_array[i]] + '\t' + line[runtime_index] + '\n')
            # TODO: Check if additional file with y=

# - - - - - - 3D PLOTTING - - - - - - -
var_val_array = [None] * len(variable_array)  # reset vars
plot3D_var_combo = [("Set_", "Lat_"), ("Set_", "Bdw_"), ("Lat_", "Frq_"), ("Bdw_", "Frq_"), ("Lat_", "Bdw_"), ("Lat_", "Pdr_"), ("Bdw_", "Pdr_")]

# The dataset is iterated through for all variable combinations
for combo in plot3D_var_combo:
    # Indexes for combo[0] combo[1] in the arrays, in the line array their index is given by index_array[index_x]
    index_0, index_1 = var_name_array.index(combo[0]), var_name_array.index(combo[1])

    protocol = None

    # Make sure both variables from the var combo have measurements in the table
    if index_array[index_0] == -1 or index_array[index_1] == -1:
        continue

    #print(combo[0] + combo[1] + "iteration")
    #print(str(index_array))

    for line in dataset_array:
        # Sometimes the last line of the table is \n
        if line[0] == "\n":
            continue

        # When a new protocol is parsed
        if protocol != line[protocol_index]:
            # Update protocol
            protocol = line[protocol_index]
            protocols.append(protocol)

            # Create file descriptor
            datafile3D = open(filename + "parsed/3D/" + combo[0] + combo[1] + protocol + ".txt", "a", 1)

            # Fill up var_val array with initial values of other configured variables - have to be fixed for a combo (controlled variables)
            for i in range(len(index_array)):
                if (index_array[i] != -1) and (var_name_array[i] != combo[0]) and (var_name_array[i] != combo[1]):
                    print(var_name_array[i] + " and x[0] = " + combo[0] + " and x[1] = " + combo[1])
                    var_val_array[i] = line[index_array[i]]
                else:
                    var_val_array[i] = None # may be inefficient
            #print(protocol + " " + str(var_val_array))
            #print(str(var_name_array))

        # Only take info from lines where the fixed variables have their initial values
        if all((var_val_array[i] is None or var_val_array[i] == line[index_array[i]]) for i in range(len(index_array))):
            datafile3D.write(line[index_array[index_0]] + '\t' + line[index_array[index_1]] + '\t' + line[runtime_index] + '\n')


'''
# ----  INTERPOLATION & WINNER SEARCH -------
# Each array contains winners for each changing variable (<name>,lowest coefficient)
# One array for each security class

winners_mal_dis = [("", 0)] * len(variable_array)
winners_mal_hon = [("", 0)] * len(variable_array)
winners_semi_dis = [("", 0)] * len(variable_array)
winners_semi_hon = [("", 0)] * len(variable_array)

# Get all generated 2D plot files - only files (not directories) were generated in this path
plots2D = os.listdir(filename + "parsed/2D/")
print(plots2D)

# Get generated files
for i in range(len(plots2D)):
    plot = open(filename + "parsed/2D/" + plots2D[i], "r")
    # print(plots2D[i])
    if plots2D[i][0:4] == "Lat_":
        f = interpolate_file(plot, 1)
        # var_name index of Lat_ is 0, use var_name_array.index(plots2D[i][0:4]) if changed

        info_file_2D.write(
            plots2D[i] + " -> f(x) = " + str(f[0]) + "*x + " + str(f[1]) + "\n")
    else:
        f = interpolate_file(plot, 2)
        index = var_name_array.index(plots2D[i][0:4])
        info_file_2D.write(plots2D[i] + " -> f(x) = " + str(f[0]) + "*x**2 + " + str(f[1]) + "*x**1 + " + str(f[2]) + "\n")
    # for j in range(2):  # range has to be degree given in prior line
    #   info_file_2D.write(" " + str(f[j]) + " * x**" + str(j) + " ")

# Find winner


# Parse summary file
# Get set size from database


'''


