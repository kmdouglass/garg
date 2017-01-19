"""GUI-based function argument assignment in Python.

Author  : Kyle M. Douglass
E-mail  : kyle.m.douglass@gmail.com
Year    : 2017
License : MIT

"""

import tkinter as tk
import inspect

class Controller():
    """Reads function arguments and assigns values via the GUI interface.
    
    Parameters
    ----------
    func : function
        The function for which the parameter signature will be extracted.
        
    Attributes
    ----------
    model : Signature
        The input function's call signature. This is a Signature object from
        the standard library's inspect module and serves as the Model in the
        Model-View-Controller pattern.
    
    """
    _ARG_TYPES = (
        inspect.Parameter.POSITIONAL_ONLY,
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
        inspect.Parameter.VAR_POSITIONAL,
        inspect.Parameter.KEYWORD_ONLY,
        inspect.Parameter.VAR_KEYWORD
    )
    
    def __init__(self, func):
        self.root = tk.Tk()
        
        self.model = inspect.signature(func)
        self.view  = View(self.root,self.on_ok_button,self.on_cancel_button)
    
    def run(self):
        self.root.title('GARG: GUI-Based Argument Assignment')
        self.root.deiconify()
        self.unpack_params()
        self.root.mainloop()

    def on_ok_button(self):
        sig = self.get_signature()
        print(sig)

    def on_cancel_button(self):
        self.root.destroy()

    def get_signature(self):
        """Retrieve an instance of signature with the values of the arguments
           filled in
           
        """
        # TODO: Implement conversion of arguments here
        # just return the dict for now
        return self.view.get_params_dict()
    
    def unpack_params(self):
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
        
        # http://wenda.mojijs.com/Home/question/detail/id/7441544/p/1/index.html
        
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
            box.insert(0,param.default)

        # Keep a reference to get content of box later
        self._argdict[param.name] = box

    def get_params_dict(self):
        """Retrive dictionary containing arguments names as
           keys and argument values as values

        """
        return {name : entry.get() for name,entry in self._argdict.items()}
        
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
    def test(a, b, *, c, d=10):
        pass
    
    c = Controller(test)
    c.run()
