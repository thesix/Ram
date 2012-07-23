#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A register machine as often used in theoretic computer science.  The
concept is based on the Random Access Machine introduced in the book
'Theoretische Informatik' by Alexander Asteroth and Christel Baier
(ISBN 3-8273-7033-7).

Usage

Import Ram from this module and create an instance Ram ("filename")
where 'filename' is the name of the file containing your program text,
or run this module with your 'filename' as command line argument.

Program text is a plain text file.  Any line starting with a hash mark
('#') is ignored.  Empty lines MUST be avoided.  The first non-comment
line MUST be a series of integer numbers denoting the initial values of
your registers.  The first register (index 0) is also the accumulator
and MUST be initialized with 0.  Program text MUST be entered as

NUM COMMAND ARG

where NUM can be anything (usually the line number for orientation),
COMMAND is one of the accepted commands (see below) and ARG is the
argument for COMMAND.  Anything following ARG up to the next newline
('\n') is ignored.

COMMANDS (see meaning of arguments below):

LOAD k  :=  LOAD v(k) into accumulator
STORE k :=  STORE contents of accumulator v(k)
ADD k   :=  ADD v(k) to accumulator
SUB k   :=  SUBtract v(k) from accumulator
MULT k  :=  MULTiply accumulator by v(k)
DIV k   :=  DIVide accumulator by v(k)
GOTO k  :=  GOTO line number k
JZERO k :=  Jump to line number k if accumulator == ZERO (0)
END ?   :=  set program counter to 0 (termination)

Arguments:

x     v(x)
------------
 k    reg[k]
#k    k
*k    reg[reg[k]]

An example program can be found at the bottom of this file.  If you run
this script without arguments, the example program will be written to
a file 'tmp.ram' in your /tmp/ directory and used as input.  Not sure what
this does on non-unix-like systems ...

Copyright © 2011 Jogi Hofmüller <j.hofmueller@student.tugraz.at>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see
    <http://www.gnu.org/licenses/>.

"""

import os
import sys

class Command:


class Register:

  """
  A self expanding register, providing a quasi infinite number of
  addresses
  """

  def __init__ (self):
    self.register = []

  def append (self, value = 0):
    """
    append value to the end of register
    """
    self.register.append (value)

  def getLen (self):
    """
    return the length of register
    """
    return len (self.register)

  def setAddress (self, address, value):
    """
    set register at address to value;  expand register if necessary
    """
    if address >= len (self.register):
      self.expand (address)
    self.register[address] = value

  def getAddress (self, address):
    """
    return the value of register at address;  expand register if
    necessary
    """
    if address >= len (self.register):
      self.expand (address)
    return self.register[address]

  def expand (self, toAddress):
    """
    expand register to a length of toAddress + 1
    """
    delta = 1 + toAddress - len (self.register)
    while delta > 0:
      self.append ()
      delta -= 1

class Ram:

  def __init__ (self, filename):
    if not os.path.isfile (filename):
      raise Exception ("file '{0}' not found".format (filename))
    self.readprog (filename)
    self.pc = 1
    self.ready = True

  def readprog (self, filename):
    infile = open (filename, "r")
    self.prog = [("PROG", "REGMACHINE")]  # line 0 of program
    self.reg = []
    for line in infile.readlines ():
      tokens = line.split ()
      if tokens[0][0] == "#":
        continue
      elif len (self.reg) == 0:
        for t in tokens:
          self.reg.append (int (t))
      else:
        self.prog.append ((tokens[1], tokens[2]))
    infile.close ()

  def run (self):
    while self.pc != 0:
      try:
        cmd = self.prog[self.pc]
      except IndexError:
        raise Exception ("Abnormal Termination @pc={0}".format (self.pc))
      print "K=({0}, R[".format (self.pc),
      for i in range (0, len (self.reg)):
        print "\b({0},{1}), ".format (i, self.reg[i]),
      print "\b])"
      if cmd[0] == "LOAD":
        self.load (cmd[1])
      elif cmd[0] == "STORE":
        self.store (cmd[1])
      elif cmd[0] == "ADD":
        self.add (cmd[1])
      elif cmd[0] == "SUB":
        self.sub (cmd[1])
      elif cmd[0] == "MULT":
        self.mult (cmd[1])
      elif cmd[0] == "DIV":
        self.div (cmd[1])
      elif cmd[0] == "GOTO":
        self.goto (cmd[1])
      elif cmd[0] == "JZERO":
        self.jzero (cmd[1])
      elif cmd[0] == "END":
        self.end ()
      else:
        print "Error:  Unknown cmd {0}".format (cmd[0])
   print "result(R)={0}".format (self.reg[0])

  def load (self, oper):
    """
    index errors are caught and reg will be expanded up to
    the index in oper;  this satisfies the need of infinite registers
    initialized with 0.
    """
    try:
      self.reg[0] = self.decoper (oper)
    except IndexError:
      for i in range (len (self.reg), self.regindex (oper)):
        self.reg.append (0)
      self.reg.append (0)
      self.reg[0] = 0
    self.pc += 1

  def store (self, oper):
    """
    index errors are caught and reg will be expanded up to
    the index oper;  accumulator value will be stored at the
    index indicated by oper.
    """
    if oper[0] == "#":
      raise Exception ("STORE called with constant operand on line {0}".format (self.pc))
    try:
      self.reg[self.regindex (oper)] = self.reg[0]
    except IndexError:
      for i in range (len (self.reg), self.regindex (oper)):
        self.reg.append (0)
      self.reg.append (self.reg[0])
    self.pc += 1

  def add (self, oper):
    self.reg[0] += self.decoper (oper)
    self.pc += 1

  def sub (self, oper):
    if self.decoper (oper) > self.reg[0]:
      self.reg[0] = 0
    else:
      self.reg[0] -= self.decoper (oper)
    self.pc += 1

  def mult (self, oper):
    self.reg[0] *= self.decoper (oper)
    self.pc += 1

  def div (self, oper):
    if self.decoper (oper) == 0:
      raise Exception ("Division by zero")
    self.reg[0] /= self.decoper (oper)
    self.pc += 1

  def goto  (self, oper):
    self.pc = int (oper)

  def jzero (self, oper):
    if self.reg[0] == 0:
      self.pc = int (oper)
    else:
      self.pc += 1

  def end (self):
    self.pc = 0

  def decoper (self, oper):
    """
    decode operand
    """
    if "*" == oper[0]:
      return self.reg[self.reg [(int (oper[1:]))]]
    elif "#" == oper[0]:
      return int (oper[1:])
    else:
      return self.reg[int (oper)]

  def regindex (self, oper):
    """
    decode reg[index] argument
    """
    if "*" == oper[0]:
      return self.reg [(int (oper[1:]))]
    else:
      return int (oper)

if __name__ == "__main__":
  if len (sys.argv) == 2:
    prog = sys.argv[1]
  else:
    outfile = open ("/tmp/tmp.ram", "w")
    p = """# temporary RAM program
# multiply two numbers in R1 and R2
# first line is register initialization
0 3 6
# program text starts here
1  LOAD #0
2  STORE 3
3  LOAD 1
4  JZERO 11
5  SUB #1
6  STORE 1
7  LOAD 2
8  ADD 3
9  STORE 3
10 GOTO 3
11 LOAD 3
12 END END
# EOF"""
    outfile.write (p)
    outfile.close ()
    print "Created temporary program '/tmp/tmp.ram'"
    print p
    prog = "/tmp/tmp.ram"

  try:
    ram = Ram (prog)
    if ram.ready:
      ram.run ()
  except Exception as e:
    print "Fatal error:  {0}".format (e)
    sys.exit (-1)
  sys.exit (0)

# EOF
