# CAMTools

***
## Summary
This is a collection of tools and scripts used to test a Cavium tCAM test stand (NSP).

#### Teststand Information
FIXME

***
## List of Tools

#### setup.sh

Setup script used to source OCTEONSDK environment on the Argonne interactive nodes.

#### GenRulesFromPatterns.py

Python script for generating rules and traces used for testing NSP performance.

###### Input
Merged patterns file in text format (typically ending in .out) generated using TrigFTKBankGen, e.g. [MergedPatterns_ss40_1M.out.bz2](MergedPatterns_ss40_1M.out.bz2) after unzipping

###### Output
"Rule" and "trace" files corresponding to different nPatterns, nDC bits, etc. Rule files are essentially pattern banks that are used to load patterns onto the NSP. Trace files are essentially lists of hits that are used to pass into the NSP and test the pattern matching. The rule and trace files are also tested and a table is generated that summarizes the performance of each set of rules.

###### Run Instructions
First make sure you set up the OCTEONSDK environment using [setup.sh](setup.sh). You will also need to modify the file so that paths are set correctly. In particular, be check that the paths used in GenConfig::study are correct. You should also modify the for loop near line 140 in order to run over all interesting rule/trace configurations.



***

