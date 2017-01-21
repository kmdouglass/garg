"""GUI-based function argument assignment in Python.

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
# 3. [ ] Decide what Controller should return (function with bound arguments?)
# 4. [X] Add option for Controller to raise error or ignore unspecified args
# 5. [ ] Finish docstrings
# 6. [ ] Ensure that words parameter and argument are used correctly in code
# 7. [ ] Add wrapper to Controller so user only has to call 'garg'
# 8. [ ] Write documentation
# 9. [ ] Write tests
# 10. [ ] Fix label frame scrolling bug
# 11. [ ] Fix alignment of Labels and Entries

class Controller():
    """Reads function arguments and assigns values via the GUI interface.
    
    Parameters
    ----------
    func : function
        The function for which the parameter signature will be extracted.
    error_on_syntax : bool
        Decides whether the program raises an error if arguments are not
        syntactically correct. If False, the program skips missing arguments
        and returns a partially bound argument list.
        
    Attributes
    ----------
    model : Signature
        The input function's call signature. This is a Signature object from
        the standard library's inspect module and serves as the Model in the
        Model-View-Controller pattern.
    view  : tk.Frame
        The GUI presented to the user.
    error_on_syntax : bool
        Decides whether the program raises an error if arguments are not
        syntactically correct. If False, the program skips missing arguments
        and returns a partially bound argument list.
    
    """
    _ARG_TYPES = (
        inspect.Parameter.POSITIONAL_ONLY,
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
        inspect.Parameter.VAR_POSITIONAL,
        inspect.Parameter.KEYWORD_ONLY,
        inspect.Parameter.VAR_KEYWORD
    )
    
    def __init__(self, func, error_on_syntax=True):
        self.root = tk.Tk()
        
        self.model = inspect.signature(func)
        self.view  = View(self.root,self.on_ok_button,self.on_cancel_button)
        
        self.error_on_syntax = error_on_syntax
        
    def get_signature(self):
        """Retrieve an instance of signature with the values of the arguments
           filled in
           
        """
        view_params = self.view.get_params_dict()
        params      = OrderedDict({})
        
        # Build the parameter list to bind to arguments; assumes the parameter
        # list in the model is in the same order as the function signature.
        for param in self.model.parameters.values():
            try:
                params[param.name] = literal_eval(view_params[param.name])
            except SyntaxError:
                # Skip adding parameter to params if error_on_syntax is False
                if self.error_on_syntax:
                    raise(SyntaxError(('Parameter \"%s\"\'s argument is '
                                       'either not a valid Python literal or '
                                       'is unspecified.' % param.name)))
            except:
                print("Unexpected error:", sys.exc_info()[0])
                raise
            
        return params
    
    def run(self):
        self.root.title('GARG: GUI-Based Argument Assignment')
        self.root.deiconify()
        self.unpack_params()
        self.root.mainloop()
        
    def on_cancel_button(self):
        self.root.destroy() 

    def on_ok_button(self):
        # TODO: Return bound arguments (or something else)
        sig = self.get_signature()
        print(sig)           
    
    def unpack_params(self):
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
                    
                    # Add Label and Entry for this parameter
                    self.view.add_parameter_entry(group, param)
                    
class View(tk.Frame):
    """Displays a GUI interface for assigning values to function arguments.
    
    """
    def __init__(self, master=None, on_ok=None, on_cancel=None):
        super().__init__(master)
        self._argdict = {}
        
        tk.Grid.rowconfigure(self.master, 0, weight=1)
        tk.Grid.rowconfigure(self.master, 1, weight=1)
        tk.Grid.columnconfigure(self.master, 0, weight=1)
        tk.Grid.columnconfigure(self.master, 1, weight=1)
        
        self._vsb    = tk.Scrollbar(self.master, orient='vertical')
        self._canvas = tk.Canvas(
            self.master,
            bg='red',
            width=400,
            height=300)
        self._buttonFrame = self.ButtonFrame(self.master,on_ok,on_cancel)
        
        # _groupFrame is a single frame that is drawn onto the canvas.
        # It contains multiple LabelFrames that are vertically stacked.
        self._groupFrame  = tk.Frame(self._canvas, bg='green')

        self._canvas.create_window(
            (0, 0),
            window=self._groupFrame,
            anchor='nw',
            tags=('frame'))
        self._canvas.configure(yscrollcommand=self._vsb.set)
        self._canvas.bind('<Configure>', self._on_canvas_resize)
        self._vsb.config(command=self._canvas.yview)
        
        self._canvas.grid(row=0, column=0, sticky=tk.N+tk.S+tk.E+tk.W)
        self._vsb.grid(row=0, column=1, sticky=tk.N+tk.S)
        self._buttonFrame.grid(row=1, columnspan=2)

    def _on_canvas_resize(self, event=None):
        width  = self._canvas.winfo_width()
        height = self._canvas.winfo_height()
        self._canvas.itemconfigure('frame', width=width, height=height)
        self._canvas.config(scrollregion=self._canvas.bbox('all'))
    
    def add_parameter_group(self, **kwargs):
        lf = tk.LabelFrame(self._groupFrame, **kwargs)
        lf.pack(fill=tk.BOTH)
        
        return lf
        
    def add_parameter_entry(self, master, param):
        lb = tk.Label(master, text=param.name)
        lb.grid(column=0)
        
        box = tk.Entry(master)
        box.grid(column=1)
        if param.default is not param.empty:
            # __repr__() ensures a Python literal is printed
            box.insert(0,param.default.__repr__()) 

        # Keep a reference to get content of box later
        self._argdict[param.name] = box

    def get_params_dict(self):
        """Retrive dictionary containing arguments names as
           keys and argument values as values

        """
        return {name : entry.get() for name, entry in self._argdict.items()}
        
    class ButtonFrame(tk.Frame):
        """Contains the OK and Cancel buttons.
        
        """
        def __init__(self, master=None,on_ok=None,on_cancel=None):
            super().__init__(master)
            
            ok_button     = tk.Button(master=self, text='OK'    ,command=on_ok)
            cancel_button = tk.Button(master=self, text='Cancel',command=on_cancel)
            
            ok_button.pack(side=tk.LEFT)
            cancel_button.pack(side=tk.RIGHT)
        
if __name__ == '__main__':
    def test(a, b, *, c, d=10, e='hello', f=[1, 2, 'hello', {'a': 2}]):
        pass
    
    c = Controller(test)
    c.run()