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
        """Garg detects positional or keyword arguments.
        
        """
        def test_func(a, b):
            pass
        
        c = garg.Garg(test_func)
        c.unpack_params()
        args = c.view.get_args_dict()
        
        self.assertTrue(('a' in args) and ('b' in args))
        
    def test_keyword_only(self):
        """Garg detects keyword only arguments.
        
        """
        def test_func(*, a, b):
            pass
        
        c = garg.Garg(test_func)
        c.unpack_params()
        args = c.view.get_args_dict()
        
        self.assertTrue(('a' in args) and ('b' in args))
        
    def test_default_value(self):
        """Garg correctly identifies keyword default values.
        
        """
        def test_func(a=2, b='test'):
            pass
        
        c = garg.Garg(test_func)
        c.unpack_params()
        args = c.get_arguments()
        
        self.assertEqual(args['a'], 2)
        self.assertEqual(args['b'], 'test')

class GUIErrorsTestCase(unittest.TestCase):        
    def test_unspecified_argument(self):
        """Garg fails to parse arguments that are not specified.
        
        """
        # TODO: Write a test case for the inverse of this when error_on_syntax
        # is False.
        def test_func(a):
            pass
        
        c = garg.Garg(test_func)
        c.unpack_params()
        
        with self.assertRaises(SyntaxError):
            # Arguments were never specified because the GUI was never used
            c.get_arguments() 
        
if __name__ == '__main__':
    unittest.main()