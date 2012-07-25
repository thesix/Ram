#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Ram import Register, CommandHandler
import unittest

class TestRegister (unittest.TestCase):

  def setUp (self):
    self.reg = Register ()

  def tearDown (self):
    del self.reg

  def testAppend (self):
    self.assertEqual (self.reg.getLen (), 0, 'register´s length should be 0')
    self.reg.append (10)
    self.assertEqual (self.reg.getLen (), 1, 'register´s length should be 1')
    self.assertEqual (self.reg.getAccumulator (), 10, 'accumulator value should be 10')

  def testSetAccumulator (self):
    self.reg.setAccumulator (10)
    self.assertEqual (self.reg.getAccumulator (), 10, 'accumulator value should be 10')

  def testRegisterExpansion (self):
    self.reg.setAddress (10, 20)
    self.assertEqual (self.reg.getLen (), 11, 'register´s length should be 11')
    # values at addresses 0 to 9 should be 0
    for i in range (0, self.reg.getLen () - 1):
      self.assertEqual (self.reg.getAddress (i), 0, 'address´ value at {0} should be 0'.format (i))
    # value at address 10 should be 20
    self.assertEqual (self.reg.getAddress (10), 20)

  def testInitialPc (self):
    self.assertEqual (self.reg.getPc (), 1, 'PC should be 1')

  def testIncrementPc (self):
    self.reg.incrementPc ()
    self.assertEqual (self.reg.getPc (), 2, 'PC should be 2')

class TestCommands (unittest.TestCase):

  def setUp (self):
    self.reg = Register ()
    self.handler = CommandHandler (self.reg)
    self.handler.setVerbosity (0)

  def tearDown (self):
    del self.handler
    del self.reg

  def testCommandLoad (self):
    self.reg.setAddress (1, 10)
    self.reg.setAddress (2, 3)
    self.reg.setAddress (3, 30)
    self.handler.execute (('LOAD', '#1'))
    self.assertEqual (self.reg.getAccumulator (), 1)
    self.handler.execute (('LOAD', '1'))
    self.assertEqual (self.reg.getAccumulator (), 10)
    self.handler.execute (('LOAD', '*2'))
    self.assertEqual (self.reg.getAccumulator (), 30)

  def testCommandStore (self):
    self.reg.setAccumulator (10)
    self.handler.execute (('STORE', '1'))
    self.assertEqual (self.reg.getAddress (1), 10)
    self.reg.setAccumulator (20)
    self.reg.setAddress (1, 2)
    self.handler.execute (('STORE', '2'))
    self.handler.execute (('STORE', '*1'))
    self.assertEqual (self.reg.getAddress (2), 20)
    with self.assertRaises (Exception):
      self.handler.execute (('STORE', '#1'))
    with self.assertRaises (Exception):
      self.handler.execute (('STORE', '0'))

  def testCommandAdd (self):
    self.reg.setAddress (0, 0)
    self.reg.setAddress (1, 1)
    self.reg.setAddress (2, 1)
    self.handler.execute (('ADD', '#1'))
    self.assertEqual (self.reg.getAccumulator (), 1)
    self.handler.execute (('ADD', '1'))
    self.assertEqual (self.reg.getAccumulator (), 2)
    self.handler.execute (('ADD', '*2'))
    self.assertEqual (self.reg.getAccumulator (), 3)

  def testCommandSub (self):
    self.reg.setAddress (0, 3)
    self.reg.setAddress (1, 1)
    self.reg.setAddress (2, 1)
    self.handler.execute (('SUB', '#1'))
    self.assertEqual (self.reg.getAccumulator (), 2)
    self.handler.execute (('SUB', '1'))
    self.assertEqual (self.reg.getAccumulator (), 1)
    self.handler.execute (('SUB', '*2'))
    self.assertEqual (self.reg.getAccumulator (), 0)
    self.handler.execute (('SUB', '#1'))
    self.assertEqual (self.reg.getAccumulator (), 0)

  def testCommandGoto (self):
    self.handler.execute (('GOTO', '2'))
    self.assertEqual (self.reg.getPc (), 2)
    with self.assertRaises (Exception):
      self.handler.execute (('GOTO', '#2'))
    with self.assertRaises (Exception):
      self.handler.execute (('GOTO', '*2'))

  def testCommandJzero (self):
    self.handler.execute (('JZERO', '10'))
    self.assertEqual (self.reg.getPc (), 10)
    self.reg.setAccumulator (1)
    self.reg.setPc (1)
    self.handler.execute (('JZERO', '10'))
    self.assertEqual (self.reg.getPc (), 2)
    with self.assertRaises (Exception):
      self.handler.execute (('JZERO', '#2'))
    with self.assertRaises (Exception):
      self.handler.execute (('JZERO', '*2'))

  def testCommandEnd (self):
    self.handler.execute (('END', 'ENDING'))
    self.assertEqual (self.reg.getPc (), 0)

if __name__ == "__main__":
  suite = unittest.TestLoader().loadTestsFromTestCase (TestRegister)
  unittest.TextTestRunner (verbosity = 2).run (suite)
  suite = unittest.TestLoader().loadTestsFromTestCase (TestCommands)
  unittest.TextTestRunner (verbosity = 2).run (suite)
  
