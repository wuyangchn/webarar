
# WebArAr

## Introduciton

WebArAr is a web-based application based on [Django](https://www.djangoproject.com/) 
designed to reduce <sup>40</sup>Ar/<sup>39</sup>Ar geochronologic data.

* The backend functionalities are packaged into a module called [ArArPy](https://github.com/wuyangchn/ararpy.git). 
Access through [PyPi](https://pypi.org/project/ararpy/).
* Django framework, Bootstrap, Echarts, Bootstrap-table, etc. provide an intuitive and interactive interface.

Visit [WebArAr](https://www.webarar.net)

## Background

This project originated from the necessity to update and enhance existing software tools for <sup>40</sup>Ar/<sup>39</sup>Ar dating. In general, ArArCALC and Isoplot/Isoplot R have been widely utilized within this field. However, several factors have rendered these tools inadequate for meeting the evolving requirements: (1) ArArCALC and Isoplot were developed as macro tools for outdated Excel versions, such as Excel 2003. Isoplot is no longer maintained, and ArArCALC is closed-source. (2) The increasing importance of chlorine correction in crushing experiments requires software with new features. (3) IsoplotR is great for plotting but lacks support for correction and newer calcultions in <sup>40</sup>Ar/<sup>39</sup>Ar community such as age calibration. Additionally, its regression methods differ from commonly used York regression.

Therefore, the main purpose of WebArAr is to balance the functionality of ArArCALC and IsoplotR and it will be continuously updated with more research needs in order to serve the community.

## Features
- [ ] Import
    - [x] Raw files from mass spec. See [File Filter](#)
    - [x] Age files from ArArCALC
    - [x] Xls files from ArArCALC
    - [x] Munally enter
- [ ] Raw Data Reduction
    - [x] Blank correction
    - [x] Mass discrimination correction
    - [x] Decay correlation
    - [x] Degas argon isotopes
- [ ] Calculation
    - [x] Age Calculation
        - [x] Regular equation
        - [x] Min equation
        - [x] Renne calibration
    - [x] Isochron regression
        - [x] Normal and inverse isochron
        - [x] Chlorine related isochrons
        - [x] York error weighted regression
        - [ ] Robust regression
        - [ ] Other regression methods
    - [x] Three-dimensional regression
    - [x] Age spectra
        - [x] Re-correction with initial ratio derived from isochrons
        - [x] Plateau ages
    - [x] Chi-squared and P values
    - [x] MSWD 
- [ ] Interfaces, tables and plots
    - [x] Interacitve multi tables and plots 
- [ ] Export
    - [x] Xls
    - [x] PDF
    - [x] SVG

## Usage

* Access the application at http://www.webarar.net.
See [Tutorial](/readme/Tutorial.md) for step-by-step instructions
* (Optional) Deploy and launch WebArAr on your computer for offline usage. See [Deploy on your own caomputer](/readme/Deployment.md).
* (Optional) Use ArArPy with a Python terminal. See [ArArPy](#ararpy).
<!-- * [Vedio examples]() -->

## Update Log

The log is [here](/../CHANGE_LOG.md)

## Citing WebArAr or ArArPy


## Reference

