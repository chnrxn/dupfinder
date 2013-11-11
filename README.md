dupfinder
=========

find and remove duplicate files

## Requirements

* Python version 2.7
* Pony ORM (package name: pony)
* argparse if Python <2.7 (package name: argparse)

## Dependency installation

Use Pip to install dependencies

	pip install --upgrade pony

## usage:
 
To get help: 

	python -m main -h
	
	usage: main.py [-h] [--dbfile DBFILE] [--action ACTION] [--trashcan TRASHCAN]
				   [--delete] [--loglevel LOGLEVEL] [--maxsize MAXSIZE]

	optional arguments:
	  -h, --help           show this help message and exit
	  --dbfile DBFILE
	  --action ACTION
	  --trashcan TRASHCAN
	  --delete
	  --loglevel LOGLEVEL
	  --maxsize MAXSIZE

Actions:

*scan* - this will recursively scan the specified directory to generate and store checksums for all the contained files in the database

	python -m main --action=scan <directory_to_scan>
	
*find* - this will recursively inspect the files in the specified directory and remove duplicate files that exist in the database

	python -m main --action=find <directory_to_find_duplicates_in>
	
No files will be removed by default.

## Options and defaults

1. maxsize: 10*1024^2 or 10MB - files larger than this will be skipped
1. delete: false - will remove duplicate files only when this is true
1. dbfile: sums.db
