#!/usr/bin/env python3

import os, sys, subprocess
import getopt, glob, re, itertools
import time, tempfile, zipfile, tarfile, csv, shutil
from operator import itemgetter
import evaluation

BASEPATH = os.getcwd()
OUTFILE = os.path.join(BASEPATH, 'results.csv')
SOLUTIONDIR = os.path.join(BASEPATH, 'solutions')
SUBMISSIONDIR = os.path.join(BASEPATH, 'submissions')
MAX_ITER = -1
ARCHIVETYPE = 'zip'


def usage(rc = 2):
  print('Usage:')
  print('  %s' % sys.argv[0] + '\t  [-o <outputfile (%s/results.csv)>]' % BASEPATH + \
          '\n\t\t  [-b <baseline-dir (%s/solutions)>]\t The directory with baseline code' % BASEPATH + \
          '\n\t\t  [-s <submissions-dir (%s/submissions)>]\t The directory with students\' submissions' % BASEPATH + \
          '\n\t\t  [-t <archivetype> (zip)]\t The archive type of students\' submission' + \
          '\n\t\t  [-n <num>]\t Stop after grading \'num\' submissions'
       )
  print()
  sys.exit(rc)

def grouped(iterable, n):
  return zip(*[iter(iterable)]*n)

def pairwise(iterable):
  a, b = itertools.tee(iterable)
  next(b, None)
  return zip(a, b)

def is_same_person(file1, file2):
  if 'E' == file1[0].upper() and file1[:8] == file2[:8]:
    return True
  elif 'A' == file1[0].upper() and file1[:9] == file2[:9]:
    return True
  return False

def sorted_nicely(l, key): # Sort the way humans expect
  convert = lambda text: int(text) if text.isdigit() else text
  alphanum_key = lambda item: [ convert(c) for c in re.split('([0-9]+)', key(item)) ]
  return sorted(l, key = alphanum_key)

def get_subm_key(file1):
  if 'E' == file1[0].upper():
    return file1[:8]
  elif 'A' == file1[0].upper():
    return file1[:9]
  return 'err'

def alphanum_key(string):
  return re.sub('[^0-9a-zA-Z]+', '', string.split('.')[0])

def remove_duplicates(submission_files): # Remove duplicates and select the latest submission
  submission_files_nodup = []
  duplicates = set()
  for subm1, subm2 in pairwise(submission_files):
      if subm2 and is_same_person(subm1, subm2):
        duplicates.update([(alphanum_key(subm1), subm1), (alphanum_key(subm2), subm2)])
      else:
        submission_files_nodup.append(subm1)
  duplicates = list(duplicates)
  duplicates = sorted_nicely(duplicates, itemgetter(0))
  files_nodup = {}
  for ind, tup in enumerate(duplicates):
      unique_key = tup[0]
      file_name = tup[1]
      files_nodup[get_subm_key(file_name)] = file_name

  for v in files_nodup.values():
    submission_files_nodup.append(v)

  return submission_files_nodup

def get_submission_files(): # Assuming all submissions to be in SUBMISSIONDIR
  submission_files = []
  for filename in glob.glob(os.path.join(SUBMISSIONDIR, '*')):
    filename = filename.rsplit('/', 1)[-1]
    pattern = '^(A|E)\w{7,8}[^"]*.' + ARCHIVETYPE + '$' # Assuming all submissions are archived
    if re.match(pattern, filename):
      submission_files.append(filename)
  submission_files.sort()
  submission_files_nodup = remove_duplicates(submission_files)
  return submission_files_nodup

eval_dict = {
        'ex1': evaluation.ex1, # 2%
        'ex2': evaluation.ex2, # 2%
        'ex3': evaluation.ex3, # 0%
        'ex4': evaluation.ex4, # 2%
        'ex5': evaluation.ex5, # 1%
        }


def main():
  try:
    opts, args = getopt.getopt(sys.argv[1:], "hb:s:o:t:n:", [ "help", "baseline=", "submissions=", "archivetype=", "output=" ])
  except getopt.GetoptError as e:
    print(e, file = sys.stderr)
    usage(1)
  global SOLUTIONDIR, SUBMISSIONDIR, OUTFILE, MAX_ITER, ARCHIVETYPE
  submission_files = []
  for o, a in opts:
    if o == '-h' or o == '--help':
      usage(0)
    if o == '-b' or o == '--baseline':
      SOLUTIONDIR = os.path.abspath(a)
    if o == '-s' or o == '--submissions':
      SUBMISSIONDIR = os.path.abspath(a)
    if o == '-o' or o == '--output':
      OUTFILE = os.path.abspath(a)
    if o == '-t' or o == '--archivetype':
      ARCHIVETYPE = a
    if o == '-n':
      MAX_ITER = int(a)

  submission_files = get_submission_files()
  it = len(submission_files) if MAX_ITER == -1 else MAX_ITER
  print('Grading %s submissions' % it)

  try:
    tmpdir = tempfile.mkdtemp()
  except OSError as e:
    print(e, file = sys.stderr)

  ret = set_baseline()

  while it > 0:
    it -= 1
    for _ex in [ 'ex1', 'ex2', 'ex3', 'ex4', 'ex5', ]:
      eval_dict[_ex]()


  try:
    shutil.rmtree(tmpdir)
  except OSError as e:
    print(e, file = sys.stderr)




if __name__ == '__main__':
  main()
