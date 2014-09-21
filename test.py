
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
    return ', '.join([self.name, as_date_string(self.date)])+ '\n'

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
    self.needs_saving = False

  def needs_saving(self):
    pass
    # if :
    #   return True
    # else:
    #   return False

  def load_file(self, filename):
    f = open(filename, 'rU')
    for line in f:
      name, date = line.strip().split(',', 1)
      self.todos.append(ToDoItem(name, date))
    f.close()

  def save_file(self, filename):
    f = open(filename, 'w')
    for t in self.todos:
      f.write(t.save_string())
    f.close()
    sorted(self.todos)

  def get_all(self):
    return self.todos

  def get_todo(self, index):
    return self.todos[index]

  def remove_todo(self, index):
    self.todos.pop(index)

  def set_todo(self, index, item):
    if index == None:
      self.todos.append(item)
    else:
      self.todos[index] = item
    sorted(self.todos)

  def __repr__(self):
    retstr = []
    for t in self.todos:
      retstr.append( 'ToDoItem(' + ','.join([t.get_name(), t.get_date()]) + ')' )
    return  ', '.join(retstr)
