"""GUI-based function argument assignment in pure Python.

GARG reads a callable's signature and creates a GUI that allows users to
interactively assign values to the callable's arguments. For security reasons,
only positional-or-keyword and keyword-only parameters that accept basic Python
datatypes are supported; all other parameters must be bound in the traditional
way.

Authors  : Kyle M. Douglass
           Felix Schaber
E-mail   : kyle.m.douglass@gmail.com
Year     : 2017
License  : MIT

"""

import inspect
import sys
import tkinter as tk
from collections import OrderedDict
from ast import literal_eval

# TODO:
# 1. [X] Handle None vs. '' (empty string) (ast.literal_eval evaluates None)
# 2. [X] Convert strings from View entries to Python objects (ast.literal_eval)
# 3. [X] Decide what Controller should return (function with bound arguments?)
# 4. [X] Add option for Controller to raise error or ignore unspecified args
# 5. [X] Finish docstrings
# 6. [X] Ensure that words parameter and argument are used correctly in code
# 7. [X] ~~Add wrapper to Controller so user only has to call 'garg'~~
# 8. [X] Write documentation
# 9. [X] Write tests
# 10. [X] Fix label frame scrolling bug
# 11. [X] Fix alignment of Labels and Entries
# 12. [X] Fix full window resize of widgets bug
# 13. [ ] Create setup.py and write installation instructions

class Garg():
    """Reads function parameters and assigns argument values using a GUI.
    
    Parameters
    ----------
    func : function
        The function for which the parameter signature will be extracted.
    ignore_errors : bool
        Decides whether the program raises an error if arguments are not
        syntactically correct. If True, the program skips missing arguments
        and returns a partially bound argument list.
        
    Attributes
    ----------
    ba    : BoundArguments
        Argument values bound to the parameters specified in the GUI.
    model : Signature
        The input function's call signature. This is a Signature object from
        the standard library's inspect module and serves as the Model in the
        Model-View-Controller pattern.
    view  : Frame
        The GUI presented to the user.
    ignore_errors : bool
        Decides whether the program raises an error if arguments are not
        syntactically correct. If True, the program skips missing arguments
        and returns a partially bound argument list.
    
    """
    _ARG_TYPES = (
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
        inspect.Parameter.KEYWORD_ONLY
    )
    
    def __init__(self, func, ignore_errors=False):
        self.root = tk.Tk()
        
        self.model = inspect.signature(func)
        self.view  = View(self.root, self.on_ok_button, self.on_cancel_button)
        self.ba    = None
        
        self.ignore_errors = ignore_errors
        
    def get_arguments(self):
        """Returns the values of the arguments set in the GUI.
        
        Returns
        -------
        params : OrderedDict
            Name/value pairs of parameter names and argument values in the same
            order as the input function's signature.
           
        """
        view_params = self.view.get_args_dict()
        params      = OrderedDict({})
        
        # Build the parameter list to bind to arguments; assumes the parameter
        # list in the model is in the same order as the function signature.
        for param in self.model.parameters.values():
            try:
                params[param.name] = literal_eval(view_params[param.name])
            except SyntaxError:
                # Skip adding parameter to params if ignore_errors is True
                if not self.ignore_errors:
                    raise(SyntaxError(('Parameter \"%s\"\'s argument %s is '
                                       'either not a valid Python literal or '
                                       'is unspecified.' % (param.name, view_params[param.name]))))
            except:
                print("Unexpected error:", sys.exc_info()[0])
                raise
            
        return params
    
    def run(self):
        """Launches the main GUI window.
        
        """
        self.root.title('GARG: GUI-Based Argument Assignment')
        self.root.deiconify()
        self.unpack_params()
        self.root.mainloop()
        
    def on_cancel_button(self):
        """Callback for the Cancel button.
        
        """
        self.root.destroy() 

    def on_ok_button(self):
        """Callback for the OK button.
        
        """
        args = self.get_arguments()
        self.ba = self.model.bind_partial(**args)
    
    def unpack_params(self):
        """Extracts parameters from the signature and places them in the GUI.
        
        """
        # TODO: Clean this up
        for arg_type in self._ARG_TYPES:
            group_exists = False
            
            for param in self.model.parameters.values():
                if param.kind == arg_type:
                    
                    # Create new LabelFrame for this type if it doesn't exist
                    if not group_exists:
                        group = self.view.add_parameter_group(
                                    text=arg_type.name)
                        group_exists = True
                    
                    # Add Label and Entry for this argument
                    self.view.add_parameter_entry(group, param)
                    
class View(tk.Frame):
    """Displays a GUI interface for assigning values to function parameters.
    
    Parameters
    ----------
    master    : Tk
        The master Tk instance.
    on_ok     : method
        OK button callback.
    on_cancel : method
        Cancel button callback.
    
    """
    def __init__(self, master, on_ok, on_cancel):
        super().__init__(master)
        self._argdict = {}
        
        tk.Grid.rowconfigure(self.master, 0, weight=1)
        tk.Grid.rowconfigure(self.master, 1, weight=0)
        tk.Grid.columnconfigure(self.master, 0, weight=1)
        tk.Grid.columnconfigure(self.master, 1, weight=0)
        
        self._vsb    = tk.Scrollbar(self.master, orient='vertical')
        self._canvas = tk.Canvas(
            self.master,
            width=400,
            height=300)
        self._buttonFrame = self.ButtonFrame(self.master,on_ok,on_cancel)
        
        # _group_frame is a single frame that is drawn onto the canvas.
        # It contains (possibly) multiple LabelFrames vertically stacked.
        self._group_frame  = tk.Frame(self._canvas)

        self._canvas.create_window(
            (0, 0),
            window=self._group_frame,
            anchor='nw',
            tags=('frame'))
        self._canvas.configure(yscrollcommand=self._vsb.set)
        self._canvas.bind('<Configure>', self._on_canvas_resize)
        self._vsb.config(command=self._canvas.yview)
        
        self._canvas.grid(row=0, column=0, sticky=tk.N+tk.S+tk.E+tk.W)
        self._vsb.grid(row=0, column=1, sticky=tk.N+tk.S)
        self._buttonFrame.grid(row=1, columnspan=2)
        
        # Keeps track of the row number in a parameter group
        self._currRow = 0

    def _on_canvas_resize(self, event=None):
        """Resizes the group frame when the canvas is resized.
        
        Parameters
        ----------
        event : Event
        
        """
        width = self._canvas.winfo_width()
        self._canvas.itemconfigure('frame', width=width)
        self._canvas.config(scrollregion=self._canvas.bbox('all'))
    
    def add_parameter_group(self, **kwargs):
        """Creates a LabelFrame to hold widgets for a single parameter type.
        
        Parameters
        ----------
        **kwargs : dict
            Key/value pairs to pass to the LabelFrame constructor.
        
        Returns
        -------
        lf : LabelFrame
            The container of Label and Entry widgets to set argument values.
            
        """
        self._currRow = 0
        lf = tk.LabelFrame(self._group_frame, **kwargs)
        lf.pack(fill=tk.BOTH, expand=1)
        
        return lf
        
    def add_parameter_entry(self, master, param):
        """Creates a Label and Entry for a single parameter.
        
        Parameters
        ----------
        master : LabelFrame
            The parent frame containing the Label + Entry widgets.
        param : Parameter
            Parameter containing the information for populating the Entry and
            Label widgets.
            
        """
        tk.Grid.columnconfigure(master, 0, weight=0)
        tk.Grid.columnconfigure(master, 1, weight=1)
        
        lb = tk.Label(master, text=param.name)
        box = tk.Entry(master)
        
        if param.default is not param.empty:
            # __repr__() ensures a Python literal is printed
            box.insert(0,param.default.__repr__()) 

        # Keep a reference to get content of box later
        self._argdict[param.name] = box
        lb.grid(row=self._currRow, column=0, padx=10)             
        box.grid(row=self._currRow, column=1, sticky=tk.E+tk.W)
        self._currRow += 1

    def get_args_dict(self):
        """Creates a dict containing argument values specified in the GUI.
        
        Returns
        -------
        args : dict
            Key/value pairs of parameter names and assigned argument values.
            
        """
        args = {name : entry.get() for name, entry in self._argdict.items()}
        return args
        
    class ButtonFrame(tk.Frame):
        """Contains the OK and Cancel buttons.
        
        Parameters
        ----------
        master : Tk
            The master Tk instance.
        on_ok : method
            OK button callback.
        on_cancel : method
            Cancel button callback.
        
        """
        def __init__(self, master, on_ok, on_cancel):
            super().__init__(master)
            
            ok_button     = tk.Button(master=self, text='OK'    ,command=on_ok)
            cancel_button = tk.Button(master=self, text='Cancel',command=on_cancel)
            
            ok_button.pack(side=tk.LEFT)
            cancel_button.pack(side=tk.RIGHT)
        
if __name__ == '__main__':
    def test(a, b, *, c, d=10, e='hello', f=[1, 2, 'hello', {'a': 2}], g=None):
        pass
    
    c = Garg(test)
    c.run()
    print(c.ba)
    print(c.ba.args)
    print(c.ba.kwargs)