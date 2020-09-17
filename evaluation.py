#!/usr/bin/env python3
import os, sys, subprocess, signal
import shutil, re, errno, math

# https://stackoverflow.com/questions/4789837/how-to-terminate-a-python-subprocess-launched-with-shell-true
def get_output(cmd, path = '.', timeout = 7): # Handle cases with infinite loops
  output = ''
  with subprocess.Popen(cmd, shell=True, encoding = 'utf8', stderr = subprocess.STDOUT,
          cwd = path, stdout = subprocess.PIPE, preexec_fn = os.setsid) as proc:
    try:
      output = proc.communicate(timeout = timeout)[0]
    except subprocess.TimeoutExpired:
      os.killpg(proc.pid, signal.SIGINT) # kill the process tree
      output = proc.communicate()[0]
      raise
    except Exception:
      raise
  return output

def get_output_no_timeout(cmd, path = '.'):
  ret = subprocess.check_output(cmd, shell = True, encoding = 'utf8', stderr = subprocess.STDOUT, cwd = path).strip()
  return ret

def ex(cmd):
  return subprocess.call(cmd, shell = True)

def positive_float(res):
  return not re.match(r'^\+?\d+(?:\.\d+)?$', res) is None

def mkdir_p(path):
  try:
    os.makedirs(path)
  except OSError as exc:
    if exc.errno == errno.EEXIST and os.path.isdir(path):
      pass
    else:
      raise

def copy_testing_files(sol_dir, workdir, ex_dir, files):
  dst_ex_dir = ex_dir.split('_')[0]

  dst_dir = os.path.join(workdir, dst_ex_dir)
  mkdir_p(dst_dir)
  src_dir = os.path.join(sol_dir, ex_dir)
  for item in files:
    src = os.path.join(src_dir, item)
    dst = os.path.join(dst_dir, item)
    try:
      shutil.copytree(src, dst)
    except OSError as exc:
      if exc.errno == errno.ENOTDIR:
        shutil.copy(src, dst)
      else: raise

def get_id(file1):
  file1 = file1.rsplit('/', 1)[-1]
  if 'E' == file1[0].upper():
    return file1[:8]
  elif 'A' == file1[0].upper():
    return file1[:9]
  return 'Error'

def printable(e, workdir):
  return ' '.join(str(e).replace(workdir+'/', '').strip().split())



def ex1(infile_c, workdir, sol_dir):
  exn = 'ex1'
  num_qparts = 7
  score = [0.0] * num_qparts
  ex_dir = 'ex1'
  files = ['Makefile', 'ex1.c', 'node.h',
          'inserthead_test.in', 'inserthead_test.out',
          'inserttail_test.in', 'inserttail_test.out',
          'deletehead_test.in', 'deletehead_test.out',
          'deletetail_test.in', 'deletetail_test.out',
          'resetlist_test.in', 'resetlist_test.out',
          'ultra_test.in', 'ultra_test.out',
          'big_test.in', 'big_test.out']

  copy_testing_files(sol_dir, workdir, ex_dir, files)
  if not os.path.isfile(os.path.join(workdir, ex_dir, 'node.c')):
    print('[%s][%s] File \'node.c\' not found' % (get_id(infile_c), exn), file = sys.stderr)
    return 0
  cmd = "make -C %s > /dev/null 2>&1" %(os.path.join(workdir, ex_dir))
  try:
    ret = ex(cmd)
  except subprocess.CalledProcessError as e:
    print('[%s][%s] Compilation failed: %s' % (get_id(infile_c), exn, printable(e, workdir)), file = sys.stderr)
    return 0
  if not ret:
    score[0] = 2
  else:
    print('[%s][%s] Compilation failed: Errcode %s' % (get_id(infile_c), exn, printable(ret, workdir)), file = sys.stderr)
    return 0
  def gen_cmd(workdir, ex_dir, ex_no, testfile):
    cmd = os.path.join(workdir, ex_dir, ex_no)
    cmd = ' '.join([cmd, '<', os.path.join(workdir, ex_dir, '%s.in'%(testfile))])
    cmd = ' '.join([cmd, '|', 'diff', os.path.join(workdir, ex_dir, '%s.out'%(testfile)), '-'])
    return cmd

  cmd = gen_cmd(workdir, ex_dir, 'ex1', 'inserthead_test')
  try:
    ret = get_output(cmd, path = os.path.join(workdir, ex_dir))
  except Exception as e:
    print('[%s][%s] Rutime error for \'insert_node_from_head_at()\' using \'inserthead_test.in\'. %s' % (get_id(infile_c), exn, printable(e, workdir)), file = sys.stderr)
    score[1] = 0
  else:
    if len(ret) > 2:
      print('[%s][%s] Wrong output for \'insert_node_from_head_at()\' using \'inserthead_test.in\'' % (get_id(infile_c), exn), file = sys.stderr)
      score[1] = 0
    else:
      score[1] = 1

  cmd = gen_cmd(workdir, ex_dir, 'ex1', 'inserttail_test')
  try:
    ret = get_output(cmd, path = os.path.join(workdir, ex_dir))
  except Exception as e:
    print('[%s][%s] Rutime error for \'insert_node_from_tail_at()\' using \'inserttail_test.in\'. %s' % (get_id(infile_c), exn, printable(e, workdir)), file = sys.stderr)
    score[2] = 0
  else:
    if len(ret) > 2:
      print('[%s][%s] Wrong output for \'insert_node_from_tail_at()\' using \'inserttail_test.in\'' % (get_id(infile_c), exn), file = sys.stderr)
      score[2] = 0
    else:
      score[2] = 1

  cmd = gen_cmd(workdir, ex_dir, 'ex1', 'deletehead_test')
  try:
    ret = get_output(cmd, path = os.path.join(workdir, ex_dir))
  except Exception as e:
    print('[%s][%s] Rutime error for \'delete_node_from_head_at()\' using \'deletehead_test.in\'. %s' % (get_id(infile_c), exn, printable(e, workdir)), file = sys.stderr)
    score[3] = 0
  else:
    if len(ret) > 2:
      print('[%s][%s] Wrong output for \'delete_node_from_head_at()\' using \'deletehead_test.in\'' % (get_id(infile_c), exn), file = sys.stderr)
      score[3] = 0
    else:
      score[3] = 1

  cmd = gen_cmd(workdir, ex_dir, 'ex1', 'deletetail_test')
  try:
    ret = get_output(cmd, path = os.path.join(workdir, ex_dir))
  except Exception as e:
    print('[%s][%s] Rutime error for \'delete_node_from_tail_at()\' using \'deletetail_test.in\'. %s' % (get_id(infile_c), exn, printable(e, workdir)), file = sys.stderr)
    score[4] = 0
  else:
    if len(ret) > 2:
      print('[%s][%s] Wrong output for \'delete_node_from_tail_at()\' using \'deletetail_test.in\'' % (get_id(infile_c), exn), file = sys.stderr)
      score[4] = 0
    else:
      score[4] = 1

  cmd = gen_cmd(workdir, ex_dir, 'ex1', 'resetlist_test')
  try:
    ret = get_output(cmd, path = os.path.join(workdir, ex_dir))
  except Exception as e:
    print('[%s][%s] Rutime error for \'reset_list()\' using \'resetlist.in. %s\'' % (get_id(infile_c), exn, printable(e, workdir)), file = sys.stderr)
    score[5] = 0
  else:
    if len(ret) > 2:
      print('[%s][%s] Wrong output for \'reset_list()\' using \'resetlist.in\'' % (get_id(infile_c), exn), file = sys.stderr)
      score[5] = 0
    else:
      score[5] = 1

  cmd = gen_cmd(workdir, ex_dir, 'ex1', 'ultra_test')
  try:
    ret = get_output(cmd, path = os.path.join(workdir, ex_dir))
  except Exception as e:
    print('[%s][%s] Rutime error with \'ultra_test.in\' testcase. %s' % (get_id(infile_c), exn, printable(e, workdir)), file = sys.stderr)
    score[6] = 0
  else:
    if len(ret) > 2:
      print('[%s][%s] Wrong output with \'ultra_test.in\' testcase' % (get_id(infile_c), exn), file = sys.stderr)
      score[6] = 0
    else:
      score[6] = 1

  return math.floor(sum(score))

def ex2(infile_c, workdir, sol_dir):
  exn = 'ex2'
  num_qparts = 4
  score = [0.0] * num_qparts
  ex_dir = 'ex2'
  files = ['Makefile', 'node.h', 'functions.c', 'functions.h', 'ultra_test.in', 'ultra_test.out', 'big_test.in', 'big_test.out']
  copy_testing_files(sol_dir, workdir, ex_dir, files)
  if not os.path.isfile(os.path.join(workdir, ex_dir, 'node.c')):
    print('[%s][%s] File \'node.c\' not found' % (get_id(infile_c), exn), file = sys.stderr)
    return 0
  cmd = "make -C %s > /dev/null 2>&1" %(os.path.join(workdir, ex_dir))
  try:
    ret = ex(cmd)
  except subprocess.CalledProcessError as e:
    print('[%s][%s] Compilation failed: %s' % (get_id(infile_c), exn, printable(e, workdir)), file = sys.stderr)
    return 0
  if not ret:
    score[0] = 2
  else:
    print('[%s][%s] Compilation failed: Errcode %s' % (get_id(infile_c), exn, printable(ret, workdir)), file = sys.stderr)
    return 0
  def gen_cmd(workdir, ex_dir, ex_no, testfile):
    cmd = os.path.join(workdir, ex_dir, ex_no)
    cmd = ' '.join([cmd, os.path.join(workdir, ex_dir, '%s.in'%(testfile))])
    cmd = ' '.join([cmd, '|', 'diff', os.path.join(workdir, ex_dir, '%s.out'%(testfile)), '-'])
    return cmd

  cmd = gen_cmd(workdir, ex_dir, 'ex2', 'ultra_test')
  try:
    ret = get_output(cmd, path = os.path.join(workdir, ex_dir))
  except Exception as e:
    print('[%s][%s] Runtime error with \'ultra_test.in\' testcase. %s' % (get_id(infile_c), exn, printable(e, workdir)), file = sys.stderr)
    score[1] = 0
  else:
    if len(ret) > 2:
      print('[%s][%s] Wrong output with \'ultra_test.in\' testcase' % (get_id(infile_c), exn), file = sys.stderr)
      score[1] = 0
    else:
      score[1] = 2

  files = ['functions.c', 'functions.h', 'function_pointers.c', 'function_pointers.h', 'fp_test.in', 'fp_test.out']
  copy_testing_files(sol_dir, workdir, 'ex2_fptest', files)
  cmd = "make fptest -C %s > /dev/null 2>&1" %(os.path.join(workdir, ex_dir))
  try:
    ret = ex(cmd)
  except subprocess.CalledProcessError as e:
    print('[%s][%s] Function pointer test. Compilation failed: %s' % (get_id(infile_c), exn, printable(e, workdir)), file = sys.stderr)
    return math.floor(sum(score))
  if not ret:
    score[2] = 2
  else:
    print('[%s][%s] Function pointer test. Compilation failed: Errcode %s' % (get_id(infile_c), exn, printable(ret, workdir)), file = sys.stderr)
    return math.floor(sum(score))

  cmd = gen_cmd(workdir, ex_dir, 'fptest', 'fp_test')
  try:
    ret = get_output(cmd, path = os.path.join(workdir, ex_dir))
  except Exception as e:
    print('[%s][%s] Runtime error with function pointer test using \'fp_test.in\'. %s' % (get_id(infile_c), exn, printable(e, workdir)), file = sys.stderr)
    score[3] = 0
  else:
    if len(ret) > 2:
      print('[%s][%s] Function pointer test failed using \'fp_test.in\'' % (get_id(infile_c), exn), file = sys.stderr)
      score[3] = 0
    else:
      score[3] = 2

  return math.floor(sum(score))

def ex3(infile_c, workdir, sol_dir):
  exn = 'ex3'
  num_qparts = 2
  score = [0.0] * num_qparts
  apps_to_check = []
  test_in = 'big_test.in'
  app1 = os.path.join(workdir, 'ex1', 'ex1')
  if not os.path.isfile(app1):
    score[0] = 0
    print('[%s][%s] Executable file \'ex1\' not found' % (get_id(infile_c), exn), file = sys.stderr)
    apps_to_check.append(-1)
  else:
    app1 = ' '.join([app1, '<', os.path.join(workdir, 'ex1', test_in)])
    apps_to_check.append(app1)
  app2 = os.path.join(workdir, 'ex2', 'ex2')
  if not os.path.isfile(app2):
    score[1] = 0
    print('[%s][%s] Executable file \'ex2\' not found' % (get_id(infile_c), exn), file = sys.stderr)
    apps_to_check.append(-1)
  else:
    app2 = ' '.join([app2, os.path.join(workdir, 'ex2', test_in)])
    apps_to_check.append(app2)
  if not apps_to_check:
    return math.floor(sum(score))
  for it, app in enumerate(apps_to_check):
    if app == -1:
      continue
    ret = ''
    cmd = "valgrind  --leak-check=full --show-leak-kinds=all -q  %s > /dev/null 2>&1" % (app)
    try:
      ret = get_output(cmd, path = workdir, timeout=10)
    except Exception as e:
      print('[%s][%s] Runtime error. %s' % (get_id(infile_c), exn, printable(e, workdir)), file = sys.stderr)
      return -2
    if len(ret) > 2:
      print('[%s][%s] Error: %s' % (get_id(infile_c), exn, printable(ret, workdir)), file = sys.stderr)
      score[it] = -1
    else:
      score[it] = 0
  return math.floor(sum(score))

def ex4(infile_c, workdir, sol_dir):
  exn = 'ex4'
  num_qparts = 12
  score = [0.0] * num_qparts
  app = os.path.join(workdir, 'ex4', 'check_system.sh')
  if not os.path.isfile(app):
    print('[%s][%s] File \'check_system.sh\' not found' % (get_id(infile_c), exn), file = sys.stderr)
    return 0
  cmd = 'bash %s' %(app)
  ret = ''
  try:
    ret = get_output(cmd, path = os.path.join(workdir, 'ex4'), timeout=10)
  except Exception as e:
    print('[%s][%s] %s' % (get_id(infile_c), exn, printable(e, workdir)), file = sys.stderr)
    return 0
  ret_lines = ret.splitlines()
  for line in ret_lines: # 4 marks
    if 'Hostname:' in line:
        res = line.split(':')[-1].strip()
        if len(res) > 2:
          score[0] = 0.5
        else:
          print('[%s][%s] \'Hostname\' missing' % (get_id(infile_c), exn), file = sys.stderr)
    elif 'Linux Kernel Version:' in line:
        res = line.split(':')[-1].strip()
        if len(res) > 3:
          score[1] = 0.5
        else:
          print('[%s][%s] \'Linux Kernel Version\' missing' % (get_id(infile_c), exn), file = sys.stderr)
    elif 'Total Processes:' in line:
        res = line.split(':')[-1].strip()
        if res.isdigit() and int(res) > 3:
          score[2] = 0.5
        else:
          print('[%s][%s] \'Total Processes\' missing' % (get_id(infile_c), exn), file = sys.stderr)
    elif 'User Processes:' in line:
        res = line.split(':')[-1].strip()
        if res.isdigit():
          score[3] = 0.5
        else:
          print('[%s][%s] \'User Processes\' missing' % (get_id(infile_c), exn), file = sys.stderr)
    elif 'Memory Used (%):' in line:
        res = line.split(':')[-1].strip()
        if positive_float(res):
          score[4] = 1
        else:
          print('[%s][%s] \'Memory Used (%%)\' missing' % (get_id(infile_c), exn), file = sys.stderr)
    elif 'Swap Used (%):' in line:
        res = line.split(':')[-1].strip()
        if positive_float(res):
          score[5] = 1
        else:
          print('[%s][%s] \'Swap Used (%%)\' missing' % (get_id(infile_c), exn), file = sys.stderr)

  with open(app, 'r') as appf: # 4 marks
    for line in appf:
      if 'hostname=' in line:
        if 'hostname' in line or all(i in line for i in ['uname', '-n']):
          score[6] = 0.5
        else:
          print('[%s][%s] Script for \'hostname\' missing' % (get_id(infile_c), exn), file = sys.stderr)
      elif 'kernel_version=' in line:
        if all(i in line for i in ['uname', '-r']):
          score[7] = 0.5
        else:
          print('[%s][%s] Script for \'kernel_version\' missing' % (get_id(infile_c), exn), file = sys.stderr)
      elif 'user_process_cnt=' in line:
        if all(i in line for i in ['ps', 'wc']):
          score[9] = 0.5
        else:
          print('[%s][%s] Script for \'user_process_cnt\' missing' % (get_id(infile_c), exn), file = sys.stderr)
      elif 'process_cnt=' in line:
        if all(i in line for i in ['ps', 'wc']):
          score[8] = 0.5
        else:
          print('[%s][%s] Script for \'process_cnt\' missing' % (get_id(infile_c), exn), file = sys.stderr)
      elif 'mem_usage=' in line:
        if all(i in line for i in ['free', 'awk']):
          score[10] = 1
        else:
          print('[%s][%s] Script for \'mem_usage\' missing' % (get_id(infile_c), exn), file = sys.stderr)
      elif 'swap_usage=' in line:
        if all(i in line for i in ['free', 'awk']):
          score[11] = 1
        else:
          print('[%s][%s] Script for \'swap_usage\' missing' % (get_id(infile_c), exn), file = sys.stderr)
  return math.floor(sum(score))

def ex5(infile_c, workdir, sol_dir):
  exn = 'ex5'
  score = 0
  app = os.path.join(workdir, 'ex5', 'check_syscalls.sh')
  if not os.path.isfile(app):
    print("[%s][%s] File \'check_syscalls.sh\' not found" % (get_id(infile_c), exn), file=sys.stderr)
    return score
  with open(app, 'r') as scr:
    for line in scr:
      if not line.startswith('#'):
        if 'strace' in line and any(i in line for i in ['--summary', '-c', '-C']):
          score = 4
  if score < 4:
      print("[%s][%s] Improper command" % (get_id(infile_c), exn), file=sys.stderr)
  return score
