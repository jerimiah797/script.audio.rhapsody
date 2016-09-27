import xbmcgui
import xbmc
import xbmcvfs

from base import WinBase, DialogBase


class InputDialog(DialogBase):

    #def __init__(self, xmlFilename, scriptPath, defaultSkin, defaultRes):
    def __init__(self, *args, **kwargs):
        DialogBase.__init__(self, *args)
        self.app = kwargs.get('app')
        self.name = xbmcgui.ControlEdit(530, 320, 400, 120, '', 'rhapsody_font16', '0xDD171717', focusTexture="none.png")
        self.pswd = xbmcgui.ControlEdit(530, 320, 400, 120, '', font='rhapsody_font16', textColor='0xDD171717', focusTexture="none.png", isPassword=1)
        self.butn = None
        self.name_txt = ""
        self.pswd_txt = ""

    def onInit(self):
        self.name_select = self.getControl(10)
        self.pswd_select = self.getControl(11)
        self.pswd_select.setVisible(False)
        self.addControl(self.name)
        self.addControl(self.pswd)
        self.butn = self.getControl(22)
        self.name.setPosition(600, 320)
        self.name.setWidth(400)
        self.name.controlDown(self.pswd)
        self.pswd.setPosition(600, 410)
        self.pswd.setWidth(400)
        self.pswd.controlUp(self.name)
        self.pswd.controlDown(self.butn)
        self.butn.controlUp(self.pswd)
        self.setFocus(self.name)





class LoginWin(WinBase):
    def __init__(self, *args, **kwargs):
        WinBase.__init__(self, *args)
        self.app = kwargs.get('app')
        self.mem = self.app.mem

    def onInit(self):
        #print "Starting login UI loop"
        while not self.app.get_var('logged_in'):
            if self.app.get_var('bad_creds'):
                self.getControl(10).setLabel('Login failed! Try again...')
            #print "Set fail label message"
            self.inputwin = InputDialog("input.xml", self.app.__addon_path__, 'Default', '720p', app=self.app)
            self.inputwin.doModal()
            if not self.app.get_var('exiting'):
                data = self.mem.login_member(self.inputwin.name_txt, self.inputwin.pswd_txt)
                self.app.set_var('logged_in', data['logged_in'])
                self.app.set_var('bad_creds', data['bad_creds'])
                del self.inputwin
            else:
                break

        #print "Exited the login UI loop! Calling the del function"
        self.close()