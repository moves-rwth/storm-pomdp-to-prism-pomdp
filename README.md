# storm-pomdp-to-prism-pomdp

This small tool on top of stormpy creates prism-pomdp compatible POMDP files in an explicit manner.
We emphasise that the current transformation is so naive that we do not make this part of storm or stormpy. 
The main goal is to create files that both storm and prism can use as import, while using some of the new modelling power of storm, and the assurance that actions are ordered. 


## Getting Started
Before starting, make sure that Storm and stormpy are installed. If not, see the [documentation](https://moves-rwth.github.io/stormpy/installation.html) for details on how to install stormpy.

First, install the Python package. If you use a virtual environment, make sure to use it.
To install, execute
```
python setup.py develop
```

Then, run the script using 
```
python pomdp-to-prism.py --input pomdp-in.pomdp  --output pomdp-out.pomdp
```

