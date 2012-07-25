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
  """
  base class for all commands.
  """
  
  def __init__ (self, register):
    self.reg = register

  def decoper (self, oper):
    """
    decode operand and return it´s value
    """
    if "*" == oper[0]:
      return self.reg.getAddress (self.reg.getAddress (int (oper[1:])))
    elif "#" == oper[0]:
      return int (oper[1:])
    else:
      return self.reg.getAddress (int (oper))

  def regindex (self, oper):
    """
    decode reg[index] argument
    """
    if "*" == oper[0]:
      return self.reg.getAddress (int (oper[1:]))
    else:
      return int (oper)

class CommandLoad (Command):
  """
  load operand into accumulator
  """

  def execute (self, oper):
    self.reg.setAccumulator (self.decoper (oper))
    self.reg.incrementPc ()

class CommandStore (Command):
  """
  store accumulator in register specified by operand
  """

  def execute (self, oper):
    if oper[0] == "#":
      raise Exception ("STORE called with constant operand on line {0}".format
                       (self.reg.getPc ()))
    address = self.regindex (oper)
    if address == 0:
      raise Exception ("illegal address 0 for STORE on line {0}".format
                       (self.reg.getPc ()))
    self.reg.setAddress (address, self.reg.getAccumulator ())
    self.reg.incrementPc ()

class CommandAdd (Command):
  """
  add operand to accumulator
  """

  def execute (self, oper):
    self.reg.setAccumulator (self.reg.getAccumulator () + self.decoper (oper))
    self.reg.incrementPc ()

class CommandSub (Command):
  """
  subtract operand from accumulator
  """

  def execute (self, oper):
    if self.decoper (oper) > self.reg.getAccumulator ():
      self.reg.setAccumulator (0)
    else:
      self.reg.setAccumulator (self.reg.getAccumulator () - self.decoper (oper))
    self.reg.incrementPc ()

class CommandMult (Command):
  """
  multiply accumulator by operand
  """

  def execute (self, oper):
    self.reg.setAccumulator (self.reg.getAccumulator () * self.decoper (oper))
    self.reg.incrementPc ()

class CommandDiv (Command):
  """
  divide accumulator by operand
  """

  def execute (self, oper):
    if self.decoper (oper) == 0:
      raise Exception ("Division by zero")
    self.reg.setAccumulator (self.reg.getAccumulator () / self.decoper (oper))
    self.reg.incrementPc ()

class CommandGoto (Command):
  """
  goto line number
  """

  def execute  (self, oper):
    if oper[0] == "#" or oper[0] == "*":
      raise Exception ("GOTO called with illegal operand on line {0}".format
                       (self.reg.getPc ()))
    self.reg.setPc (int (oper))

class CommandJzero (Command):
  """
  jump to given line if accumulator is 0 or increase pc by 1 if not
  """

  def execute (self, oper):
    if oper[0] == "#" or oper[0] == "*":
      raise Exception ("JZERO called with illegal operand on line {0}".format
                       (self.reg.getPc ()))
    if self.reg.getAccumulator () == 0:
      self.reg.setPc (int (oper))
    else:
      self.reg.incrementPc ()

class CommandEnd (Command):
  """
  end the current program by setting pc to 0
  """

  def execute (self, oper):
    self.reg.setPc (0)

class CommandHandler:

  def __init__ (self, register):
    """
    initialize the handler and create instances of all commands
    """
    self.verbosity = 1
    self.reg= register
    self.commands = {}
    self.commands ["LOAD"] = CommandLoad (self.reg);
    self.commands ["STORE"] = CommandStore (self.reg);
    self.commands ["ADD"] = CommandAdd (self.reg);
    self.commands ["SUB"] = CommandSub (self.reg);
    self.commands ["MULT"] = CommandMult (self.reg);
    self.commands ["DIV"] = CommandDiv (self.reg);
    self.commands ["JZERO"] = CommandJzero (self.reg);
    self.commands ["GOTO"] = CommandGoto (self.reg);
    self.commands ["END"] = CommandEnd (self.reg);

  def execute (self, cmd):
    """
    execute the command cmd[0] with operand cmd[1]
    @param cmd list with command name and operand
    """
    try:
      if self.verbosity > 0:
        self.reg.printStatus ()
      self.commands[cmd[0]].execute (cmd[1])
    except KeyError as e:
      print "Command {0} not found".format (cmd[0])

  def setVerbosity (self, verbosity):
    """
    set verbosity
    @param verbosity new value of verbosity
    """
    self.verbosity = verbosity

class Register:

  """
  A self expanding register, providing a quasi infinite number of
  addresses
  """

  def __init__ (self):
    self.register = []
    # call by reference on primitives does not work;  therefor
    # we inellegantly put the program counter here ...
    self.pc = 1

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

  def setAccumulator (self, value):
    """
    set address 0 to value
    """
    self.setAddress (0, value)

  def getAccumulator (self):
    """
    return the value at address 0
    """
    return self.getAddress (0)

  def expand (self, toAddress):
    """
    expand register to a length of toAddress + 1
    """
    delta = 1 + toAddress - len (self.register)
    while delta > 0:
      self.append ()
      delta -= 1

  def getPc (self):
    """
    return the program counter´s value
    """
    return self.pc

  def setPc (self, pc):
    """
    set the program counter to pc
    @param pc the new value of the program counter
    """
    self.pc = pc

  def incrementPc (self):
    """
    increment the program counter by 1
    """
    self.pc += 1

  def printStatus (self):
    """
    print the current register status to stdout
    """
    print "K=({0}, R[".format (self.getPc ()),
    for i in range (0, self.getLen ()):
      print "\b({0},{1}), ".format (i, self.getAddress (i)),
    print "\b])"

class Ram:
  """
  the random access machine
  """

  def __init__ (self, filename):
    if not os.path.isfile (filename):
      raise Exception ("file '{0}' not found".format (filename))
    self.reg = Register ()
    self.readprog (filename)
    self.commandHandler = CommandHandler (self.reg)

  def readprog (self, filename):
    infile = open (filename, "r")
    self.prog = [("PROG", "REGMACHINE")]  # line 0 of program
    for line in infile.readlines ():
      token = line.split ()
      if token[0][0] == "#":
        continue
      elif token[0] == "REGINIT":
        for word in token[1:]:
          self.reg.append (int (word))
      else:
        self.prog.append ((token[1], token[2]))
    infile.close ()

  def run (self):
    while self.reg.getPc () != 0:
      try:
        cmd = self.prog[self.reg.getPc ()]
      except IndexError:
        raise Exception ("Abnormal Termination @pc={0}".format (self.reg.getPc ()))
      self.commandHandler.execute (cmd)
    print "result(R)={0}".format (self.reg.getAccumulator ())

if __name__ == "__main__":
  if len (sys.argv) == 2:
    prog = sys.argv[1]
  else:
    outfile = open ("/tmp/tmp.ram", "w")
    p = """# temporary RAM program
# multiply two numbers in R1 and R2
# this line initializes the registers 0, 1 and 2
REGINIT 0 3 6
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
    ram.run ()
  except Exception as e:
    print "Fatal error:  {0}".format (e)
    sys.exit (-1)
  sys.exit (0)

# EOF
