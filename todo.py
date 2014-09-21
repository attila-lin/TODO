#
# Copyright (c) 2014, Yiyu Lin <linyiyu1992 at gmail dot com>
# All rights reserved.
#

import datetime
from Tkinter import *
import tkMessageBox
import tkFileDialog

DATE_FORMAT = '%d/%m/%Y'
TODAY = datetime.datetime.today()

# Used for displaying an item in the GUI
DISPLAY_FORMAT = "{0:<30}{1}"

# Used for encoding items to be saved to a file
SAVE_FORMAT = "{0},{1}\n"


def as_datetime(date_string):
    """Convert a date string in 'dd/mm/yyyy' format into a datetime object.

    as_datetime(str) -> datetime

    Returns None if date_string is invalid.
    """
    try:
        return datetime.datetime.strptime(date_string, DATE_FORMAT)
    except ValueError as e:
        return None


def as_date_string(date):
    """Convert a datetime object into a date string in 'dd/mm/yyyy' format.

    as_datetime(datetime) -> str
    """
    return date.strftime(DATE_FORMAT)


class ToDoError(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)

class ToDoItem():
  """
  docstring for ToDoItem
  """
  def __init__(self, name, date):
    self.name = name
    self.date = as_datetime(date)
    if self.date == None:
      raise ToDoError(date)

  def get_name(self):
    return self.name

  def get_date(self):
    return as_date_string(self.date)

  def is_overdue(self):
    now = datetime.datetime.today()
    if self.date < now:
      return True
    else:
      return False

  def __str__(self):
    return '{}    {}'.format(self.name, as_date_string(self.date))

  def save_string(self):
    return ','.join([self.name, as_date_string(self.date)])+ '\n'

  def __repr__(self):
    return 'ToDoItem(' + ', '.join([self.name, as_date_string(self.date)]) + ')'

  def __lt__(self, other):
    return self.date < other.date


class ToDoList():
  """
  docstring for ToDoList
  """
  def __init__(self):
    self.todos = []
    self.ns = False

  def needs_saving(self):
    return self.ns

  def load_file(self, filename):
    f = open(filename, 'rU')
    self.todos = []
    for line in f:
      name, date = line.strip().split(',', 1)
      # print name
      self.todos.append(ToDoItem(name, date))
    f.close()
    self.todos = sorted(self.todos)
    self.ns = False

  def save_file(self, filename):
    self.todos = sorted(self.todos)
    f = open(filename, 'w')
    for t in self.todos:
      f.write(t.save_string())
    f.close()
    self.ns = False

  def get_all(self):
    return self.todos

  def get_todo(self, index):
    return self.todos[index]

  def remove_todo(self, index):
    self.todos.pop(index)
    self.ns = True

  def set_todo(self, index, item):
    if index == None:
      self.todos.append(item)
    else:
      self.todos[index] = item
    self.todos = sorted(self.todos)
    self.ns = True

  def __repr__(self):
    retstr = []
    for t in self.todos:
      retstr.append( 'ToDoItem(' + ','.join([t.get_name(), t.get_date()]) + ')' )
    return  ', '.join(retstr)



class Controller(Frame):
  def __init__(self, master=None):
    self.todolist = ToDoList()

    Frame.__init__(self, master, relief=SUNKEN, bd=2, width=600, height=400)
    self.pack()
    self.pack_propagate(0)

    # close
    self.master = master
    master.protocol("WM_DELETE_WINDOW", self.handler)

    self.menubar = Menu(self)

    self.file_opt = options = {}
    options['defaultextension'] = '.txt'
    options['filetypes'] = [('all files', '.*'), ('text files', '.txt')]

    # menu
    menu = Menu(self.menubar, tearoff=0)
    self.menubar.add_cascade(label="File", menu=menu)
    menu.add_command(label="Open To Do File", command=self.askopenfile)
    menu.add_command(label="Save To Do File", command=self.asksavefile)
    menu.add_command(label="Exit", command=self.exit)

    # todolist
    # self.lb = Listbox(self, height=200)
    self.lb = Listbox(self)
    # self.lb.grid(row=0, column=0, columnspan = 3, rowspan = 3, sticky = W+E+N+S)
    for item in self.todolist.get_all():
      string = str(item)
      self.lb.insert(END, string)
    self.lb.pack(side="top",fill="both",expand=False)
    self.lb.pack_propagate(0)

    # buttons
    self.addtodo = Button(self,text="Add To Do", command=self.add_cb)
    self.edittodo = Button(self,text="Edit To Do", command=self.edit_cb)
    self.removetodo = Button(self, text="Remove To Do", command=self.rm_cb)
    self.addtodo.place(x=150,y=360)
    # self.addtodo.pack()
    # self.addtodo.pack(side="left")

    self.edittodo.place(x=250,y=360)
    # self.edittodo.pack()
    # self.edittodo.pack(side= "left")

    self.removetodo.place(x=350,y=360)
    # self.removetodo.pack()
    # self.removetodo.pack(side="left")

    # self.addtodo.grid(row=1,column=0, sticky = W)
    # self.addtodo.pack()

    # self.edittodo.grid(row=1,column=1, sticky = W)
    # self.edittodo.pack()

    # self.removetodo.grid(row=1,column=2, sticky = W)
    # self.removetodo.pack()


    try:
      self.master.config(menu=self.menubar)
    except AttributeError:
      # master is a toplevel window (Python 1.4/Tkinter 1.63)
      self.master.tk.call(master, "config", "-menu", self.menubar)

  def handler(self):
    if self.todolist.needs_saving() == True:
      if tkMessageBox.askyesno(title='Save Changes', message='Unsaved changes. Save?'):
        self.todolist.save_file(self.filename)
        self.quit()
    else:
      self.quit()

  def askopenfile(self):
    """Returns an opened file in read mode."""
    # if need save
    if self.todolist.needs_saving() == True:
      if tkMessageBox.askyesno(title='Save Changes', message='Unsaved changes. Save?'):
        self.todolist.save_file(self.filename)

    filename = tkFileDialog.askopenfilename(**self.file_opt)
    if filename:
      # clear all
      self.lb.delete(0, END)

      try:
        self.todolist.load_file(filename)
      except ToDoError:
        tkMessageBox.showinfo("File Error", "Invalid file format.")
        return
      self.filename = filename


      pos = 0
      for item in self.todolist.get_all():
        string = str(item)
        self.lb.insert(END, string)
        if item.is_overdue(): # pass
          self.lb.itemconfig(pos, fg='red')
        else:
          self.lb.itemconfig(pos, fg='blue')
        pos += 1

  def asksavefile(self):
    self.todolist.save_file(self.filename)

  def exit(self):
    self.quit()

  def add_cb(self):
    self.todoentry = Toplevel()
    self.todoentry.title("Todo Entry")
    namelabel = Label(self.todoentry, text="Name:")
    # namelabel.pack(side="left")
    namelabel.place(x=20, y=20)
    self.namearea = Text(self.todoentry, height=1, width=15)
    # namearea.pack()
    self.namearea.place(x=70, y=20)

    datelabel = Label(self.todoentry, text="Date:")
    # datelabel.pack(side="left")
    datelabel.place(x=20, y=50)
    self.datearea = Text(self.todoentry, height=1, width=15)
    # datearea.pack()
    self.datearea.place(x=70, y=50)

    cancelbutton = Button(self.todoentry, text="Cancel",  command=self.cancel)
    # cancelbutton.pack()
    cancelbutton.place(x=30, y=80)

    okbutton = Button(self.todoentry, text="OK",  command=self.ok)
    # okbutton.pack()
    okbutton.place(x=120, y=80)

  def cancel(self):
    self.todoentry.destroy()

  def ok(self):
    name = self.namearea.get("1.0",END)
    date = self.datearea.get("1.0",END)
    # print name
    # print date
    try:
      item = ToDoItem(name[:-1],date[:-1])
    except ToDoError:
      tkMessageBox.showinfo("File Error", "Invalid file format.")
      return

    self.todolist.set_todo(None, item)
    self.reflash()
    self.todoentry.destroy()

  def reflash(self):
    self.lb.delete(0, END)
    pos = 0
    for item in self.todolist.get_all():
      string = str(item)
      self.lb.insert(END, string)
      if item.is_overdue(): # pass
        self.lb.itemconfig(pos, fg='red')
      else:
        self.lb.itemconfig(pos, fg='blue')
      pos += 1


  def edit_cb(self):
    items = self.lb.curselection()
    if len(items) == 0:
      tkMessageBox.showinfo("Selection Error", "No item selected")

    self.index = int(items[0])
    todoitem = self.todolist.get_todo(self.index)
    # print todoitem
    self.todoentry = Toplevel()
    self.todoentry.title("Todo Entry")
    namelabel = Label(self.todoentry, text="Name:")
    # namelabel.pack(side="left")
    namelabel.place(x=20, y=20)
    self.namearea = Text(self.todoentry, height=1, width=15)
    self.namearea.insert(INSERT, todoitem.get_name())
    # namearea.pack()
    self.namearea.place(x=70, y=20)

    datelabel = Label(self.todoentry, text="Date:")
    # datelabel.pack(side="left")
    datelabel.place(x=20, y=50)
    self.datearea = Text(self.todoentry, height=1, width=15)
    self.datearea.insert(INSERT, todoitem.get_date())
    # datearea.pack()
    self.datearea.place(x=70, y=50)

    cancelbutton = Button(self.todoentry, text="Cancel",  command=self.cancel)
    # cancelbutton.pack()
    cancelbutton.place(x=30, y=80)

    okbutton = Button(self.todoentry, text="OK",  command=self.editok)
    # okbutton.pack()
    okbutton.place(x=120, y=80)

  def editok(self):
    name = self.namearea.get("1.0",END)
    date = self.datearea.get("1.0",END)
    try:
      item = ToDoItem(name[:-1],date[:-1])
    except ToDoError:
      tkMessageBox.showinfo("File Error", "Invalid file format.")
      return

    self.todolist.set_todo(self.index, item)
    self.reflash()
    self.todoentry.destroy()

  def rm_cb(self):
    items = self.lb.curselection()
    if len(items) == 0:
      tkMessageBox.showinfo("Selection Error", "No item selected")
    pos = 0
    for i in items :
      idx = int(i) - pos
      self.todolist.remove_todo(idx)
      self.lb.delete(idx,idx)
      pos = pos + 1




class ToDoApp(object):
    def __init__(self, master=None):
        master.title("TODOs")
        self.controller = Controller(master)


def main():
    root = Tk()
    app = ToDoApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
