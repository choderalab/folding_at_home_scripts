# Folding@Home Utility Scripts and Notebooks

This repository contains scripts and notebooks to manage and track folding@home data.\
Note: This repository uses the in-progress RESTful API that is under development.\
As a result the scripts within this notebook may need updating every so often.

## Useful scripts and notebooks files

+ `fah-api-tracker.ipynb`: this notebook uses the REST API to pull information about your
project in JSON format and makes histograms
+ `environment.yml`: this will install with conda the necessary libraries to run
the code of this repository.

## Install Environment
Thanks to the RESTful API the requirements for this repository are minimal.\
The following python libraries are necessary:
- `numpy`
- `json`
- `matplotlib`
- `requests`

To install the environment run the following command:
```conda env create -f environment.yml```

## Getting a license file for the RESTful API
To get a license file for the RESTful API you need access to the Assignment Server.\
(To get access to the AS you'll need to contact Joseph - see Sukrit or John for details)

1. Generate a private key by running
```openssl genrsa -out private.pem 2048```
This is your private key. *Never Share This Key.*
2. Generate a public key by running
```openssl req -out csr.pem -key private.pem -new -subj "/CN=[YOUR EMAIL ADDRESS]/"```
NOTE that `/CN=[YOUR EMAIL ADDRESS]/` should match the one you use to login to the AS.
3. Go to the AS page and at the top click the Certificates tab.
4. Paste the contents of csr.pem into the text box and click the "Submit CSR" button.
5. The AS will auto-download the certificate and save it as `cert.pem`
You can check the details of your certificate by running: 
```openssl x509 -text -noout -in fah-cert-chain-sukritsingh92@gmail.com.pem```

Inside the notebook you'll be passing a path to `cert.pem` and `private.pem`
