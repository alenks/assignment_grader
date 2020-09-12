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
NUM_EX = 5
TMPDIR = ''


def usage(rc = 2):
  print('Usage:')
  print('  %s' % sys.argv[0] + '\t  [-h | --help]' + \
          '\n\t\t  [-o <outputfile (%s/results.csv)>]' % BASEPATH + \
          '\n\t\t  [-b <baseline-dir (%s/solutions)>]\t The directory with baseline code' % BASEPATH + \
          '\n\t\t  [-s <submissions-dir (%s/submissions)>]\t The directory with students\' submissions' % BASEPATH + \
          '\n\t\t  [-t <archivetype> (zip)]\t The archive type of students\' submission' + \
          '\n\t\t  [-n <num (total submissions)>]\t Stop after grading \'num\' submissions' + \
          '\n\t\t  [-e <num (5)>]\t Total number of exercises'
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
      elif (alphanum_key(subm1), subm1) not in duplicates:
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

def extract_file(fname, path):
  listdir_pr = os.listdir(path)
  try:
    shutil.unpack_archive(fname, path)
  except Exception as e:
    print(e, file = sys.stderr)
    return
  listdir_ex = os.listdir(path)
  ex_dirs = list(set(listdir_ex) - set(listdir_pr))
  def is_id(ex_dirs):
    for el in ex_dirs:
      pattern = '^(A|E)\w{7,8}[^"]*$'
      if re.match(pattern, el):
        return el

  if is_id(ex_dirs):
    list_l1 = glob.glob(os.path.join(path, is_id(ex_dirs), '*'))
    for el in list_l1:
      el = el[:-1] if el.endswith('/') else el
      shutil.copytree(el, os.path.join(path, el.split('/')[-1]))
  print(os.listdir(path))
  return

def copy_to_workdir(submission_file, TMPDIR):
  src = os.path.join(SUBMISSIONDIR, submission_file)
  dst = os.path.join(TMPDIR, submission_file)
  try:
    shutil.copyfile(src, dst)
  except Exception as e:
    print(e, file = sys.stderr)
  extract_file(dst, TMPDIR)
  return

def remove_from_workdir(dirname):
  for content in os.listdir(dirname):
    fullpath = os.path.join(dirname, content)
    try:
      if os.path.isfile(fullpath) or os.path.islink(fullpath):
        os.unlink(fullpath)
      elif os.path.isdir(fullpath):
        shutil.rmtree(fullpath)
    except Exception as e:
      print(e, file = sys.stderr)
  return


eval_lst = [
        evaluation.ex1, # 2% {8,6,4,2,0}
        evaluation.ex2, # 2% {8,6,4,2,0}
        evaluation.ex3, # 0% {0,-1,-2}
        evaluation.ex4, # 2% {8,7,6,5,4,3,2,1,0}
        evaluation.ex5, # 1% {4,0}
        ]

def main():
  try:
    opts, args = getopt.getopt(sys.argv[1:], "hb:s:o:t:n:e:", [ "help", "baseline=", "submissions=", "archivetype=", "output=", "stopcount=", "numex=" ])
  except getopt.GetoptError as e:
    print(e, file = sys.stderr)
    usage(1)
  global SOLUTIONDIR, SUBMISSIONDIR, OUTFILE, MAX_ITER, ARCHIVETYPE, NUM_EX, TMPDIR
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
    if o == '-n' or o == '--stopcount':
      MAX_ITER = int(a)
    if o == '-e' or o == '--numex':
      NUM_EX = int(a)

  submission_files = get_submission_files()
  tot_it = len(submission_files) if MAX_ITER == -1 else MAX_ITER
  print('Grading %s submissions' % tot_it)

  try:
    TMPDIR = tempfile.mkdtemp()
  except Exception as e:
    print(e, file = sys.stderr)
  with open(OUTFILE, 'w') as csv_file:
    writer = csv.writer(csv_file, delimiter=',')
    header = ['StudentID'] + ['Ex' + str(x+1) for x in range(0,NUM_EX)]  + ['Total', 'FileName']
    writer.writerow(header)
    for _it in range(tot_it):
      copy_to_workdir(submission_files[_it], TMPDIR)
      res_ex = []
      for _ex in range(0, NUM_EX):
        ret = eval_lst[_ex](os.path.join(SUBMISSIONDIR, submission_files[_it]), TMPDIR, SOLUTIONDIR)
        res_ex.insert(_ex, ret)
      writer.writerow([get_subm_key(submission_files[_it])] + res_ex + [max(0, sum(res_ex)), submission_files[_it]])
      remove_from_workdir(TMPDIR)

  try:
    shutil.rmtree(TMPDIR)
  except Exception as e:
    print(e, file = sys.stderr)



if __name__ == '__main__':
  try:
    main()
  except KeyboardInterrupt:
    if os.path.exists(TMPDIR):
      print('\nCtrl-C detected: Removing %s' %(TMPDIR), file = sys.stdout)
      try:
        shutil.rmtree(TMPDIR)
      except Exception as e:
        print(e, file = sys.stderr)
    sys.exit(-1)
