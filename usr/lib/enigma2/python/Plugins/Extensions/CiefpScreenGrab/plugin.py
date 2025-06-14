from __future__ import absolute_import
from __future__ import print_function
from enigma import eActionMap, ePicLoad, eTimer
from Components.ActionMap import ActionMap
from Components.ConfigList import ConfigListScreen
from Components.config import config, getConfigListEntry, ConfigSubsection, ConfigSelection, ConfigEnableDisable, ConfigYesNo
from Components.Pixmap import Pixmap
from Components.Console import Console
from Components.Label import Label
from Components.MenuList import MenuList
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Tools.Notifications import AddNotification
from datetime import datetime
from time import time as systime
from os import path, makedirs, remove
import glob

pluginversion = "Version: 1.2"
config.plugins.CiefpScreenGrab = ConfigSubsection()
config.plugins.CiefpScreenGrab.enable = ConfigEnableDisable(default=True)
config.plugins.CiefpScreenGrab.switchhelp = ConfigYesNo(default=True)
config.plugins.CiefpScreenGrab.miniskin = ConfigYesNo(default=False)
config.plugins.CiefpScreenGrab.path = ConfigSelection(default="/media/hdd", choices=[("/media/hdd"), ("/media/usb"), ("/tmp", "/tmp")])
config.plugins.CiefpScreenGrab.pictureformat = ConfigSelection(default="-j", choices=[("-j", "jpg"), ("-p", "png")])
config.plugins.CiefpScreenGrab.jpegquality = ConfigSelection(default="100", choices=[("10"), ("20"), ("40"), ("60"), ("80"), ("100")])
config.plugins.CiefpScreenGrab.picturetype = ConfigSelection(default="all", choices=[("all", "OSD + Video"), ("-v", "Video"), ("-o", "OSD")])
config.plugins.CiefpScreenGrab.picturesize = ConfigSelection(default="default", choices=[("default", _("Skin resolution")), ("-r 720", "720"), ("-r 1280", "1280"), ("-r 1920", "1920")])
config.plugins.CiefpScreenGrab.timeout = ConfigSelection(default="3", choices=[("1", "1 sec"), ("3", "3 sec"), ("5", "5 sec"), ("10", "10 sec"), ("off", _("no message")), ("0", _("no timeout"))])
config.plugins.CiefpScreenGrab.buttonchoice = ConfigSelection(default="-1", choices=[("-1", _("None")), ("113", _("Mute")), ("138", _("Help")), ("358", " Info"), ("362", _("Timer")), ("365", _("EPG")), ("377", _("TV")), ("385", _("Radio")), ("388", _("Text")), ("392", _("Audio")), ("398", _("Red")), ("399", _("Green")), ("400", _("Yellow")), ("401", _("Blue"))])
config.plugins.CiefpScreenGrab.dummy = ConfigSelection(default="1", choices=[("1", " ")])

def getPicturePath():
    picturepath = config.plugins.CiefpScreenGrab.path.value
    if picturepath.endswith('/'):
        picturepath = picturepath + 'CiefpScreenGrab'
    else:
        picturepath = picturepath + '/CiefpScreenGrab'
    try:
        if not path.exists(picturepath):
            makedirs(picturepath)
            print(f"[CiefpScreenGrab] Created directory: {picturepath}")
    except OSError:
        print(f"[CiefpScreenGrab] Failed to create directory: {picturepath}")
        AddNotification(MessageBox, _("Sorry, your device for screenshots is not writeable.\n\nPlease choose another one."), MessageBox.TYPE_ERROR, timeout=10)
    return picturepath

class getScreenshot:
    def __init__(self):
        self.ScreenshotConsole = Console()
        if hasattr(self.ScreenshotConsole, 'binary'):
            self.ScreenshotConsole.binary = True
        self.previousflag = 0
        print("[CiefpScreenGrab] Initializing getScreenshot")
        try:
            eActionMap.getInstance().bindAction('', 0, self.screenshotKey)
            print("[CiefpScreenGrab] eActionMap binding successful")
        except Exception as e:
            print(f"[CiefpScreenGrab] Error binding eActionMap: {str(e)}")

    def screenshotKey(self, key, flag):
        print(f"[CiefpScreenGrab] Key pressed: key={key}, flag={flag}, selected_button={config.plugins.CiefpScreenGrab.buttonchoice.value}, enable={config.plugins.CiefpScreenGrab.enable.value}, switchhelp={config.plugins.CiefpScreenGrab.switchhelp.value}")
        selectedbutton = int(config.plugins.CiefpScreenGrab.buttonchoice.value)
        if selectedbutton == -1 or not config.plugins.CiefpScreenGrab.enable.value:
            return 0
        if key == selectedbutton:
            if not config.plugins.CiefpScreenGrab.switchhelp.value:
                if flag == 3:
                    self.previousflag = flag
                    print("[CiefpScreenGrab] Long press detected, triggering screenshot")
                    self.grabScreenshot()
                    return 1
                if self.previousflag == 3 and flag == 1:
                    self.previousflag = 0
                    print("[CiefpScreenGrab] Long press release detected")
                    return 1
            else:
                if flag == 0:
                    print("[CiefpScreenGrab] Key press started (flag=0), waiting for flag=1")
                    return 1
                if flag == 3:
                    self.previousflag = flag
                    print("[CiefpScreenGrab] Long press started (flag=3), waiting for release")
                    return 0
                if flag == 1 and self.previousflag == 0:
                    print("[CiefpScreenGrab] Short press detected, triggering screenshot")
                    self.grabScreenshot()
                    return 1
                if self.previousflag == 3 and flag == 1:
                    self.previousflag = 0
                    print("[CiefpScreenGrab] Long press release detected, no action")
                    return 0
        return 0

    def grabScreenshot(self, ret=None):
        filename = self.getFilename()
        print("[CiefpScreenGrab] Grab screenshot to %s" % filename)
        cmd = "grab"
        if not config.plugins.CiefpScreenGrab.picturetype.value == "all":
            cmdoptiontype = " " + str(config.plugins.CiefpScreenGrab.picturetype.value)
            cmd += cmdoptiontype
        if not config.plugins.CiefpScreenGrab.picturesize.value == "default":
            cmdoptionsize = " " + str(config.plugins.CiefpScreenGrab.picturesize.value)
            cmd += cmdoptionsize
        cmdoptionformat = " " + str(config.plugins.CiefpScreenGrab.pictureformat.value)
        cmd += cmdoptionformat
        if config.plugins.CiefpScreenGrab.pictureformat.getText() == "jpg":
            cmdoptionquality = " " + str(config.plugins.CiefpScreenGrab.jpegquality.value)
            cmd += cmdoptionquality
        cmd += " -s -q"
        extra_args = (filename)
        self.ScreenshotConsole.ePopen(cmd, self.gotScreenshot, extra_args)

    def gotScreenshot(self, data, retval, extra_args=None):
        if extra_args is not None:
            filename = extra_args
        else:
            filename = ""
        if not config.plugins.CiefpScreenGrab.timeout.value == "off":
            messagetimeout = int(config.plugins.CiefpScreenGrab.timeout.value)
            error = False
            msg_type = MessageBox.TYPE_INFO
            if retval == 0 and filename:
                try:
                    with open(filename, "wb") as file:
                        file.write(data)
                    print(f"[CiefpScreenGrab] Screenshot saved to: {filename}")
                    msg_text = _("Screenshot successfully saved as:\n%s") % filename
                    self.session.open(CiefpScreenGrab, filename)
                except Exception as e:
                    print(f"[CiefpScreenGrab] Error creating file: {e}")
                    error = True
            else:
                error = True
            if error:
                print("[CiefpScreenGrab] Grabbing Screenshot failed")
                msg_text = _("Grabbing Screenshot failed !!!")
                msg_type = MessageBox.TYPE_ERROR
            AddNotification(MessageBox, msg_text, msg_type, timeout=messagetimeout)
        else:
            if retval == 0 and filename:
                try:
                    with open(filename, "wb") as file:
                        file.write(data)
                    print(f"[CiefpScreenGrab] Screenshot saved to: {filename}")
                    self.session.open(CiefpScreenGrab, filename)
                except Exception as e:
                    print(f"[CiefpScreenGrab] Error creating file: {e}")

    def getFilename(self):
        now = systime()
        now = datetime.fromtimestamp(now)
        now = now.strftime("%Y-%m-%d_%H-%M-%S")
        screenshottime = "screenshot_" + now
        if config.plugins.CiefpScreenGrab.pictureformat.getText() == "bmp":
            fileextension = ".bmp"
        elif config.plugins.CiefpScreenGrab.pictureformat.getText() == "jpg":
            fileextension = ".jpg"
        elif config.plugins.CiefpScreenGrab.pictureformat.getText() == "png":
            fileextension = ".png"
        picturepath = getPicturePath()
        if picturepath.endswith('/'):
            screenshotfile = picturepath + screenshottime + fileextension
        else:
            screenshotfile = picturepath + '/' + screenshottime + fileextension
        return screenshotfile

class CiefpScreenGrab(Screen):
    skin = """
    <screen name="CiefpScreenGrab" position="center,center" size="1800,800" title="..:: Ciefp ScreenGrab Preview ::..">
        <widget name="preview" position="0,0" size="1250,750" alphatest="on"/>
        <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/CiefpScreenGrab/background2.png" position="1260,0" size="550,800" zPosition="0"/>
        <eLabel name="key_red" position="0,760" size="150,40" text="Exit" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" foregroundColor="#ffffff"/>
        <eLabel name="key_yellow" position="160,760" size="150,40" text="Files" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" foregroundColor="#ffffff"/>
    </screen>
    """

    def __init__(self, session, filepath):
        Screen.__init__(self, session)
        self.session = session
        self.filepath = filepath
        self["preview"] = Pixmap()
        self["actions"] = ActionMap(["ColorActions", "OkCancelActions"], {
            "red": self.exit,
            "yellow": self.openFiles,
            "cancel": self.exit
        }, -2)
        self.picload = ePicLoad()
        self.onShown.append(self.loadPreview)
        self.setTitle("..:: Ciefp ScreenGrab Preview ::..")

    def loadPreview(self):
        print(f"[CiefpScreenGrab] Loading preview: {self.filepath}")
        try:
            self.picload.setPara([1280, 720, 1, 1, 0, 1, "#00000000"])
            self.picload.startDecode(self.filepath, 0, 0, False)
            ptr = self.picload.getData()
            if ptr:
                self["preview"].instance.setPixmap(ptr)
                print(f"[CiefpScreenGrab] Preview loaded successfully")
            else:
                print(f"[CiefpScreenGrab] Failed to load preview: No data")
        except Exception as e:
            print(f"[CiefpScreenGrab] Error loading preview: {str(e)}")

    def openFiles(self):
        print("[CiefpScreenGrab] Opening FileScreen")
        self.session.open(FileScreen)
        self.close()

    def exit(self):
        print("[CiefpScreenGrab] Exiting CiefpScreenGrab")
        self.close()

class FileScreen(Screen):
    skin = """
    <screen name="FileScreen" position="center,center" size="1800,800" title="..:: Ciefp ScreenGrab Files ::..">
        <widget name="filelist" position="0,0" size="500,700" scrollbarMode="showOnDemand" itemHeight="35" font="Regular;28" />
        <widget name="preview" position="500,0" size="1300,700" alphatest="on"/>
        <eLabel name="key_red" position="0,760" size="150,40" text="Delete" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" foregroundColor="#ffffff"/>
        <eLabel name="key_green" position="160,760" size="150,40" text="Select All" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" foregroundColor="#ffffff"/>
    </screen>
    """

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        self.selected_files = set()
        self.save_path = getPicturePath()
        print(f"[CiefpScreenGrab] Initializing FileScreen for path: {self.save_path}")
        if not path.exists(self.save_path):
            print(f"[CiefpScreenGrab] Directory {self.save_path} does not exist")
            self.session.open(MessageBox, _("Screenshot directory does not exist!"), MessageBox.TYPE_ERROR, timeout=10)
            self.close()
            return
        self["filelist"] = MenuList([], enableWrapAround=True)
        self["preview"] = Pixmap()
        self["actions"] = ActionMap(["ColorActions", "OkCancelActions"], {
            "red": self.deleteFile,
            "green": self.selectAll,
            "ok": self.selectFile,
            "cancel": self.exit
        }, -2)
        self.updateFileList()
        self["filelist"].onSelectionChanged.append(self.updatePreview)
        self.picload = ePicLoad()
        self.timer = eTimer()
        self.timer.callback.append(self.loadPreview)
        self.setTitle("..:: Ciefp ScreenGrab Files ::..")

    def updateFileList(self):
        file_list = []
        for filepath in sorted(glob.glob(path.join(self.save_path, "*.png")) + glob.glob(path.join(self.save_path, "*.jpg")) + glob.glob(path.join(self.save_path, "*.bmp")), reverse=True):
            filename = path.basename(filepath)
            is_selected = filepath in self.selected_files
            display_text = f"[{'X' if is_selected else ' '}] {filename}"
            file_list.append((display_text, filepath, is_selected))
        self["filelist"].setList(file_list)
        print(f"[CiefpScreenGrab] Loaded {len(file_list)} files")

    def updatePreview(self):
        current_entry = self["filelist"].getCurrent()
        if current_entry:
            filepath = current_entry[1]  # filepath is second element in tuple
            print(f"[CiefpScreenGrab] Updating preview for: {filepath}")
            self.timer.start(1, True)

    def loadPreview(self):
        current_entry = self["filelist"].getCurrent()
        if current_entry:
            filepath = current_entry[1]  # filepath is second element in tuple
            print(f"[CiefpScreenGrab] Loading preview: {filepath}")
            try:
                self.picload.setPara([1300, 700, 1, 1, 0, 1, "#00000000"])
                self.picload.startDecode(filepath, 0, 0, False)
                ptr = self.picload.getData()
                if ptr:
                    self["preview"].instance.setPixmap(ptr)
                    print(f"[CiefpScreenGrab] Preview loaded successfully")
                else:
                    print(f"[CiefpScreenGrab] Failed to load preview: No data")
            except Exception as e:
                print(f"[CiefpScreenGrab] Error loading preview: {str(e)}")

    def deleteFile(self):
        if self.selected_files:
            print(f"[CiefpScreenGrab] Deleting {len(self.selected_files)} selected files")
            self.session.openWithCallback(self.deleteFileConfirmed, MessageBox, _("Delete selected files?"), MessageBox.TYPE_YESNO, default=False)
        else:
            print("[CiefpScreenGrab] No files selected for deletion")
            self.session.open(MessageBox, _("No files selected!"), MessageBox.TYPE_INFO, timeout=5)

    def deleteFileConfirmed(self, confirmed):
        if confirmed:
            for filepath in list(self.selected_files):
                try:
                    remove(filepath)
                    print(f"[CiefpScreenGrab] Deleted file: {filepath}")
                except OSError as e:
                    print(f"[CiefpScreenGrab] Failed to delete {filepath}: {str(e)}")
                    self.session.open(MessageBox, f"Failed to delete {filepath}: {str(e)}", MessageBox.TYPE_ERROR, timeout=10)
            self.selected_files.clear()
            self.updateFileList()
            print("[CiefpScreenGrab] FileList refreshed")
            self.session.open(MessageBox, _("Selected files deleted successfully!"), MessageBox.TYPE_INFO, timeout=5)
        else:
            print("[CiefpScreenGrab] Deletion cancelled")

    def selectAll(self):
        print("[CiefpScreenGrab] Selecting all files")
        self.selected_files.clear()
        for filepath in glob.glob(path.join(self.save_path, "*.png")) + glob.glob(path.join(self.save_path, "*.jpg")) + glob.glob(path.join(self.save_path, "*.bmp")):
            self.selected_files.add(filepath)
        self.updateFileList()
        self.session.open(MessageBox, _("All files selected"), MessageBox.TYPE_INFO, timeout=5)

    def selectFile(self):
        current_entry = self["filelist"].getCurrent()
        if current_entry:
            filepath = current_entry[1]  # filepath is second element in tuple
            if filepath in self.selected_files:
                self.selected_files.remove(filepath)
                print(f"[CiefpScreenGrab] Deselected file: {filepath}")
            else:
                self.selected_files.add(filepath)
                print(f"[CiefpScreenGrab] Selected file: {filepath}")
            self.updateFileList()

    def exit(self):
        print("[CiefpScreenGrab] Exiting FileScreen")
        if self["filelist"].onSelectionChanged:
            self["filelist"].onSelectionChanged.remove(self.updatePreview)
        self.close()

class MinimalSkinScreen(Screen):
    skin = """
    <screen name="MinimalSkinScreen" position="1340,50" size="540,40" title="..:: Minimal ScreenGrab ::..">
        <eLabel name="key_red" position="0,0" size="130,40" text="Exit" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" foregroundColor="#ffffff"/>
        <eLabel name="key_green" position="135,0" size="130,40" text="Grab" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" foregroundColor="#ffffff"/>
        <eLabel name="key_yellow" position="270,0" size="130,40" text="Files" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" foregroundColor="#ffffff"/>
        <eLabel name="key_blue" position="405,0" size="130,40" text="Settings" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" foregroundColor="#ffffff"/>
    </screen>
    """

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        self.screenshot = getScreenshot()
        self.screenshot.session = session
        self["actions"] = ActionMap(["ColorActions", "OkCancelActions"], {
            "red": self.exit,
            "green": self.grab,
            "yellow": self.openFiles,
            "blue": self.openSettings,
            "cancel": self.exit
        }, -2)
        self.setTitle("..:: Minimal ScreenGrab ::..")

    def grab(self):
        self.screenshot.grabScreenshot()

    def openFiles(self):
        self.session.open(FileScreen)

    def openSettings(self):
        self.session.open(CiefpGrabScreen)

    def exit(self):
        print("[CiefpScreenGrab] Exiting MinimalSkinScreen")
        self.close()

class CiefpGrabScreen(Screen, ConfigListScreen):
    skin = """
    <screen name="CiefpGrabScreen" position="center,center" size="1800,800" title="..:: CiefpScreenGrab ::..">
        <widget name="config" position="0,0" size="1200,700" scrollbarMode="showOnDemand" itemHeight="35" font="Regular;28" />
        <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/CiefpScreenGrab/background.png" position="1200,0" size="600,800" zPosition="0"/>
        <widget name="key_red" position="0,760" size="150,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" foregroundColor="#ffffff" />
        <widget name="key_green" position="160,760" size="150,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" foregroundColor="#ffffff" />
        <widget name="key_yellow" position="320,760" size="150,40" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" foregroundColor="#ffffff" />
        <widget name="key_blue" position="480,760" size="150,40" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" foregroundColor="#ffffff" />
        <widget name="HelpWindow" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/CiefpScreenGrab/help.png" position="0,0" size="1,1" transparent="1" alphatest="on" zPosition="1" />
    </screen>
    """

    def __init__(self, session):
        self.session = session
        Screen.__init__(self, session)
        self.createConfigList()
        ConfigListScreen.__init__(self, self.list, session=self.session, on_change=self.changedEntry)
        self["key_red"] = Label(_("Exit"))
        self["key_green"] = Label(_("Save"))
        self["key_yellow"] = Label(_("Default"))
        self["key_blue"] = Label(_("Files"))
        self["HelpWindow"] = Pixmap()
        self["setupActions"] = ActionMap(["SetupActions", "ColorActions"], {
            "green": self.keyGreen,
            "red": self.cancel,
            "yellow": self.revert,
            "blue": self.openFileScreen,
            "cancel": self.cancel,
            "ok": self.keyGreen,
        }, -2)
        self.onShown.append(self.setWindowTitle)

    def setWindowTitle(self):
        self.setTitle(_("..:: CiefpScreenGrab ::.. %s") % pluginversion)

    def createConfigList(self):
        self.list = []
        self.list.append(getConfigListEntry(_("Enable CiefpScreenGrab :"), config.plugins.CiefpScreenGrab.enable))
        self.list.append(getConfigListEntry(_("Use Minimal Skin :"), config.plugins.CiefpScreenGrab.miniskin))
        if config.plugins.CiefpScreenGrab.enable.value:
            self.list.append(getConfigListEntry(_("Screenshot of :"), config.plugins.CiefpScreenGrab.picturetype))
            self.list.append(getConfigListEntry(_("Format for screenshots :"), config.plugins.CiefpScreenGrab.pictureformat))
            if config.plugins.CiefpScreenGrab.pictureformat.getText() == "jpg":
                self.list.append(getConfigListEntry(_("Quality of jpg picture :"), config.plugins.CiefpScreenGrab.jpegquality))
            self.list.append(getConfigListEntry(_("Picture size (width) :"), config.plugins.CiefpScreenGrab.picturesize))
            self.list.append(getConfigListEntry(_("Path for screenshots :"), config.plugins.CiefpScreenGrab.path))
            self.list.append(getConfigListEntry(_("Select a button to take a screenshot :"), config.plugins.CiefpScreenGrab.buttonchoice))
            check = config.plugins.CiefpScreenGrab.buttonchoice.value
            if check == "-1":
                buttonname = _("None")
            elif check == "113":
                buttonname = (_("Mute"))
            elif check == "358":
                buttonname = (_("Info"))
            elif check == "362":
                buttonname = (_("Timer"))
            elif check == "365":
                buttonname = (_("EPG"))
            elif check == "377":
                buttonname = (_("TV"))
            elif check == "385":
                buttonname = (_("Radio"))
            elif check == "388":
                buttonname = (_("Text"))
            elif check == "392":
                buttonname = (_("Audio"))
            elif check == "398":
                buttonname = (_("Red"))
            elif check == "399":
                buttonname = (_("Green"))
            elif check == "400":
                buttonname = (_("Yellow"))
            elif check == "401":
                buttonname = (_("Blue"))
            else:
                buttonname = (_("Help"))
            if check in ['398', '399', '400']:
                self.list.append(getConfigListEntry(_("Only button ' ") + buttonname + _(" long ' can be used."), config.plugins.CiefpScreenGrab.dummy))
                config.plugins.CiefpScreenGrab.switchhelp.setValue(False)
            elif check != "-1":
                self.list.append(getConfigListEntry(_("Use the ' ") + buttonname + _(" ' button instead of ' ") + buttonname + _(" long ' :"), config.plugins.CiefpScreenGrab.switchhelp))
            self.list.append(getConfigListEntry(_("Timeout for info message :"), config.plugins.CiefpScreenGrab.timeout))

    def changedEntry(self):
        self.createConfigList()
        self["config"].setList(self.list)

    def save(self):
        for x in self["config"].list:
            x[1].save()
        self.changedEntry()
        self.close()

    def keyGreen(self):
        self.save()

    def cancel(self):
        if self["config"].isChanged():
            self.session.openWithCallback(self.cancelConfirm, MessageBox, _("Really close without saving settings?"), MessageBox.TYPE_YESNO, default=False)
        else:
            for x in self["config"].list:
                x[1].cancel()
            self.close()

    def cancelConfirm(self, result):
        if result:
            print("[CiefpScreenGrab] Cancel confirmed. Config changes will be lost")
            for x in self["config"].list:
                x[1].cancel()
            self.close()
        else:
            print("[CiefpScreenGrab] Cancel not confirmed")

    def revert(self):
        self.session.openWithCallback(self.keyYellowConfirm, MessageBox, _("Reset CiefpScreenGrab settings to defaults?"), MessageBox.TYPE_YESNO, timeout=20, default=False)

    def keyYellowConfirm(self, confirmed):
        if confirmed:
            print("[CiefpScreenGrab] Setting Configuration to defaults")
            config.plugins.CiefpScreenGrab.enable.setValue(True)
            config.plugins.CiefpScreenGrab.miniskin.setValue(True)
            config.plugins.CiefpScreenGrab.switchhelp.setValue(True)
            config.plugins.CiefpScreenGrab.path.setValue("/media/hdd")
            config.plugins.CiefpScreenGrab.pictureformat.setValue("-p")
            config.plugins.CiefpScreenGrab.picturetype.setValue("all")
            config.plugins.CiefpScreenGrab.picturesize.setValue("default")
            config.plugins.CiefpScreenGrab.timeout.setValue("3")
            config.plugins.CiefpScreenGrab.buttonchoice.setValue("-1")
            self.save()
        else:
            print("[CiefpScreenGrab] Reset to defaults not confirmed")

    def openFileScreen(self):
        print("[CiefpScreenGrab] Opening FileScreen")
        self.session.open(FileScreen)

def autostart(reason, session=None, **kwargs):
    if reason == 0 and session is not None:
        print("[CiefpScreenGrab] start...")
        screenshot = getScreenshot()
        screenshot.session = session

def startSetup(session, **kwargs):
    print("[CiefpScreenGrab] Starting config screen")
    if config.plugins.CiefpScreenGrab.miniskin.value:
        session.open(MinimalSkinScreen)
    else:
        session.open(CiefpGrabScreen)

def Plugins(**kwargs):
    return [
        PluginDescriptor(where=PluginDescriptor.WHERE_SESSIONSTART, fnc=autostart),
        PluginDescriptor(
            name="CiefpScreenGrab",
            description=_("Take screenshots of your Enigma2 interface"),
            where=PluginDescriptor.WHERE_PLUGINMENU,
            icon="plugin.png",
            fnc=startSetup
        )
    ]