# -*- coding: utf-8 -*-

__version__ = '0.1.0'
__date__    = 'jan 03rd, 2013'
__author__ = 'François Vincent'
__mail__ = 'fvincent@groupeseb.com'
__github__ = 'https://github.com/francois-vincent'

import subprocess, sys, os
import datetime, time

# ----------- Simple question ---------------
message = "café dans 3 minutes ?"
cmd = 'zenity --question --title="Question" --text="%s"' % message
returncode = subprocess.call(cmd, shell=True)
if not returncode:
    print "You have accepted"
else:
    print "You have refused"

# ----------- Simple warning with timeout ---------------
message = "café dans 3 minutes"
cmd = 'zenity --warning --timeout=5 --text="%s"' % message
subprocess.call(cmd, shell=True)

# ----------- multi-selection ---------------
cmd = 'zenity --list --separator="|" --title="Options" ' \
      '--multiple ' \
      '--text="Sélectionnez une option" ' \
      '--column="option" --column="description"'
options = [
    ('opt1', 'this is option 1'),
    ('opt2', 'this is option 2'),
    ('opt3', 'this is option 3'),
]
proc = subprocess.Popen(cmd, shell=True,
                       stdin=subprocess.PIPE, stdout=subprocess.PIPE)
result = proc.communicate('\n'.join('\n'.join(x) for x in options))[0].split('|')
if not proc.returncode:
    print "Your selection is:\n  "+'\n  '.join(result)
else:
    print "You have cancelled"

# ----------- multi-selection with check-box ---------------
cmd = 'zenity --list --separator="|" --title="Options" ' \
      '--checklist ' \
      '--text="Sélectionnez une option" ' \
      '--column="check" --column="option" --column="description"'
options = [
    ('', 'opt1', 'this is option 1'),
    ('', 'opt2', 'this is option 2'),
    ('', 'opt3', 'this is option 3'),
]
proc = subprocess.Popen(cmd, shell=True,
                       stdin=subprocess.PIPE, stdout=subprocess.PIPE)
result = proc.communicate('\n'.join('\n'.join(x) for x in options))[0].split('|')
if proc.returncode:
    print "You have cancelled"
else:
    print "Your selection is:\n  "+'\n  '.join(result)

# -------- input file selection with filter ----------------
cmd = 'zenity --file-selection --separator="|" --title="Input Files" ' \
      '--multiple ' \
      '--file-filter="*.txt"'
proc = subprocess.Popen(cmd, shell=True,
                       stdout=subprocess.PIPE)
result = proc.communicate()[0].split('|')
if not proc.returncode:
    print "Your selection is:\n  "+'\n  '.join(result)
else:
    print "You have cancelled"

# -------- output file selection ----------------
cmd = 'zenity --file-selection --separator="|" --title="Output File" ' \
      '--save '
proc = subprocess.Popen(cmd, shell=True,
                       stdout=subprocess.PIPE)
result = proc.communicate()[0].split('|')
if not proc.returncode:
    print "Your selection is:\n  "+'\n  '.join(result)
else:
    print "You have cancelled"

# ---------- affichage d'un texte ---------------
cmd = 'zenity --text-info --title="Code" --filename="%s"' % (sys.argv[0], )
proc = subprocess.Popen(cmd, shell=True)
proc.wait()

# -------- entrée d'un texte -----------------
username = os.environ.get('USERNAME', '')
cmd = 'zenity --entry --title="username" --text="entrez votre username" --entry-text="%s"' % username
proc = subprocess.Popen(cmd, shell=True,
                       stdout=subprocess.PIPE)
result = proc.communicate()[0]
if not proc.returncode:
    print "Your entry is:\n  "+result
else:
    print "You have cancelled"

# -------- entrée d'un mot de passe -----------------
cmd = 'zenity --entry --title="password" --text="entrez votre password" --hide-text'
proc = subprocess.Popen(cmd, shell=True,
                       stdout=subprocess.PIPE)
result = proc.communicate()[0]
if not proc.returncode:
    print "Your entry is:\n  "+result
else:
    print "You have cancelled"

# ----------- entrée d'une date -------------------------
year, month, day = datetime.date.today().isoformat().split('-')
cmd = 'zenity --calendar --title="Date Synchro" --text="Choisissez une date pour la prochaine synchro" ' \
      '--year=%s --month=%s --day=%s' % (year, month, day)
proc = subprocess.Popen(cmd, shell=True,
                       stdout=subprocess.PIPE)
result = proc.communicate()[0]
if not proc.returncode:
    print "Your entry is:\n  "+result
else:
    print "You have cancelled"

# ------- show progress bar --------------
cmd = 'zenity --progress --text="Création de l\'index" --auto-close'
proc = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
try:
    for i in xrange(100):
        proc.stdin.write("%d\n" % (i+1,))
        time.sleep(0.04)
        if proc.poll():
            break
    if not proc.returncode:
        print "Your job finished"
    else:
        print "You have cancelled"
except:
    proc.terminate()
