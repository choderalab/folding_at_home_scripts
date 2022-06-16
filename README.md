# Folding@Home Utility Scripts and Notebooks

This repository contains my scripts and notebooks to manage folding@home data.
Use them as you wish but beware of bugs! Please let me know if you find some bug
or problem and please share your improvements to the code!

## Current Files

+ `fah-progress.ipynb`: this notebook will download the leveldb of the workserver
and help-you study the state of your data.
+ `environment.yml`: this will install with conda the necessary libraries to run
the code of this repository.
+ `environment-mac.yml`: this will install with conda necessary libraries for MacOS X systems *except for the `plyvel` library*

## Install Environment
### Linux

You must also install [leveldb](https://github.com/google/leveldb) to use the
fah-progress.ipynb. 

``` bash
conda env create -f environment.yml
conda activate fah-leveldb
ipython kernel install --user --name=fah-leveldb
```

### MacOS X - by Sukrit Singh (sukrit.singh@choderalab.org)

To actually install the environment, first do:
``` bash
conda env create -f environment-mac.yml
conda activate fah-leveldb
ipython kernel install --user --name=fah-leveldb
```

However, if you have MacOS 11 (Big Sur) or later, you must do a manual installation of the `plyvel` library due to differences in the Darwin OS.

Next, download the [`plyvel`](https://github.com/wbolster/plyvel) library manually from the github page.

Unzip and navigate into the `plyvel` package:
```
unzip plyvel-master.zip
cd plyvel-master
```

Next, in `plyvel-master/setup.py`, replace *Line 17* with an updated version:
```
extra_compile_args = ['-Wall', '-g', '-x', 'c++', '-std=c++11', '-fno-rtti']
```
Save the updated `setup.py`.

Next we will install leveldb: 
It turns out that the `plyvel` repo already has the scripts you need to setup `leveldb`. Simply go to `plyvel-master/scripts` and run the following scripts - Run them in the following order (note that you need `cmake`):
1. `./cibuildwheel-before-build.sh`
2. `./install-leveldb.sh`
3. `./install-snappy.sh`

*One alternative approach* : To install [leveldb](https://github.com/google/leveldb) on MacOS, you can use [Homebrew](https://brew.sh/)
```
brew install leveldb
```
Note that homebrew installation can be a bit tricky on MacOS Big Sur

Once you leveldb installed: 

Run the following commands in the same directory where `setup.py` is:
```
make
python setup.py install
```

Test whether plyvel works using `python -c 'import plyvel'` - this should return no output if everything worked!

Now feel free to use `fah-progress.ipynb` for anything you want!
