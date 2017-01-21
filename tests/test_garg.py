"""GUI-based function argument assignment in Python.

Author  : Kyle M. Douglass
E-mail  : kyle.m.douglass@gmail.com
Year    : 2017
License : MIT

Run this file with

> python -m unittest tests/test_garg.py

"""

import unittest
import garg

class FunctionSignatureTestCase(unittest.TestCase):
    def test_positional_or_keyword(self):
        """Controller detects positional or keyword arguments.
        
        """
        def test_func(a, b):
            pass
        
        c = garg.Controller(test_func)
        c.unpack_params()
        args = c.view.get_params_dict()
        
        self.assertTrue(('a' in args) and ('b' in args))
        
    def test_keyword_only(self):
        """Controller detects keyword only arguments.
        
        """
        def test_func(*, a, b):
            pass
        
        c = garg.Controller(test_func)
        c.unpack_params()
        args = c.view.get_params_dict()
        
        self.assertTrue(('a' in args) and ('b' in args))
        
    def test_default_value(self):
        """Controller correctly identifies keyword default values.
        
        """
        def test_func(a=2, b='test'):
            pass
        
        c = garg.Controller(test_func)
        c.unpack_params()
        args = c.get_signature()
        
        self.assertEqual(args['a'], 2)
        self.assertEqual(args['b'], 'test')

class GUIErrorsTestCase(unittest.TestCase):        
    def test_unspecified_argument(self):
        """Controller fails to parse arguments that are not specified.
        
        """
        def test_func(a):
            pass
        
        c = garg.Controller(test_func)
        c.unpack_params()
        
        with self.assertRaises(SyntaxError):
            # Arguments were never specified because the GUI was never used
            c.get_signature() 
        
if __name__ == '__main__':
    unittest.main()