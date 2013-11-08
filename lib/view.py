

def draw_mainwin(win, app):
		v = win.getProperty('browseview')
		inst = app.get_var('view_matrix')[v]
		app.set_var(list, inst.data)
		win.make_visible(300, 50)
		inst.make_active()
		win.setFocusId(50)
		if inst.pos:
			win.setCurrentListPosition(inst.pos)
