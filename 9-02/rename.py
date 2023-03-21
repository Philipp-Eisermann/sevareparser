import os
import re

# Loop through each directory in the current directory
for directory in os.listdir("."):
    if os.path.isdir(directory): # Check if the item is a directory (not a file or symbolic link)
        # Check if the directory contains a file matching the pattern "E*-run-summary.dat"
        summary_files = [f for f in os.listdir(directory) if re.match(r'E\d{2}-run-summary.dat', f)]
        if summary_files:
            # Extract the experiment number, node string, and test types from the run summary file
            with open(os.path.join(directory, summary_files[0])) as f:
                contents = f.read()
                exp = re.search(r'Experiment = (\d{2})', contents).group(1)
                nodes = re.search(r'Nodes = (.+)', contents).group(1).replace(' ', '_')
                testtypes = []
                for index, line in enumerate(contents):
                    if "Testtypes:" in line:
                        break

                # Extract the test types from the lines following the "Testtypes:" line
                for line in contents[index+1:]:
                    line = line.strip()
                    if line.startswith('#') or not line:
                        continue
                    testtype = line.split()[0]
                    testtypes.append(testtype[:3])

                    result = "".join(testtypes)

            # Rename the directory with the new name
            new_name = f"{exp}_{nodes}_{testtypes}"
            tests = ''.join(re.findall(r'Testtypes: ([A-Z]{3})', contents)[:3])
            os.rename(directory, new_name)
        else:
            # Print an error message if there is no run summary file
            print(f"No run summary in {directory}")
