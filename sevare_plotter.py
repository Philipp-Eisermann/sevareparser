# SEVARE PLOTTER
# Will create a /plotted directory and write everything in there
# A folder is created for each variable combination type ("<var_name>*_) contained in /parsed
# In these folders a plot (.tex & .pdf) for each security class (if represented by at least 1 protocol) will be created

parser = argparse.ArgumentParser(
    description='This program plots the results parsed by sevare parser.')

parser.add_argument('filename', type=str, help='Required, name of the test-run folder (usually of the form MONTH-YEAR).')

args = parser.parse_args()

filename = args.filename

if filename[len(args.filename)-1] != '/':
    filename += '/'

colors = ['black', 'blue', 'brown', 'cyan', 'darkgray', 'gray', 'green', 'lightgray', 'lime', 'magenta', 'olive',
          'orange', 'pink', 'purple', 'red', 'teal', 'violet', 'white', 'yellow']

# - - - - - - - - CREATE 2D LATEX FILES - - - - - - - - - - -


data_names = os.listdir(filename + "parsed/2D/")

prefixes = []  # holds all different variable-combinations
prefix = ""

for data in data_names:
    if prefix != data[0:4]:
        prefix = data[0:4]
        prefixes += [prefix]
        # TODO: create directory

for var_combo in prefixes:
    files = []  # Holds all files with this variable combination
    for data in data_names:
        # add protocols

    # go through files array and sort them in the 4 classes
    for file in files:

    # create latex file for each security class


# For 2D, all measurements are put into one file
if third_column_index == -1:
    latex_file = open(args.filename + "_plot.tex", "a")
    # todo: Make sure this file does not exist beforehand
    latex_file.write("\\documentclass[beamer,multi=true,preview]{standalone}\n\
\\usepackage{beamerpackages}\n\
\\usepackage{tumcolor}\n\
\\newlength{\\upt}\n\
\\setlength{\\upt}{0.0666667\\beamertextwidth}\n\n\
\\setbeamertemplate{headline}{}\n\n\
\\begin{document}%\n\
\\let\\shipout\\myshipout\n\
\\begin{standaloneframe}[plain]%\n\
\\begin{tikzpicture}\n\
\\begin{axis}[\n")
    latex_file.write("\ttitle={Experiment on " + "},\n\
    ylabel={" + args.second_column + "},\n\
    xlabel={" + args.first_column + "},\n\
    ymin=0, width=20cm,height=14cm,\n\
    legend pos={north west}\n\
    ]\n")
    for i in range(len(protocols)):
        latex_file.write(
            "\\addplot[color=" + colors[i] + "] table {" + DATA_DIRECTORY + "/" + args.filename + "/" + protocols[
                i] + ".dat};\n")

    latex_file.write("\\legend{\n")
    for prot in protocols:
        latex_file.write(prot + ',')
    latex_file.write("}\n\
\\end{axis}\n\
\\end{tikzpicture}\n\
\\end{standaloneframe}\n\
\\end{document}\n")

# - - - - - - - - CREATE 3D LATEX FILES - - - - - - - - - - -

# TODO: handle "_" in argument - latex does not compile if in title without leading \
else:
    for i in range(len(protocols)):
        latex_file = open(protocols[i] + "_plot.tex", "a")

        latex_file.write("\\documentclass{article}\n\
\\usepackage[margin=0.5in]{geometry}\n\
\\usepackage{pgfplots}\n\
\\pgfplotsset{width=10cm,compat=1.9}\n\
\\begin{document}\n\
\\begin{tikzpicture}\n\
\\begin{axis}[\n")
        latex_file.write("    xlabel={" + args.first_column + "},\n\
    ylabel={" + args.second_column + "},\n\
    zlabel={" + args.t + "}]\n")
        latex_file.write("\\addplot3[surf] table {" + DATA_DIRECTORY + "/" + protocols[i] + ".dat};\n")
        latex_file.write("\\end{axis}\n\
\\end{tikzpicture}\n\
\\end{document}\n")

latex_file.close()


# - - - - - - - - CREATE PDFs FROM TEX FILES - - - - - - - - - - -