Guide:

> Parameter: directory name of a run outputted by sevare bench (https://github.com/vyrovcz/sevarebench, version 2023/02 *)
> Run with python3 sevare_parser.py <name of directory>, this will generate a directory /parsed containing all data files and an info file with the interpolations
> If the /parsed directory already exists, SevareParser will delete nothing but append to all the files it intended to create and write on

Remarks about datatable: 

--> Best practice: make the parameter ranges go from least contraining to most constraining
> For parsing 2D data files from the 3+ variable tables, the parser always takes the first appearing values of parameters that are not being plotted in this iteration. 
  
--> The table MUST NOT contain lines with equal values of the variable array (see variable_array) 
> this only happens if the protocol was run multiple times for same parameter values in the same run
> will generate datafiles with multiple runtimes for a variable combination - disturbs interpolation

--> This version of sevare parser does not remove high runtime values for first iteration of protocols with heavy preprocessing phase
> the very large values as first y makes the interpolation completely errouneous (but no runtime error)

--> The winner search picks the best protocols based on their first coefficient which may be needed to be updated for some variables such as bandwidth, where the second coefficient (indicator of the bandwidth bottleneck of the protocol)

--> If the experiment types were to be extended:
> Make sure than the short form of the prefix DOES NOT start with "." (causes problem in plotter)

Required Packages:
> SevareParser and SevarePlotter use numpy and scipy, which can be installed using pip:
sudo apt install python3-pip
pip3 install -U numpy scipy
  
* The software contained in this repo was designed and tested based on the version of sevarebench up to 2023/02.
