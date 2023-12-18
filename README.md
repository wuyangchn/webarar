
*Thank you for using WebArAr. As of **December 17, 2023**, this documentation provides 
a short introduction to the features and functionalities available in the 
current release. However, it is planned to enhance and expand it to be better.*

# WebArAr

WebArAr is a web-based application designed for <sup>40</sup>Ar/<sup>39</sup>Ar geochronologic data (based on [Django](https://www.djangoproject.com/)).

* The backend functionalities are provided by [ArArPy](#ararpy). 
* WebArAr provides an intuitive interface, forstering a user-friendly and interactive experience.

Visit [WebArAr](https://www.webarar.net)


<!-- ## Content

[Introduction](#introduction)

[Features](#features)

[ArArPy](#ararpy)


## Introduction -->

<!-- WebArAr is a web-based application designed for the reduction and analysis 
of <sup>40</sup>Ar/<sup>39</sup>Ar geochronologic data for both beginners 
and professionals. This platform provides researchers with a user-friendly 
interface to input raw data, conduct various calculations to determine ages, 
and export in many formats.

The web application of WebArAr is mainly developed in Python ([ArArPy](#ArArPy)) 
with the Django framework, 
HTML template components, cascading style sheets (CSS), and JavaScript. 
The main functions on the backend for handling file input, data 
correction, and age calculation are programmed using Python, working with 
some open-source modules, including json, xlrd, xlsxwriter, math, SciPy, 
and NumPy. On the frontend, Bootstrap, a widely used CSS framework, is used 
to yield a simple and responsive interface. Apache Echarts 
(https://echarts.apache.org/) is used to plot interactive charts, 
such as age spectra and isochrone diagrams. 
The data tables are created using Handsontable, a commercial software but free 
for non-commercial purposes such as academic research 
(https://github.com/handsontable/handsontable/).  -->



# Features

#### 1. **Interactive data input:**
   - Easily enter raw data from mass spectrometers through an interactive 
   web page.
   - Modify and update parameters to recalculate ages, allowing flexibility 
   in data analysis.

#### 2. **Isochron data recalculation:**
   - Users can input isochron data and selectively recalculate isochronous 
   ages by choosing specific points.

#### 3. **3D K-Cl-Ar correction regression:**
   - Utilizes advanced 3D K-Cl-Ar correction regression to minimize errors 
   associated with assumptions in Cl correction.
   - Particularly beneficial in progressive crushing 40Ar/39Ar dating when 
   fluid inclusions may contain complex chlorine components.

#### 4. **Export options:**
   - Export diagrams in various formats suitable for publications.
   - Export sample data as structured JSON serialized files for easy sharing 
   and future use.

#### 5. **Publication accessibility:**
   - Availability of specially structured JSON serialized files with paper 
   publications enhances data visibility and encourages reusability.

#### 6. **MSWD distribution analysis:**
   - Discussion on the distribution of MSWD values, highlighting the influence 
   of analytical and geological errors.
   - Acknowledges the variability of MSWD values and challenges the rigid 
   requirement for values to be close to 1.

# Usage

* Access the application at http://www.webarar.net.
* (Optional) Install and launch WebArAr on your laptop for offline usage. See [Installation](#installation).
* (Optional) Use ArArPy with a Python terminal. See [ArArPy](#ararpy).

# Instruction

* See [user manual](#).
* See [video](#).

# Installation

The following instruction is for local usage. If you are planning to run WebArAr on a server computer instead, you can do much the same as mentioned below, but with some additional steps for a more stable application, such as replacing the built-in web server.

#### 1. Install Python 3

    (to be completed)
   
   

#### 2. Install MySql

    (to be completed)

#### 3. Redis

    (to be completed)

#### 4. Download codes

    (to be completed)

#### 5. Run server

    (to be completed)

### 

# ArArPy

The main python code used in WebArAr is packaged as ArArPy and uploaded to PyPI.
ArArPy includes all data processing steps, including reading data from local files, 
blank correction, decay correction, interference reactions correction, age calculation, 
isochron regression, etc. The software is written in Python language combined with 
some open source packages, such as numpy, pandas, os, scipy, pickle, xlrd, xlsxwriter, 
and json. 

### Installing from PyPI
ArArPy can be installed via pip from PyPI.

    pip install ararpy

### Testing
#### 1. **Running the test function from a Python terminal**

    >>> import ararpy as ap
    >>> ap.test()
    Running: ararpy.test()
    ============= Open an example .arr file =============
    file_path = 'your_dir\\examples\\22WHA0433.arr'
    sample = from_arr(file_path=file_path)
    sample.name() = '22WHA0433 -PFI'
    sample.help = 'builtin methods:\n __class__\t__delattr__\t__dir__\t__eq__\t__format__\t__ge__\t__getattribute__\t__gt__\t__hash__\t__init__\t__init_subclass__\t__le__\t__lt__\t__ne__\t__new__\t__reduce__\t__reduce_ex__\t__repr__\t__setattr__\t__sizeof__\t__str__\t__subclasshook__\ndunder-excluded methods:\n apparent_ages\tblank\tcalc_ratio\tcorr_atm\tcorr_blank\tcorr_ca\tcorr_cl\tcorr_decay\tcorr_k\tcorr_massdiscr\tcorr_r\tdoi\tinitial\tisochron\tlaboratory\tname\tparameters\tpublish\trecalculation\tresearcher\tresults\tsample\tsequence\tset_selection\tunknown\tupdate_table\n'
    sample.parameters() = <ararpy.ArArData object at 0x0000027F7FBEC9D0>
    sample.parameters().to_df() = 
             0    1      2       3       4    5  ...   117     118   119 120 121 122
    0   298.56  0.0  0.018  0.0063  0.1885  0.0  ...  0.31  298.56  0.31   1   1   1
    1   298.56  0.0  0.018  0.0063  0.1885  0.0  ...  0.31  298.56  0.31   1   1   1
    2   298.56  0.0  0.018  0.0063  0.1885  0.0  ...  0.31  298.56  0.31   1   1   1
    3   298.56  0.0  0.018  0.0063  0.1885  0.0  ...  0.31  298.56  0.31   1   1   1
    4   298.56  0.0  0.018  0.0063  0.1885  0.0  ...  0.31  298.56  0.31   1   1   1
    ... ...     ...  ...    ...     ...     ...  ...  ...   ...     ...    ... ... ...
    22  298.56  0.0  0.018  0.0063  0.1885  0.0  ...  0.31  298.56  0.31   1   1   1
    23  298.56  0.0  0.018  0.0063  0.1885  0.0  ...  0.31  298.56  0.31   1   1   1
    24  298.56  0.0  0.018  0.0063  0.1885  0.0  ...  0.31  298.56  0.31   1   1   1
    25  298.56  0.0  0.018  0.0063  0.1885  0.0  ...  0.31  298.56  0.31   1   1   1
    26  298.56  0.0  0.018  0.0063  0.1885  0.0  ...  0.31  298.56  0.31   1   1   1

#### 2. **Example 1： create an empty sample**

    >>> import ararpy as ap    
    >>> sample = ap.from_empty()  # create new sample instance
    >>> print(sample.show_data())
    # Sample Name:
    #
    # Doi:
    #    9a43b5c1a99747ee8608676ac31814da  # uuid
    # Corrected Values:
    #     Empty DataFrame
    # Columns: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    # Index: []
    # Parameters:
    #     Empty DataFrame
    # Columns: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
    #           30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56,
    #           57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83,
    #           84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, ...]
    # Index: []
    #
    # [0 rows x 123 columns]
    # Isochron Values:
    #     Empty DataFrame
    # Columns: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
    #           30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46]
    # Index: []
    # Apparent Ages:
    #     Empty DataFrame
    # Columns: [0, 1, 2, 3, 4, 5, 6, 7]
    # Index: []
    # Publish Table:
    #     Empty DataFrame
    # Columns: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    # Index: []
    
#### 3. **Example 2： change data point selection and recalculate**

    >>> import ararpy as ap 
    >>> import os
    >>> example_dir = os.path.join(os.path.dirname(os.path.abspath(ap.__file__)), r'examples')
    >>> file_path = os.path.join(example_dir, r'22WHA0433.arr')
    >>> sample = ap.from_arr(file_path)
    # normal isochron age
    >>> print(f"{sample.results().isochron.inverse.set1.age = }")
    # sample.results().isochron.inverse.set1.age = 163.10336210925516
    # check current data point selection
    >>> print(f"{sample.sequence().mark.value}")
    # [nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
    >>> print(f"{sample.sequence().mark.set1.index}")
    # [11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26]
    
    # change data point selection
    >>> sample.set_selection(10, 1)
    # check new data point selection
    >>> print(f"{sample.sequence().mark.set1.index}")
    # [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26]
    
    # recalculate
    >>> sample.recalculate(re_plot=True)
    # check new results
    >>> print(f"{sample.results().isochron.inverse.set1.age = }")
    # sample.results().isochron.inverse.set1.age = 164.57644271385772

### Classes

    Info
    Plot
    Sample
    Table
    
    class Info(builtins.object)
     |  Info(id='', name='', type='Info', **kwargs)
     |  
     |  Methods defined here:
     |  
     |  __init__(self, id='', name='', type='Info', **kwargs)
     |      Initialize self.  See help(type(self)) for accurate signature.
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors defined here:
     |  
     |  __dict__
     |      dictionary for instance variables (if defined)
     |  
     |  __weakref__
     |      list of weak references to the object (if defined)
    
    class Plot(builtins.object)
     |  Plot(id='', type='', name='', data=None, info=None, **kwargs)
     |  
     |  Methods defined here:
     |  
     |  __init__(self, id='', type='', name='', data=None, info=None, **kwargs)
     |      Initialize self.  See help(type(self)) for accurate signature.
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors defined here:
     |  
     |  __dict__
     |      dictionary for instance variables (if defined)
     |  
     |  __weakref__
     |      list of weak references to the object (if defined)
     |  
     |  ----------------------------------------------------------------------
     |  Data and other attributes defined here:
     |  
     |  Axis = <class 'sample.Plot.Axis'>
     |  
     |  BasicAttr = <class 'sample.Plot.BasicAttr'>
     |  
     |  Label = <class 'sample.Plot.Label'>
     |  
     |  Set = <class 'sample.Plot.Set'>
     |  
     |  Text = <class 'sample.Plot.Text'>
    
    class Sample(builtins.object)
     |  Sample(**kwargs)
     |  
     |  Methods defined here:
     |  
     |  __init__(self, **kwargs)
     |      Initialize self.  See help(type(self)) for accurate signature.
     |  
     |  apparent_ages(self)
     |  
     |  blank(self)
     |  
     |  calc_ratio(self)
     |  
     |  corr_atm(self)
     |  
     |  corr_blank(self)
     |  
     |  corr_ca(self)
     |  
     |  corr_cl(self)
     |  
     |  corr_decay(self)
     |  
     |  corr_k(self)
     |  
     |  corr_massdiscr(self)
     |  
     |  corr_r(self)
     |  
     |  corrected(self)
     |  
     |  doi(self)
     |
     |  degas(self)
     |  
     |  initial(self)
     |  
     |  isochron(self)
     |  
     |  laboratory(self)
     |  
     |  name(self)
     |  
     |  parameters(self)
     |  
     |  publish(self)
     |  
     |  recalculation(self)
     |  
     |  researcher(self)
     |  
     |  results(self)
     |  
     |  sample(self)
     |  
     |  sequence(self)
     |  
     |  set_selection(self)
     |  
     |  show_data(self)
     |  
     |  unknown(self)
     |  
     |  update_table(self)
     |  
     |  ----------------------------------------------------------------------
     |  Readonly properties defined here:
     |  
     |  version
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors defined here:
     |  
     |  __dict__
     |      dictionary for instance variables (if defined)
     |  
     |  __weakref__
     |      list of weak references to the object (if defined)
    
    class Table(builtins.object)
     |  Table(id='', name='Table', colcount=None, rowcount=None, header=None, data=None, coltypes=None, textindexs=None, numericindexs=None, **kwargs)
     |  
     |  Methods defined here:
     |  
     |  __init__(self, id='', name='Table', colcount=None, rowcount=None, header=None, data=None, coltypes=None, textindexs=None, numericindexs=None, **kwargs)
     |      Initialize self.  See help(type(self)) for accurate signature.
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors defined here:
     |  
     |  __dict__
     |      dictionary for instance variables (if defined)
     |  
     |  __weakref__
     |      list of weak references to the object (if defined)

