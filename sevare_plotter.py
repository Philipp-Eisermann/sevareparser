import argparse
import os
import matplotlib.pyplot as plt


# SEVARE PLOTTER
# Will create a /plotted directory and write everything in there
# A folder is created for each variable combination type ("<var_name>*_) contained in /parsed
# In these folders a plot (.tex & .pdf) for each security class (if represented by at least 1 protocol) will be created


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


# Input: protocol, String
# Output: Integer (-1 -> did not find protocol, 0 -> mal_dis, 1 -> mal_hon, 2 -> semi_dis, 3 -> semi_hon)
def get_security_class(prot):
    protocols_mal_dis = ["mascot", "lowgear", "highgear", "chaigear", "cowgear", "spdz2k", "tinier", "real-bmr"]
    protocols_mal_hon = ["sy-shamir", "malicious-shamir", "malicious-rep-field", "ps-rep-field", "sy-rep-field",
                          "brain", "malicious-rep-ring", "ps-rep-ring", "sy-rep-ring", "malicious-rep-bin",
                         "malicious-ccd", "ps-rep-bin", "mal-shamir-bmr", "mal-rep-bmr"]
    protocols_semi_dis = ["hemi", "semi", "temi", "soho", "semi2k", "semi-bmr", "semi-bin"]
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


def get_security_class_name(class_nb):
    if class_nb == 0:
        return "Malicious, Dishonest Majority"
    if class_nb == 1:
        return "Malicious, Honest Majority"
    if class_nb == 2:
        return "Semi-Honest, Dishonest Majority"
    if class_nb == 3:
        return "Semi-Honest, Honest Majority"


# Input: protocol, String
# Output: Integer (-1 -> did not find protocol, 0 -> mal_dis, 1 -> mal_hon, 2 -> semi_dis, 3 -> semi_hon)
def get_security_class(prot):
    protocols_mal_dis = ["mascot", "lowgear", "highgear", "chaigear", "cowgear", "spdz2k", "tinier", "real-bmr"]
    protocols_mal_hon = ["hemi", "semi", "temi", "soho", "semi2k", "semi-bmr", "semi-bin"]
    protocols_semi_dis = ["sy-shamir", "malicious-shamir", "malicious-rep-field", "ps-rep-field", "sy-rep-field",
                          "brain", "malicious-rep-ring",
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

    return "error"


# Is used to generate the axis labels of plots
def get_name(prefix_):
    prefix_names = ["Latency (ms)", "Bandwidths (Mbit/s)", "Packet Loss (%)", "Frequency (GHz)", "Quotas(%)",
                    "CPU Threads", "Input Size"]  # Axis names
    prefixes_ = ["Lat_", "Bdw_", "Pdr_", "Frq_", "Quo_", "Cpu_", "Set_"]

    if prefix_ in prefixes_:
        return prefix_names[prefixes_.index(prefix_)]
    return prefix_


# - - - - - - - - - - ARGUMENTS - - - - - - - - -

parser = argparse.ArgumentParser(
    description='This program plots the results parsed by sevare parser.')

parser.add_argument('filename', type=str,
                    help='Required, name of the test-run folder (usually of the form MONTH-YEAR).')

args = parser.parse_args()

filename = args.filename

if filename[len(args.filename) - 1] != '/':
    filename += '/'

colors = ['black', 'blue', 'brown', 'cyan', 'darkgray', 'gray', 'green', 'lightgray', 'lime', 'magenta', 'olive',
          'orange', 'pink', 'purple', 'red', 'teal', 'violet', 'white', 'yellow']

# Create directories
os.mkdir(filename + "plotted/")
os.mkdir(filename + "plotted/2D")

# - - - - - - - - CREATE 2D PLOTS - - - - - - - - - - -

data_names = os.listdir(filename + "parsed/2D/")

prefixes = []  # will contain the variables for 2D plotting
last = ""

# look at what variables where used in the experiment
for data in data_names:
    # only 2D files, so always 3 char long prefix for variable
    if last != data[0:4]:
        last = data[0:4]
        if last not in prefixes:
            prefixes += [last]
            # We want one directory for multiple graphs per variable
            # Its name should be the prefix without the tailing '_'
            os.mkdir(filename + "plotted/2D/" + last[:len(last) - 1])

# The runtime is in O(n*m) where n is nb of protocols and m nb of variables
# We need to go through all files for each variable to get all the datafiles for a variable to plot them together
for prefix in prefixes:
    # Will hold the filenames organized by security class for the prefix of this iteration
    protocols = [None] * 4
    for i in range(4):
        protocols[i] = []

    # sort in the 4 classes
    for data in data_names:
        if data[:4] == prefix:
            protocol_name = data[4:(len(data) - 4)]
            protocols[get_security_class(protocol_name)] += [protocol_name]

    # create plots
    for i in range(4):  # for each security class
        for protocol in protocols[i]:
            # Fill up info of this security class
            data_file_reader = open(filename + "parsed/2D/" + prefix + protocol + ".txt", "r")
            x, y = read_file(data_file_reader)
            plt.plot(x, y, marker='x', label=protocol, linewidth=1.0)

        # Create plot for this security class
        plt.xlabel(get_name(prefix))
        plt.ylabel("Runtime (s)")  # Datafiles always contain runtime values for the second coordinate
        plt.legend()

        plt.savefig(filename + "plotted/2D/" + prefix[:len(last) - 1] + "/" + get_security_class_name(i) + ".pdf")
        plt.clf()

    # Cost of security plots
    info2D_reader = open(filename + "parsed/info2D.txt", "r")


# - - - - - - - - CREATE 3D PLOTS - - - - - - - - - - -

data_names = os.listdir(args.filename + "parsed/3D/")

prefixes = []  # variable combinations for 3D plotting
