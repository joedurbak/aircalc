# aircalc
calculates air mass, rise time and set time for given ra and dec

# input

expects csv with header line that at least contains:

  - BlockID
  - ObjectName
  - RA
  - DEC

# installation

Clone the repository

    git clone https://github.com/joedurbak/aircalc

Install the packages

    conda install astropy numpy matplotlib pandas jinja2
    conda install -c conda-forge astroplan
