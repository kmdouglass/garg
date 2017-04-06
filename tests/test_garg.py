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
import types

class FunctionSignatureTestCase(unittest.TestCase):
    def test_positional_or_keyword(self):
        """GARG detects positional or keyword arguments.
        
        """
        def test_func(a, b):
            pass
        
        c = garg.Garg(test_func)
        c.unpack_params()
        args = c.view.get_args_dict()
        
        self.assertTrue(('a' in args) and ('b' in args))
        
    def test_keyword_only(self):
        """GARG detects keyword only arguments.
        
        """
        def test_func(*, a, b):
            pass
        
        c = garg.Garg(test_func)
        c.unpack_params()
        args = c.view.get_args_dict()
        
        self.assertTrue(('a' in args) and ('b' in args))
        
    def test_default_value(self):
        """GARG correctly identifies keyword default values.
        
        """
        def test_func(a=2, b='test'):
            pass
        
        c = garg.Garg(test_func)
        c.unpack_params()
        args = c.get_arguments()
        
        self.assertEqual(args['a'], 2)
        self.assertEqual(args['b'], 'test')
        
    def test_bound_arguments(self):
        """GARG correctly binds the input values to the parameters.
        
        """
        def test_func(a=2, b='test', *, c=3):
            pass
        
        c = garg.Garg(test_func)
        c.unpack_params()
        c.on_ok_button()
        
        self.assertEqual(c.ba.args[0], 2)
        self.assertEqual(c.ba.args[1], 'test')
        self.assertEqual(c.ba.kwargs['c'], 3)

class ErrorsTestCase(unittest.TestCase):
    def test_unspecified_argument(self):
        """GARG fails to parse arguments that are not specified.
        
        """
        def test_func(a):
            pass
        
        c = garg.Garg(test_func)
        c.unpack_params()
        
        with self.assertRaises(SyntaxError):
            # Arguments were never specified because the GUI was never used
            c.get_arguments()
            
    def test_unspecified_argument_no_error(self):
        """Exceptions are overridden when ignore_syntax_errors is True.
        
        """
        def test_func(a, b=10):
            pass
        
        c = garg.Garg(test_func, ignore_syntax_errors=True)
        c.unpack_params()
        params = c.get_arguments()
        
        self.assertTrue('a' not in params)
        self.assertEqual(params['b'], 10)
            
    def test_nonvalid_python_literal(self):
        """Arguments not able to be evalulated by literal_eval raise an error.
        
        """
        def test_func(a):
            pass
        
        c = garg.Garg(test_func)
        c.unpack_params()
        
        # Build the params dict that would normally bind args to params.
        # Note that the string does contain a valid Python literal.
        params = {'a': '*+-2'}
        
        # Override the View's get_args_dict method to make it testable and
        c.view.get_args_dict = types.MethodType(lambda self: params, c.view)
        
        with self.assertRaises(SyntaxError):
            # The input argument cannot be parsed into a valid Python datatype
            c.get_arguments()
            
    def test_POSITIONAL_ONLY_raises_error(self):
        """POSITIONAL_ONLY arguments raise an error.
        
        """
        # pow accepts positional only parameters
        c = garg.Garg(pow)
        c.unpack_params()
        
        with self.assertRaises(KeyError):
            # The positional only arguments will be in the argument list
            c.get_arguments()
        
    def test_POSITIONAL_ONLY_no_error(self):
        """POSITIONAL_ONLY arguments are ignored with ignore_positional_only.
        
        """
        # pow has positional only parameters
        c = garg.Garg(pow, ignore_positional_only=True)
        c.unpack_params()
        
        c.get_arguments()
        
if __name__ == '__main__':
    unittest.main()