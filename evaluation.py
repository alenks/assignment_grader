import os, sys, subprocess, math
import shutil, re, errno

def get_output(cmd):
  return subprocess.getoutput(cmd).strip()

def ex(cmd):
  return os.system(cmd)

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
  dst_dir = os.path.join(workdir, ex_dir)
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




def ex1(infile_c, workdir, sol_dir):
  score = [0.0] * 3
  ex_dir = 'ex1'
  files = ['Makefile', 'ex1.c', 'node.h', 'big_test.in', 'big_test.out', 'ultra_test.in', 'ultra_test.out',]
  copy_testing_files(sol_dir, workdir, ex_dir, files)
  if not os.path.isfile(os.path.join(workdir, ex_dir, 'node.c')):
    return 0
  cmd = "make -C %s > /dev/null" %(os.path.join(workdir, ex_dir))
  if not ex(cmd):
    score[0] = 2
  else:
    return 0
  def gen_cmd(workdir, ex_dir, ex_no, testfile):
    cmd = os.path.join(workdir, ex_dir, ex_no)
    cmd = ' '.join([cmd, '<', os.path.join(workdir, ex_dir, '%s.in'%(testfile))])
    cmd = ' '.join([cmd, '|', 'diff', os.path.join(workdir, ex_dir, '%s.out'%(testfile)), '-'])
    return cmd

  cmd = gen_cmd(workdir, ex_dir, 'ex1', 'big_test')
  try:
    ret = get_output(cmd)
  except subprocess.CalledProcessError as e:
    print(e.output, file = sys.stderr)
    return 2
  if len(ret) > 2:
    return 2
  score[1] = 2

  cmd = gen_cmd(workdir, ex_dir, 'ex1', 'ultra_test')
  try:
    ret = get_output(cmd)
  except subprocess.CalledProcessError as e:
    print(e.output, file = sys.stderr)
    return 4
  if len(ret) > 2:
    return 4
  score[2] = 4

  return math.floor(sum(score))

def ex2(infile_c, workdir, sol_dir):
  score = [0.0]*3
  ex_dir = 'ex2'
  files = ['Makefile', 'node.h', 'functions.c', 'functions.h', 'big_test.in', 'big_test.out', 'ultra_test.in', 'ultra_test.out']
  copy_testing_files(sol_dir, workdir, ex_dir, files)
  if not os.path.isfile(os.path.join(workdir, ex_dir, 'node.c')):
    return 0
  cmd = "make -C %s > /dev/null" %(os.path.join(workdir, ex_dir))
  if not ex(cmd):
    score[0] = 2
  else:
    return 0
  def gen_cmd(workdir, ex_dir, ex_no, testfile):
    cmd = os.path.join(workdir, ex_dir, ex_no)
    cmd = ' '.join([cmd, os.path.join(workdir, ex_dir, '%s.in'%(testfile))])
    cmd = ' '.join([cmd, '|', 'diff', os.path.join(workdir, ex_dir, '%s.out'%(testfile)), '-'])
    return cmd

  cmd = gen_cmd(workdir, ex_dir, 'ex1', 'big_test')
  try:
    ret = get_output(cmd)
  except subprocess.CalledProcessError as e:
    print(e.output, file = sys.stderr)
    return 2
  if len(ret) > 2:
    return 2
  score[1] = 2

  cmd = gen_cmd(workdir, ex_dir, 'ex1', 'ultra_test')
  try:
    ret = get_output(cmd)
  except subprocess.CalledProcessError as e:
    print(e.output, file = sys.stderr)
    return 4
  if len(ret) > 2:
    return 4
  score[2] = 4

  return math.floor(sum(score))

def ex3(infile_c, workdir, sol_dir):
  apps_to_check = []
  test_in = 'big_test.in'
  app1 = os.path.join(workdir, 'ex1', 'ex1')
  app1 = ' '.join([app1, '<', os.path.join(workdir, 'ex1', test_in)])
  apps_to_check.append(app1)
  app2 = os.path.join(workdir, 'ex2', 'ex2')
  app2 = ' '.join([app2, os.path.join(workdir, 'ex2', test_in)])
  apps_to_check.append(app2)
  score = 0
  for app in apps_to_check:
    ret = ''
    cmd = "valgrind  --leak-check=full --show-leak-kinds=all -q  %s > /dev/null" % (app)
    try:
      ret = get_output(cmd)
    except subprocess.CalledProcessError as e:
      print(e.output, file = sys.stderr)
      return -2
    if len(ret) > 2:
      score -= 1
  return score

def ex4(infile_c, workdir, sol_dir):
  num_qparts = 12
  score = [0.0] * num_qparts
  app = os.path.join(workdir, 'ex4', 'check_system.sh')
  cmd = 'bash %s' %(app)
  ret = ''
  try:
    ret = get_output(cmd)
  except subprocess.CalledProcessError as e:
    print(e.output, file = sys.stderr)
    return 0
  ret_lines = ret.splitlines()
  for line in ret_lines: # 4 marks
    if 'Hostname:' in line:
        res = line.split(':')[-1].strip()
        if len(res) > 2:
          score[0] = 0.5
    elif 'Linux Kernel Version:' in line:
        res = line.split(':')[-1].strip()
        if len(res) > 3:
          score[1] = 0.5
    elif 'Total Processes:' in line:
        res = line.split(':')[-1].strip()
        if res.isdigit() and int(res) > 3:
          score[2] = 0.5
    elif 'User Processes:' in line:
        res = line.split(':')[-1].strip()
        if res.isdigit():
          score[3] = 0.5
    elif 'Memory Used (%):' in line:
        res = line.split(':')[-1].strip()
        if positive_float(res):
          score[4] = 1
    elif 'Swap Used (%):' in line:
        res = line.split(':')[-1].strip()
        if positive_float(res):
          score[5] = 1

  with open(app, 'r') as appf: # 4 marks
    for line in appf:
      if 'hostname=' in line:
        if 'hostname' in line or all(i in line for i in ['uname', '-n']):
          score[6] = 0.5
      elif 'kernel_version=' in line:
        if all(i in line for i in ['uname', '-r']):
          score[7] = 0.5
      elif 'user_process_cnt=' in line:
        if all(i in line for i in ['ps', 'wc']):
          score[9] = 0.5
      elif 'process_cnt=' in line:
        if all(i in line for i in ['ps', 'wc']):
          score[8] = 0.5
      elif 'mem_usage=' in line:
        if all(i in line for i in ['free', 'awk']):
          score[10] = 1
      elif 'swap_usage=' in line:
        if all(i in line for i in ['free', 'awk']):
          score[11] = 1
  return math.floor(sum(score))

def ex5(infile_c, workdir, sol_dir):
  score = 0
  with open(os.path.join(workdir, 'ex5', 'check_syscalls.sh'), 'r') as scr:
    for line in scr:
      if not line.startswith('#'):
        if 'strace' in line and any(i in line for i in ['--summary', '-c', 'C']):
          score = 4
  return score
