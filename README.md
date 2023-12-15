
# WebArAr

[Introduction](#Introduction)

[Features](#Features)

WebArAr is a web-based application designed for the reduction and analysis 
of <sup>40</sup>Ar/<sup>39</sup>Ar geochronologic data for both beginners 
and professionals. This platform provides researchers with a user-friendly 
interface to input raw data, conduct various calculations to determine ages, 
and export in many formats.

The web application of WebArAr is mainly developed in Python with the Django 
framework, HTML template components, cascading style sheets (CSS), and 
JavaScript. The main functions on the backend for handling file input, data 
correction, and age calculation are programmed using Python, working with 
some open-source modules, including json, xlrd, xlsxwriter, math, SciPy, 
and NumPy. On the frontend, Bootstrap, a widely used CSS framework, is used 
to yield a simple and responsive interface. Apache Echarts 
(https://echarts.apache.org/) 
is used to plot interactive charts, such as age spectra and isochrone diagrams. 
The data tables are created using Handsontable, a commercial software but free 
for non-commercial purposes such as academic research 
(https://github.com/handsontable/handsontable/). 

## How to Access WebArAr

Visit [WebArAr](https://www.webarar.net) to explore the platform and start 
your <sup>40</sup>Ar/<sup>39</sup>Ar dating data analysis.

## Features

### 1. **Interactive Data Input:**
   - Easily enter raw data from mass spectrometers through an interactive 
   web page.
   - Modify and update parameters to recalculate ages, allowing flexibility 
   in data analysis.

### 2. **Isochron Data Recalculation:**
   - Users can input isochron data and selectively recalculate isochronous 
   ages by choosing specific points.

### 3. **3D K-Cl-Ar Correction Regression:**
   - Utilizes advanced 3D K-Cl-Ar correction regression to minimize errors 
   associated with assumptions in Cl correction.
   - Particularly beneficial in progressive crushing 40Ar/39Ar dating when 
   fluid inclusions may contain complex chlorine components.

### 4. **Export Options:**
   - Export diagrams in various formats suitable for publications.
   - Export sample data as structured JSON serialized files for easy sharing 
   and future use.

### 5. **Publication Accessibility:**
   - Availability of specially structured JSON serialized files with paper 
   publications enhances data visibility and encourages reusability.

### 6. **MSWD Distribution Analysis:**
   - Discussion on the distribution of MSWD values, highlighting the influence 
   of analytical and geological errors.
   - Acknowledges the variability of MSWD values and challenges the rigid 
   requirement for values to be close to 1.


---

*Note: pass.*
