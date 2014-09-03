# fastbillreport

Financial report builder for Fastbill

## Introduction

[Fastbill][fastbill] is a wonderful cloud service for people like me having a
 small side business, that just want to manage incoming and outgoing bills. 
 It's easy, low priced and fast.
 
People like me, however, need a bit more than what the "Complete"-plan offers:

Every quarter I have to send a "UstVa" report to my tax office and for that I
 collect my bills, order them and put them in a folder. I calculate all bills
  and I fill out the tax report.
  
For this I need some kind of very basic reporting (hey, 
I'm a one man show offering services. I actually only need 4 figures for the 
UstVa-report!).

This is, what this script does. It's a basic platform for reports based on 
the Fastbill API and the wonderful [python-fastbill library][python-fastbill]
 by Stylight.
 
It already contains the following reports:

* books - a simple books report printing all invoices (income or expense) 
from a given scope
* ustva - reporting on figures for the german UstVa tax report

## Prerequisites

* [Python 2.7][python]
* [Python-Fastbill][python-fastbill]
* A fastbill API key (get one on your Settings/Overview-page)

## Usage

Run fastbillreport.py with --help to display an argument help.

A typical command would contain the following arguments

python python-fastbill.py -u <User> -k <key> <report> -s <scope> -d 
<scope-value> <report-name>

* -u: User of fastbill
* -k: API-key
* report: one of the supported reports (use python python-fastbill.py --help 
to see the supported reports)
* -s: Scope (e.g. "quarter". Look at python python-fastbill.py books --help 
for valid values)
* -d: A value for the scope (for example 20141 for the first quarter 2014. 
Again, see the report-specific help for details)

Each report has different output. Just have a try for examples.

[fastbill]: http://fastbill.com
[python-fastbill]: https://github.com/stylight/python-fastbill
