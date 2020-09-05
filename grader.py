#!/usr/bin/env python3

import os, sys, subprocess
import getopt, glob, re
import time, tempfile, zipfile, tarfile, csv

BASEPATH = os.getcwd()
OUTFILE = os.path.join(BASEPATH, 'results.csv')
SOLUTIONDIR = os.path.join(BASEPATH, 'solutions')
SUBMISSIONDIR = os.path.join(BASEPATH, 'submissions')
MAX_ITER = -1


def usage(rc = 2):
  print('Usage:')
  print('  %s' % sys.argv[0] + '\t  [-o <outputfile (results.csv)>]' + \
          '\n\t\t  [-b <baseline-dir (solutions)>]\t The directory with baseline code' + \
          '\n\t\t  [-s <submissions-dir (submissions)>]\t The directory with students\' submissions' + \
          '\n\t\t  [-n <num>]\t Stop after grading \'num\' submissions'
       )
  print()
  sys.exit(rc)

def main():
  try:
    opts, args = getopt.getopt(sys.argv[1:], "hb:s:o:n:", [ "help", "baseline=", "submissions=", "output="])
  except getopt.GetoptError as e:
    print(e, file = sys.stderr)
    usage(1)
  global SOLUTIONDIR, SUBMISSIONDIR, OUTFILE, MAX_ITER
  for o, a in opts:
    if o == '-h' or o == '--help':
      usage(0)
    if o == '-b' or o == '--baseline':
      SOLUTIONDIR = os.path.abspath(a)
    if o == '-s' or o == '--submissions':
      SUBMISSIONDIR = os.path.abspath(a)
    if o == 'o' or o == 'output':
      OUTFILE = os.path.abspath(a)
    if o == 'n':
      MAX_ITER = a

if __name__ == '__main__':
  main()
