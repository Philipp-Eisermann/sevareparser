Guide:
- Parameter: directory name of a run outputted by sevare bench (https://github.com/vyrovcz/sevarebench)
- Run with python3 sevare_parser.py <name of directory>, this will generate a directory /parsed containing all data files and an info file with the interpolations
- If the /parsed directory already exists, SevareParser will delete nothing but append to all the files it intended to create and write on

Remarks about datatable: \\
--> The table MUST NOT contain lines with equal values of the variable array (see variable_array) 
> this only happens if the protocol was run multiple times for same parameter values in the same run
> will generate datafiles with multiple runtimes for a variable combination - disturbs interpolation

--> This version of sevare parser does not remove high runtime values for first iteration of protocols with heavy preprocessing phase
> the very large values as first y makes the interpolation completely errouneous (but no runtime error)

--> The winner search picks the best protocols based on their first coefficient which may be needed to be updated for some variables such as bandwidth, where the second coefficient (indicator of the bandwidth bottleneck of the protocol)
