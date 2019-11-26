# GIC
Calculation of geomagnetically induced currents in the Dutch powergrid. Details about the calculations can be found inside the code. The 'ods' and 'csv' files in the network folder contain the information about the Dutch (+German/Belgian) powergrid.

## Install
1. Clone the git repository

    ```bash
    > git clone https://github.com/outfrenk/Dutch_GIC
    ```

2. Build and install the package

    ```bash
    > python setupGIC.py install
    ```

## data
The raw data used during research can also be found in the data folder

## Example
An example of how to run the code (dutchgic.py) can be found in the 'usage class GIC' jupyter notebook or for a complete jupyter notebook in 'Class_GIC_notebook.ipynb' in the notebooks folder. The logbook.log in the logbook folder contains details about running the code.

## Testing
You can test the code using pytest as well. However, change the string in test_code.py in the tests folder (in function test_init()) to the location where you store your csv files (spreadsheetcables.csv and spreadsheettrafo.csv) before running.
Then run

    ```bash
    > pytest
    ```

## Dependencies external
This class depends on a couple of packages:
- numpy
- re
- os
- pandas
- logging
- multiprocessing
- threading
- scipy
- urllib
- datetime
- matplotlib
- pySECS (which can be downloaded at https://github.com/greglucas/pySECS)

## Dependencies internal
The functions all have a dependency on each other; some can be run alone, others need to be run with the function who called them. These dependent functions are indicated by @. If the function only push data towards a subfunction &rarr; is used. When a function pushes data towards a subfunction, but this subfunction pushes data back as well &harr; is used.

If we would run the function *runall()*, it would run the following functions:
1. *standard_download()*

   a.&rarr; *download_data()* 
   
   b.&harr; *find_quiet_data()*
   
2. *iteratestation()*

   a.&rarr; *newplotspace()*
   
3. *magnetic_interpolation()*

   a. &rarr;*magnetic_time()*@
   
      aa.&harr; *mag_interpolate()*@ NEEDS pySECS package here!
      
4. *BtoE()*

   a.&harr; *check_sampling()*
   
   b.&harr; *Parzen()*
   
   c.&harr; *filt()*
   
   d.&harr; *transferfunction()*
   
   e.&rarr; *writing_electric()*@
   
5. *calculate_GIC()*

   a.&harr; *check_sampling()*
   
   b.&rarr; *GICfunction()*@
   
      ba.&harr; *ObtainJ()*@ &harr; *calcE()*@
         
6. *plot_GIC()*
 
   a.&harr; *check_sampling()*
    
7. *make_video()*
 

### *GIC_index()*
There is also a GIC_index function. This function needs magnetic values from *magnetic_interpolation()* to work. It uses *check_sampling()* in the process.
