import Tkinter as tk
import tkFileDialog
import tkFont
import ScrolledText
import pimote as pm
import subprocess


master = tk.Tk()
master.wm_title("PiMote Program Generator")
default_head = "# An auto-generated PiMote program made by PiMote Program Generator. Tom Richardson 2013\n\n"
default_head += "from pimote import *\n\nclass MyPhone(Phone):\n\t#########----------------------------------------------###########\n\t"
default_head += "# Your code will go here! Check for the ID of the button pressed #\n\t# and handle that button press as you wish.                      #\n\t"
default_head += "#########----------------------------------------------###########\n\tdef buttonPressed(self, id, message, phoneId):\n"

notice = "This program is still a very early build. No validation has been added to the fields, so be careful with input!"


class VerticalScrolledFrame(tk.Frame):
    """A pure Tkinter scrollable frame that actually works!

    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling
    
    """
    def __init__(self, parent, *args, **kw):
        tk.Frame.__init__(self, parent, *args, **kw)            

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)
        canvas = tk.Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=vscrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
        vscrollbar.config(command=canvas.yview)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = tk.Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=tk.NW)

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)

        return

def nameExists(name):
	for c in components:
		if c[1] == name:
			return True
	return False

def add_new_button():
	name = "button_"
	num=1
	while nameExists(name+str(num)):
		num+=1
	name = name+str(num)
	components.append([0, name, "Button"])
	refresh_layout()
def add_new_toggle():
	name = "toggle_"
	num=1
	while nameExists(name+str(num)):
		num+=1
	name = name+str(num)
	components.append([1, name, "Toggle button", False])
	refresh_layout()
def add_new_input():
	name = "input_"
	num=1
	while nameExists(name+str(num)):
		num+=1
	name = name+str(num)
	components.append([2, name, "Input Text"])
	refresh_layout()
def add_new_voice():
	name = "voice_"
	num=1
	while nameExists(name+str(num)):
		num+=1
	name = name+str(num)
	components.append([3, name])
	refresh_layout()
def add_new_recurring():
	name = "recurring_"
	num=1
	while nameExists(name+str(num)):
		num+=1
	name = name+str(num)
	components.append([4, name, 1000])
	refresh_layout()
def add_new_output():
	name = "output_"
	num=1
	while nameExists(name+str(num)):
		num+=1
	name = name+str(num)
	components.append([5, name, "Output Field"])
	refresh_layout()
def add_new_progress():
	name = "progress_"
	num=1
	while nameExists(name+str(num)):
		num+=1
	name = name+str(num)
	components.append([6, name, 100])
	refresh_layout()
def add_new_video():
	name = "video_"
	num=1
	while nameExists(name+str(num)):
		num+=1
	name = name+str(num)
	components.append([7, name])
	refresh_layout()
def add_new_spacer():
	name = "spacer_"
	num=1
	while nameExists(name+str(num)):
		num+=1
	name = name+str(num)
	components.append([8, name, 50])
	refresh_layout()

def refresh_layout():
	global inner_frame
	global layout_frame
	height = inner_frame.winfo_height()
	try:
		inner_frame.destroy()
	except Exception, e:
		print("Problem when destroying, " + str(e))

	inner_frame = tk.Frame(master=layout_frame.interior, height=height)
	
	row = 0
	for c in components:
		comp_frame = tk.Frame(master=inner_frame, bd=1, relief="groove", pady=2, padx=2)
		font = tkFont.Font(size=8)
		comp_button = tk.Button(master=comp_frame, text=c[1], command= lambda c=c: show_properties(c))
		comp_button.grid(row=0, column=0, sticky=tk.W+tk.E)
		control_frame = tk.Frame(master=comp_frame)
		control_frame.grid(row=0, column=1)
		up_button = tk.Button(master=control_frame, text="^", font=font, height=1, command = lambda row=row: move_up(row))
		up_button.grid(row=0, column=0)
		if row == 0:
			up_button.config(state="disabled")
		down_button=tk.Button(master=control_frame, text="v", height=1, font=font, command = lambda row=row: move_down(row))
		down_button.grid(row=1, column=0)
		if row == len(components)-1:
			down_button.config(state="disabled")
		tk.Grid.columnconfigure(comp_frame,0, weight=2)
		comp_frame.pack(fill="x")
		row += 1

	inner_frame.pack(fill="both")

def move_up(row):
	a, b = components[row], components[row-1]
	components[row], components[row-1] = b, a
	refresh_layout()

def move_down(row):
	a, b = components[row], components[row+1]
	components[row], components[row+1] = b, a
	refresh_layout()

def show_properties(comp):
	global properties_frame
	global properties_inner
	
	try:
		properties_inner.destroy()
	except:
		pass
	properties_inner = tk.Frame(master=properties_frame)
	properties_inner.grid(row=0, column=0, rowspan=9, sticky=tk.N+tk.S+tk.W+tk.E)

	if comp[0] == 0:
		variable_name_label = tk.Label(master=properties_inner, text="Variable name: "+comp[1], anchor=tk.W, height=2).grid(row=0, column=0, columnspan=2, sticky=tk.N+tk.S+tk.E+tk.W)
		name_label = tk.Label(master=properties_inner, text="Name: ").grid(row=1, column=0)
		name_entry = tk.Entry(master=properties_inner)
		name_entry.grid(row=1, column=1)
		name_entry.insert(0, comp[2])
		save_button = tk.Button(master=properties_inner, text="Save", command=lambda:save_component(comp=comp, value=name_entry.get()))
		save_button.grid(row=2, column = 1)
		delete_button = tk.Button(master=properties_inner, text="Delete", command=lambda:delete_component(comp=comp)).grid(row=2, column=0)
	elif comp[0] == 1:
		variable_name_label = tk.Label(master=properties_inner, text="Variable name: "+comp[1], anchor=tk.W, height=2).grid(row=0, column=0, columnspan=2, sticky=tk.N+tk.S+tk.E+tk.W)
		name_label = tk.Label(master=properties_inner, text="Name: ").grid(row=1, column=0)
		name_entry = tk.Entry(master=properties_inner)
		name_entry.grid(row=1, column=1)
		name_entry.insert(0, comp[2])
		selected = tk.BooleanVar()
		selected_box = tk.Checkbutton(master=properties_inner, text="Initial Value", variable=selected, onvalue=True, offvalue=False)
		selected.set(comp[3])
		selected_box.grid(row=2, column=1)
		save_button = tk.Button(master=properties_inner, text="Save", command=lambda:save_component(comp=comp, value=name_entry.get(), initial_value=selected.get()))
		save_button.grid(row=3, column = 1)
		delete_button = tk.Button(master=properties_inner, text="Delete", command=lambda:delete_component(comp=comp)).grid(row=3, column=0)
	elif comp[0] == 2:
		variable_name_label = tk.Label(master=properties_inner, text="Variable name: "+comp[1], anchor=tk.W, height=2).grid(row=0, column=0, columnspan=2, sticky=tk.N+tk.S+tk.E+tk.W)
		name_label = tk.Label(master=properties_inner, text="Name: ").grid(row=1, column=0)
		name_entry = tk.Entry(master=properties_inner)
		name_entry.grid(row=1, column=1)
		name_entry.insert(0, comp[2])
		save_button = tk.Button(master=properties_inner, text="Save", command=lambda:save_component(comp=comp, value=name_entry.get()))
		save_button.grid(row=2, column = 1)
		delete_button = tk.Button(master=properties_inner, text="Delete", command=lambda:delete_component(comp=comp)).grid(row=2, column=0)
	elif comp[0] == 3:
		variable_name_label = tk.Label(master=properties_inner, text="Variable name: "+comp[1], anchor=tk.W, height=2).grid(row=0, column=0, columnspan=2, sticky=tk.N+tk.S+tk.E+tk.W)
		name_label = tk.Label(master=properties_inner, text="No properties for Voice Input").grid(row=1, column=0)
		delete_button = tk.Button(master=properties_inner, text="Delete", command=lambda:delete_component(comp=comp)).grid(row=2, column=0)
	elif comp[0] == 4:
		variable_name_label = tk.Label(master=properties_inner, text="Variable name: "+comp[1], anchor=tk.W, height=2).grid(row=0, column=0, columnspan=2, sticky=tk.N+tk.S+tk.E+tk.W)
		name_label = tk.Label(master=properties_inner, text="Time Period: ").grid(row=1, column=0)
		name_entry = tk.Entry(master=properties_inner)
		name_entry.grid(row=1, column=1)
		name_entry.insert(0, comp[2])
		save_button = tk.Button(master=properties_inner, text="Save", command=lambda:save_component(comp=comp, value=int(name_entry.get())))
		save_button.grid(row=2, column = 1)
		delete_button = tk.Button(master=properties_inner, text="Delete", command=lambda:delete_component(comp=comp)).grid(row=2, column=0)
	elif comp[0] == 5:
		variable_name_label = tk.Label(master=properties_inner, text="Variable name: "+comp[1], anchor=tk.W, height=2).grid(row=0, column=0, columnspan=2, sticky=tk.N+tk.S+tk.E+tk.W)
		name_label = tk.Label(master=properties_inner, text="Text: ").grid(row=1, column=0)
		name_entry = ScrolledText.ScrolledText(master=properties_inner, height=8, width=30, bd=2, relief="sunken")
		name_entry.grid(row=1, column=1)
		name_entry.insert(tk.END, comp[2])
		save_button = tk.Button(master=properties_inner, text="Save", command=lambda:save_component(comp=comp, value=name_entry.get(1.0, tk.END)[:-1].replace("\n", "<br>")))
		save_button.grid(row=2, column = 1)
		delete_button = tk.Button(master=properties_inner, text="Delete", command=lambda:delete_component(comp=comp)).grid(row=2, column=0)
	elif comp[0] == 6:
		variable_name_label = tk.Label(master=properties_inner, text="Variable name: "+comp[1], anchor=tk.W, height=2).grid(row=0, column=0, columnspan=2, sticky=tk.N+tk.S+tk.E+tk.W)
		name_label = tk.Label(master=properties_inner, text="Max Value: ").grid(row=1, column=0)
		name_entry = tk.Entry(master=properties_inner)
		name_entry.grid(row=1, column=1)
		name_entry.insert(0, comp[2])
		save_button = tk.Button(master=properties_inner, text="Save", command=lambda:save_component(comp=comp, value=int(name_entry.get())))
		save_button.grid(row=2, column = 1)
		delete_button = tk.Button(master=properties_inner, text="Delete", command=lambda:delete_component(comp=comp)).grid(row=2, column=0)
	elif comp[0] == 7:
		variable_name_label = tk.Label(master=properties_inner, text="Variable name: "+comp[1], anchor=tk.W, height=2).grid(row=0, column=0, columnspan=2, sticky=tk.N+tk.S+tk.E+tk.W)
		name_label = tk.Label(master=properties_inner, text="No properties for Video Feed").grid(row=1, column=0)
		delete_button = tk.Button(master=properties_inner, text="Delete", command=lambda:delete_component(comp=comp)).grid(row=2, column=0)
	elif comp[0] == 8:
		variable_name_label = tk.Label(master=properties_inner, text="Variable name: "+comp[1], anchor=tk.W, height=2).grid(row=0, column=0, columnspan=2, sticky=tk.N+tk.S+tk.E+tk.W)
		name_label = tk.Label(master=properties_inner, text="Height: ").grid(row=1, column=0)
		name_entry = tk.Entry(master=properties_inner)
		name_entry.grid(row=1, column=1)
		name_entry.insert(0, comp[2])
		save_button = tk.Button(master=properties_inner, text="Save", command=lambda:save_component(comp=comp, value=int(name_entry.get())))
		save_button.grid(row=2, column = 1)
		delete_button = tk.Button(master=properties_inner, text="Delete", command=lambda:delete_component(comp=comp)).grid(row=2, column=0)

def save_component(comp = None, value="", initial_value=None):
	global info_label
	if comp[0] == 0 or comp[0] == 2 or comp[0] == 4 or comp[0] == 5 or comp[0] == 6 or comp[0] == 8:
		comp[2] = value
		info_label.config(text="Saved '" + comp[1] + "' {Value: " + str(comp[2])+"}")
	elif comp[0] == 1:
		comp[2] = value
		if initial_value == 1:
			comp[3] = True
		else:
			comp[3] = False
		info_label.config(text="Saved '" + comp[1] + "' {Value: " + str(comp[2])+", Initial Value: "+str(comp[3])+"}")
def delete_component(comp = None):
	global info_label
	global properties_inner
	global properties_frame
	info_label.config(text="Deleted '" + comp[1]+"'")
	components.remove(comp)
	refresh_layout()

	try:
		properties_inner.destroy()
	except:
		pass
	properties_inner = tk.Frame(master=properties_frame)
	properties_inner.grid(row=0, column=0, rowspan=9, sticky=tk.N+tk.S+tk.W+tk.E)

def generate_program():
	global info_label
	global password_value
	global password_entry
	global max_value
	global max_entry

	if len(components) == 0:
		info_label.config(text="You have not populated the phone with components")
		return

	fileName = tkFileDialog.asksaveasfilename(parent=master, defaultextension=[".py"], filetypes=[("Python File", ".py")], title="Generate to..")
	my_program = open(fileName, "w+")
	my_program.write(default_head)
	for c in components:
		if c[0] == 0 or c[0] == 1 or c[0] == 2 or c[0] == 3 or c[0] == 4:
			my_program.write("\t\tif id == " + c[1] + ".getId():\n\t\t\tpass\n")
	my_program.write("\nphone = MyPhone()   # The phone object\n\n")
	for c in components:
		if c[0] == 0:
			my_program.write(c[1] + " = Button('"+c[2]+"')\nphone.add("+c[1]+")\n")
		elif c[0] == 1:
			my_program.write(c[1] + " = ToggleButton('"+c[2]+"', "+str(c[3])+")\nphone.add("+c[1]+")\n\n")
		elif c[0] == 2:
			my_program.write(c[1] + " = InputText('"+c[2]+"')\nphone.add("+c[1]+")\n\n")
		elif c[0] == 3:
			my_program.write(c[1] + " = VoiceInput()\nphone.add("+c[1]+")\n\n")
		elif c[0] == 4:
			my_program.write(c[1] + " = RecurringInfo("+str(c[2])+")\nphone.add("+c[1]+")\n\n")
		elif c[0] == 5:
			my_program.write(c[1] + " = OutputText('"+c[2]+"')\nphone.add("+c[1]+")\n\n")
		elif c[0] == 6:
			my_program.write(c[1] + " = ProgressBar("+str(c[2])+")\nphone.add("+c[1]+")\n\n")
		elif c[0] == 7:
			my_program.write(c[1] + " = VideoFeed()\nphone.add("+c[1]+")\n\n")
		elif c[0] == 8:
			my_program.write(c[1] + " = Spacer("+str(c[2])+")\nphone.add("+c[1]+")\n\n")

	if max_value.get():
		my_program.write("server.setMaxClients("+str(max_entry.get())+")\n")
	if password_value.get():
		my_program.write("server.setPassword('"+str(password_entry.get())+"')\n")
	my_program.write("server = PhoneServer()\nserver.addPhone(phone)\nserver.start('0.0.0.0', 8090)")
	proc = subprocess.Popen('pwd', stdout=subprocess.PIPE)
	generate_text = "Generated program, saved as '"+fileName+"'.\nTo run, 'cd' into that directory and type 'python myprogram.py' into a terminal.\n"
	generate_text += "Make sure you add your code to the 'buttonPressed()' method to handle when a button is pressed!"
	info_label.config(text=generate_text)
	my_program.close()

def toggle_password(value):
	global password_entry
	if not value:
		password_entry.config(state="disabled")
	else:
		password_entry.config(state="normal")

def toggle_max_clients(value):
	global max_entry
	if not value:
		max_entry.config(state="disabled")
	else:
		max_entry.config(state="normal")

def save_program():
	global components
	global password_value
	global password_entry
	global max_value
	global max_entry
	fileName = tkFileDialog.asksaveasfilename(parent=master, defaultextension=[".pmg"], filetypes=[("PiMote File", ".pmg")], title="Save the program as...")
	if len(fileName ) > 0:
		file = open(fileName, "w")
		file.write(str(password_value.get())+","+password_entry.get()+",\n")
		file.write(str(max_value.get())+","+max_entry.get()+",\n")
		for c in components:
			for inf in c:
				file.write(str(inf)+",")
			file.write("\n")
		file.close()

def open_program():
	global components
	global password_value
	global password_entry
	global max_value
	global max_entry
	fileName = tkFileDialog.askopenfilename(parent=master, filetypes=[("PiMote File", ".pmg")], title="Open file")
	if len(fileName) > 0:
		file = open(fileName, "r")
		components = []
		p = file.readline().split(",")
		
		if int(p[0]) == 1:
			password_value.set(True)
			toggle_password(password_value.get())
			password_entry.delete(0, tk.END)
			password_entry.insert(0, p[1])
		else:
			password_value.set(False)
			toggle_password(password_value.get())

		m = file.readline().split(",")
		print(m)
		if int(m[0]) == 1:
			max_value.set(True)
			toggle_max_clients(max_value.get())
			max_entry.delete(0, tk.END)
			max_entry.insert(0, m[1])
		else:
			max_value.set(False)
			toggle_max_clients(max_value.get())
		
		c = file.readline().split(",")
		c.remove(c[len(c)-1])
		while len(c)!=0:
			fix_component(c)
			components.append(c)
			c = file.readline().split(",")
			c.remove(c[len(c)-1])
		file.close()

	for i in components:
		print(i)
	print("Refreshing")
	refresh_layout()

def fix_component(c):
	c[0] = int(c[0])
	if c[0] == 4 or c[0] == 6 or c[0] == 8:
		c[2] = int(c[2])
	elif c[0] == 1:
		if c[3] == "True":
			c[3] = True
		else:
			c[3] = False


	

components = []

menubar = tk.Menu(master)
filemenu = tk.Menu(menubar, tearoff=0)
filemenu.add_command(label="Open", command=open_program)
filemenu.add_command(label="Save as", command=save_program)
filemenu.add_command(label="Quit", command=master.quit)
menubar.add_cascade(label="File", menu=filemenu)

main_frame = tk.Frame(master)
main_frame.grid(row=0, column=0)
space5 = tk.Label(master, height=4).grid(row=1, column=0)
info_label = tk.Label(master, text=notice, anchor=tk.NW, height=5, justify=tk.LEFT, padx=8)
info_label.grid(row=2, column=0, sticky=tk.E+tk.W+tk.N+tk.S)

buttons_label = tk.Label(master=main_frame, text="Add Components", height=3).grid(row=0, column=0)
button_frame = tk.Frame(master=main_frame)
button_frame.grid(row=1, column=0, rowspan=9, sticky=tk.W+tk.E+tk.N+tk.S)
add_button = tk.Button(master=button_frame, text="Add Button", command=add_new_button)
add_button.grid(row=1, column=0, sticky=tk.W+tk.E+tk.N+tk.S)
add_toggle = tk.Button(master=button_frame, text="Add Toggle Button", command=add_new_toggle)
add_toggle.grid(row=2, column=0, sticky=tk.W+tk.E+tk.N+tk.S)
add_input = tk.Button(master=button_frame, text="Add Text Input", command=add_new_input)
add_input.grid(row=3, column=0, sticky=tk.W+tk.E+tk.N+tk.S)
add_voice = tk.Button(master=button_frame, text="Add Voice Input", command=add_new_voice)
add_voice.grid(row=4, column=0, sticky=tk.W+tk.E+tk.N+tk.S)
add_recurring = tk.Button(master=button_frame, text="Add poll", command=add_new_recurring)
add_recurring.grid(row=5, column=0, sticky=tk.W+tk.E+tk.N+tk.S)
add_output = tk.Button(master=button_frame, text="Add Output Text", command=add_new_output)
add_output.grid(row=6, column=0, sticky=tk.W+tk.E+tk.N+tk.S)
add_progress = tk.Button(master=button_frame, text="Add Progress Bar", command=add_new_progress)
add_progress.grid(row=7, column=0, sticky=tk.W+tk.E+tk.N+tk.S)
add_video = tk.Button(master=button_frame, text="Add Video Feed", command=add_new_video)
add_video.grid(row=8, column=0, sticky=tk.W+tk.E+tk.N+tk.S)
add_spacer = tk.Button(master=button_frame, text="Add Space", command=add_new_spacer)
add_spacer.grid(row=9, column=0, sticky=tk.W+tk.E+tk.N+tk.S)

space = tk.Label(master=main_frame, width=6).grid(row=0, column=1)

layout_label = tk.Label(master=main_frame, text="Phone Layout", width=25).grid(row=0, column=2)
layout_frame = VerticalScrolledFrame(main_frame, relief="raised", borderwidth=2, padx=5, pady=5)
layout_frame.grid(row=1, column=2, rowspan=10, sticky=tk.N+tk.S+tk.E+tk.W)
inner_frame = tk.Frame(master=layout_frame.interior)
inner_frame.pack(fill="both")
space2 = tk.Label(master=main_frame, width=6, height=3).grid(row=0, column=3)

properties_label = tk.Label(master=main_frame, text="Properties", width=35).grid(row=0, column=4)
properties_frame = tk.Frame(master=main_frame)
properties_frame.grid(row=1, column=4, rowspan=9, sticky=tk.N+tk.S+tk.W+tk.E)
properties_inner = tk.Frame(master=properties_frame)
properties_inner.grid(row=0, column=0, rowspan=9, sticky=tk.N+tk.S+tk.W+tk.E)

space3 = tk.Label(master=main_frame, width=6, height=3).grid(row=0, column=5)

server_frame = tk.Frame(master=main_frame)
server_frame.grid(row=1, column=6, sticky=tk.W+tk.E+tk.N+tk.S, rowspan=9)
server_label = tk.Label(master=main_frame, text="Server Controls", anchor="center").grid(row=0, column=6, columnspan=2)
password_value = tk.BooleanVar()
password_box = tk.Checkbutton(master=server_frame, text="Password ", variable=password_value, onvalue=True, offvalue=False, command=lambda:toggle_password(password_value.get()))
password_box.grid(row=2, column=1, sticky=tk.E)
password_value.set(False)
password_label = tk.Label(master=server_frame, text="Password:").grid(row=3, column=0)
password_entry = tk.Entry(master=server_frame, state="disabled")
password_entry.grid(row=3, column=1)
max_value = tk.BooleanVar()
max_box = tk.Checkbutton(master=server_frame, text="Max Clients ", variable=max_value, onvalue=True, offvalue=False, command=lambda:toggle_max_clients(max_value.get()))
max_box.grid(row=4, column=1, sticky=tk.E)
max_value.set(False)
max_label = tk.Label(master=server_frame, text="Max Clients:").grid(row=5, column=0)
max_entry = tk.Entry(master=server_frame, state="disabled")
max_entry.grid(row=5, column=1)

start_server = tk.Button(master=server_frame, text="Generate Program", command=generate_program)
start_server.grid(row=7, column=1, sticky=tk.N+tk.S+tk.W+tk.E)
# stop_server = tk.Button(master, text="Stop server", state="disabled")
# stop_server.grid(row=2, column=6, sticky=tk.N+tk.S+tk.W+tk.E)

space4 = tk.Label(master=main_frame, width=6, height=3).grid(row=0, column=8)

master.config(menu=menubar)
tk.mainloop()
