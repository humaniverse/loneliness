# loneliness <img src='man/figures/logo.png' align="right" height="150" /></a>

<!-- badges: start -->
[![Project Status: WIP – Initial development is in progress, but there
has not yet been a stable, usable release suitable for the
public.](https://www.repostatus.org/badges/latest/wip.svg)](https://www.repostatus.org/#wip)
<!-- badges: end -->

## Overview
A loneliness prescription index for the UK. 
The code and approach for Scotland, Wales and Northern Ireland is based on [an approach developed by the Office for National Statistics' Data Science Campus](https://datasciencecampus.ons.gov.uk/developing-a-loneliness-prescription-index/), which uses GP prescription data to find areas with above-average prescriptions for conditions where loneliness has been shown to be a risk factor: Alzheimer's, depression, hyperternsion, diabetes, cardiovascular disease, anxiety, addiction and insomnia. Currently under active
development.

## Virtual Environments
This project uses `requirements.txt` to manage Python package dependencies. 

Instruction below to create and activate the virtual environment using Python's inbuilt `venv` module:
* Create a new virtual environment:
  - `python -m venv venv_loneliness`
* Activate the virtual environment:
  - Windows: `venv_loneliness\Scripts\activate.bat`
  - Unix: `source venv_loneliness/bin/activate`
* Install the packages:
  - Windows: `pip install -r requirements-win.txt`
  - Unix: `pip install -r requirements-unix.txt`
* Deactivate the virtual environment:
  - `deactivate`

  ## Drug List
  Sources for the treatment drugs below:
  * [Depression - NICE](https://bnf.nice.org.uk/treatment-summaries/antidepressant-drugs/); [Depression - NHS](https://www.nhs.uk/mental-health/talking-therapies-medicine-treatments/medicines-and-psychiatry/antidepressants/overview/)
  * [Alzheimer](https://www.nice.org.uk/guidance/ta217)
  * [Hypertension - NICE](https://bnf.nice.org.uk/treatment-summaries/hypertension/#related-drugs); [Hypertension - NHS](https://www.nhs.uk/conditions/high-blood-pressure-hypertension/treatment/#:~:text=Common%20examples%20are%20amlodipine%2C%20felodipine,and%20verapamil%2C%20are%20also%20available.)
  * [Type 2 Diabetes](https://bnf.nice.org.uk/treatment-summaries/type-2-diabetes/)
  * [Cardiovascular disease](https://www.nhs.uk/conditions/coronary-heart-disease/treatment/)
  * [Insomnia](https://cks.nice.org.uk/topics/insomnia/)
  * [Addiction](https://cks.nice.org.uk/topics/opioid-dependence/)
  * [Social anxiety](https://cks.nice.org.uk/topics/generalized-anxiety-disorder/prescribing-information/escitalopram-paroxetine-sertraline/)