import sys
import argparse
import os
import numpy as np
from scipy.optimize import curve_fit

import re
import glob

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


# Reads 2D data file and returns the x and y datapoints in arrays
def read_file(file_):
    x = []
    y = []
    d = None
    # fill up x and y
    d = file_.readlines()
    # print(d)
    for lin in range(len(d)):
        dd = d[lin].split('\t')
        x.append(float(dd[0]))
        y.append(float(dd[1][0:len(dd[1]) - 1]))
    return x, y


# This function will write the interpolation function at the end of each file contained in file_array
# is_linear indicates if all files should be interpolated linearly or not (true=linear interpolation)
def interpolate_file(file_, degree, comm_rounds="nothing"):
    x, y = read_file(file_)
    if x == [] or y == []:
        return [0, 0]

    if len(x) < 5:
        print("Not enough datapoints")
        return [-1, -1]

    #if comm_rounds != "nothing":
    #    x = [el * comm_rounds for el in x]

    return np.polyfit(x, y, degree)


def interpolate_exponential(file_):
    x, y = read_file(file_)
    if x == [] or y == []:
        return [0, 0]

    #print(x[0])
    # print(y[0])

    if len(x) < 5:
        return [-1, -1]

    popt, pcov = curve_fit(lambda t, a, b, c: a * np.exp(b * t) + c, x, y)
    return popt


def interpolate_inverse(file_, data_sent="nothing"):
    x, y = read_file(file_)
    if x == [] or y == []:
        return [0, 0]

    if len(x) < 5:
        return [-1, -1]

    if data_sent == "nothing":
        popt, pcov = curve_fit(lambda t, a, b: a / t + b, x, y)
    else:
        popt, pcov = curve_fit(lambda t, b: (a * data_sent) / t + b, x, y)

    # popt, pcov = curve_fit(lambda t, a, b, c: a * np.exp(b * t) + c, x.reverse(), y)
    # popt, pcov = curve_fit(lambda t, a, b, c: a*t**2 + b*t + c, x, y)

    '''
        if data_sent != "nothing":
            x = [el / data_sent for el in x]

    return np.polyfit(x, y, degree)
    '''
    # We do not need the estimated covariance of popt
    return popt


# Input: protocol, String
# Output: Integer (-1 -> did not find protocol, 0 -> mal_dis, 1 -> mal_hon, 2 -> semi_dis, 3 -> semi_hon)
def get_security_class(prot):
    protocols_mal_dis = ["mascot", "lowgear", "highgear", "chaigear", "cowgear", "spdz2k", "tinier", "real-bmr"]
    protocols_mal_hon = ["hemi", "semi", "temi", "soho", "semi2k", "semi-bmr", "semi-bin"]
    protocols_semi_dis = ["sy-shamir", "malicious-shamir", "malicious-rep-field", "ps-rep-field", "sy-rep-field",
                          "brain", "malicious-rep-ring", "yao", "yaoO",
                          "ps-rep-ring", "sy-rep-ring", "malicious-rep-bin", "malicious-ccd", "ps-rep-bin",
                          "mal-shamir-bmr", "mal-rep-bmr"]
    protocols_semi_hon = ["atlas", "shamir", "replicated-field", "replicated-ring", "shamir-bmr", "rep-bmr",
                          "replicated-bin", "ccd"]
    if prot in protocols_mal_dis:
        return 0
    if prot in protocols_mal_hon:
        return 1
    if prot in protocols_semi_dis:
        return 2
    if prot in protocols_semi_hon:
        return 3
    else:
        print("ERROR: Protocol is was not recognized")


def get_security_class_name(class_nb):
    if class_nb == 0:
        return "Malicious, Dishonest Majority"
    if class_nb == 1:
        return "Malicious, Honest Majority"
    if class_nb == 2:
        return "Semi-Honest, Dishonest Majority"
    if class_nb == 3:
        return "Semi-Honest, Honest Majority"


# Adds empty lines to a 3D datafile each time the x coordinate changes
def add_empty_lines(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    with open(file_path, 'w') as file:
        previous_x = lines[0].split('\t')[0]
        for line_ in lines:
            # print(line)
            x_, y_, z_ = line_.split('\t')
            if x_ != previous_x:
                file.write('\n')
            file.write(line_)
            previous_x = x_


# ----- ARGUMENTS --------
parser = argparse.ArgumentParser(
    description='This program parses the measurement folder outputted by sevare-bench (version from 11/22).')

parser.add_argument('filename', type=str, help='Required, name of the test-run folder (normally a date).')

parser.add_argument('-s', type=str, required=False,
                    help='(Optional) When set the table will be sorted by this parameter beforehand.')

args = parser.parse_args()

filename = args.filename

if filename[len(args.filename)-1] != '/':
    filename += '/'

# ------- PARSING ---------

# Open datatable
files = [f for f in os.listdir(filename + "data/") if f.endswith(".csv") and "full" in f]
if len(files) > 0:
    print("Found full results table...")
    f = files[0]
else:
    files = [f for f in os.listdir(filename + "data/") if f.endswith(".csv") and "short" in f]
    if len(files) > 0:
        print("Found short results table...")
        f = files[0]
    else:
        print("Could neither find a short or a full results table in the data/ directory.")
        exit()

f = open(filename + "data/" + f)

if not os.path.exists(filename + "parsed"):
    os.mkdir(filename + "parsed")

interpolations_file_2D = open(filename + "parsed/interpolations2D.txt", "a")
info_file = open(filename + "parsed/protocols_infos.txt", "a")

header = f.readline().split(';')

runtime_index = -1
protocol_index = -1
sorting_index = -1

comm_rounds_index = -1
data_sent_index = -1

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

    if header[i] == "runtime_internal(s)" or header[i] == "runtime(s)":  # Name from the table
        runtime_index = i
    elif header[i] == "protocol":  # Name from the table
        protocol_index = i
    # Sorting index
    elif header[i] == args.s:
        sorting_index = i
    # Metrics indexes
    elif header[i] == "P0commRounds":
        comm_rounds_index = i
    elif header[i] == "ALLdataSent(MB)":  # "P0dataSent(MB)"
        data_sent_index = i

# Uses simple get_sorting function to sort
# if sorting_index != -1:
#    dataset_array = sorted(dataset_array, key=get_sorting)

if not os.path.exists(filename + "parsed/2D"):
    os.mkdir(filename + "parsed/2D")

if not os.path.exists(filename + "parsed/3D"):
    os.mkdir(filename + "parsed/3D")

# Create array of dataset
protocol = ""
protocols = []
comm_rounds_array = []
data_sent_array = []

dataset = f.readlines()
f.close()
dataset_array = []
for li in dataset:
    dataset_array.append(li.split(';'))

# get highest input value from summary
maxinput = -1
with open(glob.glob(filename + "E*-run-summary.dat")[0], "r") as f:
    for line in f:
        match = re.search(r"Inputs.*", line)
        if match:
            maxinput = match.group(0).split(" ")[-1]
            break

# - - - - - - - Parsing for 2D plots - - - - - - - -
print("Starting 2D plotting.")
# Go through dataset for each variable
# print(index_array)
for i in range(len(index_array)):
    # Only parse for variables that are measured in the table
    if index_array[i] == -1:
        continue

    # print(str(i) + " Iteration")
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
                    var_val_array[j] = None  # may be inefficient
            # print(protocol + str(var_name_array[i]) + str(var_val_array))

            # We want the maximum set size value in the var_val_array
            var_val_array[-1] = maxinput

            # Fill up metrics arrays
            prot_comm_rounds = line[comm_rounds_index]
            if prot_comm_rounds[0] == "~":
                prot_comm_rounds = prot_comm_rounds[1:]
            elif "NA" in prot_comm_rounds:
                prot_comm_rounds = -1
            comm_rounds_array.append(float(prot_comm_rounds))

            prot_data_sent = line[data_sent_index]
            if "NA" in prot_data_sent:
                prot_data_sent = 0
            elif prot_data_sent.endswith("\n"):
                prot_data_sent = prot_data_sent[:-1]
            data_sent_array.append(float(prot_data_sent))

        # Only parse line when it shows the initial values of controlled variables
        if all((var_val_array[j] is None or var_val_array[j] == line[index_array[j]]) for j in range(len(index_array))):
            datafile2D.write(line[index_array[i]] + '\t' + line[runtime_index] + '\n')
            # TODO: Check if additional file with y=

datafile2D.close()

# - - - - - - 3D PLOTTING - - - - - - -
print("Starting 3D plotting.")
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
                    # print(var_name_array[i] + " and x[0] = " + combo[0] + " and x[1] = " + combo[1])
                    var_val_array[i] = line[index_array[i]]
                else:
                    var_val_array[i] = None  # may be inefficient
            #print(protocol + " " + str(var_val_array))
            #print(str(var_name_array))

        # Only take info from lines where the fixed variables have their initial values
        if all((var_val_array[i] is None or var_val_array[i] == line[index_array[i]]) for i in range(len(index_array))):
            datafile3D.write(line[index_array[index_0]] + '\t' + line[index_array[index_1]] + '\t' + line[runtime_index] + '\n')

    add_empty_lines(filename + "parsed/3D/" + combo[0] + combo[1] + protocol + ".txt")

# Add empty lines to the data files for latex
#plots3D = os.listdir(filename + "parsed/3D/")
#for plot3D in plots3D:
#    add_empty_lines(filename + "parsed/3D/" + plot3D)

# ----  INTERPOLATION & WINNER SEARCH for 2D experiments -------
print("Starting interpolation and winner search.")

# winners is a two dimensional array
# The first dimension gives the security class: 0 -> mal_dis, 1 -> mal_hon, 2 -> semi_dis, 3 -> semi_hon
# The second dimension gives the variable (indexes analog to var_name_array) for which the winner is stored
# Each element is a tuple: (<protocol_name>, best coefficient)

winners = [None] * 4
for i in range(4):
    winners[i] = [None] * len(variable_array)
    for j in range(len(variable_array)):
        winners[i][j] = ["", sys.maxsize]
# print(winners)

# Get all generated 2D plot files - only files (not directories) were generated in this path
plots2D = os.listdir(filename + "parsed/2D/")

# Interolate generated files
for i in range(len(plots2D)):
    plot = open(filename + "parsed/2D/" + plots2D[i], "r")
    plot_type = plots2D[i][0:4]  # String

    # Reparse protocol name from file name - may be optimisable
    protocol = plots2D[i][4:(len(plots2D[i])-4)]
    # print("Interpolating " + protocol + "... ")

    prot_comm_rounds = comm_rounds_array[protocols.index(protocol)]  # Array contains floats
    prot_data_sent = data_sent_array[protocols.index(protocol)]  # Array contains floats

    if plot_type == "Lat_":
        # f = interpolate_file(plot, 1)
        f = interpolate_file(plot, 1, prot_comm_rounds)  # Using 3rd argument of function
        # var_name index of Lat_ is 0, use var_name_array.index(plots2D[i][0:4]) if changed
        interpolations_file_2D.write(plots2D[i] + " -> f(x) = " + str(f[0]) + "*x + " + str(f[1]) + "\n")
        f[0] = f[0] / prot_comm_rounds
        info_file.write(plots2D[i] + " -> " + str(f[0]) + " with " + str(prot_comm_rounds) + "\n")

    elif plot_type == "Pdr_":
        # f has the form a*e^(b*x) + c
        f = interpolate_exponential(plot)
        if f[0] == -1 and f[1] == -1:
            interpolations_file_2D.write(plots2D[i] + " -> not enough datapoints.\n")
            continue
        else:
            interpolations_file_2D.write(plots2D[i] + " -> f(x) = " + str(f[0]) + "*e^(" + str(f[1]) + "*x) + " + str(f[2]) + "\n\n")

    elif plot_type == "Bdw_":
        # f has the form a/x + b
        f = interpolate_inverse(plot)
        if f[0] == -1:
            interpolations_file_2D.write(plots2D[i] + " -> not enough datapoints.\n")
            continue
        else:
            if f[0] < 0:
                interpolations_file_2D.write(plots2D[i] + " -> error: preprocessing phase\n")  # See remark in README.md
                continue
            interpolations_file_2D.write(plots2D[i] + " -> f(x) = " + str(f[0]) + "/x + " + str(f[1]) + "\n")
            f[0] = f[0] * prot_data_sent    # find correlation
            info_file.write(plots2D[i] + " -> " + str(f[0]) + " with " + str(prot_data_sent) + "\n\n")

    elif plot_type == "Set_":
        continue

    else:
        f = interpolate_file(plot, 2)
        # print(f)
        if f[0] == -1 and f[1] == -1:
            interpolations_file_2D.write(plots2D[i] + " -> not enough datapoints.\n")
        else:
            interpolations_file_2D.write(plots2D[i] + " -> f(x) = " + str(f[0]) + "*x**2 + " + str(f[1]) + "*x**1 + " + str(f[2]) + "\n")
    # for j in range(2):  # range has to be degree given in prior line
    #   interpolations_file_2D.write(" " + str(f[j]) + " * x**" + str(j) + " ")

    first_index = get_security_class(protocol)
    second_index = var_name_array.index(plot_type)  # Int

    # For each variable, a lower first coefficient means a runtime function that indicates a more effective protocol
    if winners[first_index][second_index][1] > f[0]:
        winners[first_index][second_index][0] = protocol
        winners[first_index][second_index][1] = f[0]

    #print(winners[0])
    #print(winners[1])
    #print(winners[2])
    #print(winners[3])

    # Wrap up iteration
    plot.close()

# Write all winners in table
interpolations_file_2D.write("\n\n\nProtocol Winners:\n\n")
# Go through security class
for i in range(4):
    interpolations_file_2D.write(get_security_class_name(i) + " protocols:\n")
    for j in range(len(winners[i])):
        if winners[i][j][0] == "" or winners[i][j][1] == -1:
            continue
        interpolations_file_2D.write("- " + winners[i][j][0] + " was best for " + var_name_array[j] + " with a coefficient of: " + str(winners[i][j][1]) + "\n")

# Write list of winners for plotter parsing
interpolations_file_2D.write("\nWinners:\n")

# For all variables
for j in range(len(winners[i])):
    # If the array does not contain a value for a variable for one security class, it won't contain values for that
    # same variable for other security classes
    if all((winners[h][j][0] == '') for h in range(4)):
        continue
    # TODO: empty rows for a variable still get put into the file
    interpolations_file_2D.write(var_name_array[j] + ":")

    for i in range(4):
        #print(winners[i])
        if winners[i][j][1] != -1:
            interpolations_file_2D.write(winners[i][j][0]+",")
    interpolations_file_2D.write("\n")

# Parse summary file
# Get set size from database


# - - - - - - Finish - - - - - -
datafile3D.close()
interpolations_file_2D.close()
info_file.close()
