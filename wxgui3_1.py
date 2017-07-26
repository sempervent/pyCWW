#!/usr/bin/env python
# encoding: utf-8
###############################################################################
#  This is the graphical user interface for pyCWW. This GUI was developed to  #
#  allow people unfamiliar with command-line interfaces to be able to use &   #
#  customize the algorithms used in pyCWW.                                    #
#                                                                             #
#  This interface was programmed by Joshua N. Grant with assistance from      #
#  Caroline Rempe.                                                            #
###############################################################################

# due to differences in wx on *nix machines, wxversion is used
#import wxversion
#wxversion.select("2.8")
import wx
import wx.html
import os
import glob
import xml.etree.ElementTree as et
import json
from cell_wall_erosion_fxn import *


class Frame(wx.Frame):
    def __init__(self, parent, id, title):
        global file_list_box
        wx.Frame.__init__(self, parent, id, title, size=(420, 270), style=
                          wx.DEFAULT_FRAME_STYLE & ~wx.MAXIMIZE_BOX ^
                          wx.RESIZE_BORDER)
        # initiate the file menu
        file_menu = wx.Menu()
        file_menu.Append(ID_FILE_OPEN_FILE, 'Add File')
        file_menu.Append(ID_FILE_OPEN_DIR, 'Add Directory')
        file_menu.AppendSeparator()
        file_menu.Append(ID_FILE_LIST_SAVE, 'Save File List')
        file_menu.Append(ID_FILE_LIST_LOAD, 'Load File List')
        file_menu.Append(ID_FILE_LIST_CLEAR, 'Clear File List')
        file_menu.AppendSeparator()
        file_menu.Append(ID_FILE_EXIT, "Exit Program")
        # initiate the run menu
        run_menu = wx.Menu()
        run_menu.Append(ID_PREVIEW, 'Preview Settings')
        run_menu.Append(ID_CWW, 'Get Cell Wall Widths')
        run_menu.Append(ID_AP, 'Get Area and Perimeter')
        run_menu.AppendSeparator()
        run_menu.Append(ID_RUN_ALL, 'Run All')
        # initiate the help menu
        help_menu = wx.Menu()
        help_menu.Append(ID_HELP_HELP, 'Help')
        help_menu.Append(ID_HELP_ABOUT, 'About')
        # initiate the presets menu
        presets_menu = wx.Menu()
        presets_menu.Append(ID_SET_OUTPUT, 'Choose Output File Location')
        presets_menu.AppendSeparator()
        presets_menu.Append(ID_SETTINGS_SAVE, 'Save Current Settings')
        presets_menu.Append(ID_SETTINGS_LOAD, 'Load Previous Settings')
        presets_menu.AppendSeparator()
        presets_menu.Append(ID_PRESETS_CUSTOM, 'Create Custom Preset')
        presets_menu.Append(ID_PRESETS_HELP, 'Help with Custom Presets')
        # place the menu bar
        menu_bar = wx.MenuBar()
        menu_bar.Append(file_menu, 'File')
        menu_bar.Append(run_menu, 'Run')
        menu_bar.Append(presets_menu, 'Settings')
        menu_bar.Append(help_menu, 'Help')
        self.SetMenuBar(menu_bar)
        # define menu bar events
        wx.EVT_MENU(self, ID_PREVIEW, self.OnPreview)
        wx.EVT_MENU(self, ID_CWW, self.GetCWW)
        wx.EVT_MENU(self, ID_AP, self.GetAP)
        wx.EVT_MENU(self, ID_RUN_ALL, self.RunAll)
        wx.EVT_MENU(self, ID_SETTINGS_SAVE, self.SaveSettings)
        wx.EVT_MENU(self, ID_SETTINGS_LOAD, self.LoadSettings)
        wx.EVT_MENU(self, ID_FILE_OPEN_FILE, self.openFile)
        wx.EVT_MENU(self, ID_FILE_OPEN_DIR, self.openDir)
        wx.EVT_MENU(self, ID_FILE_EXIT, self.OnClose)
        wx.EVT_MENU(self, ID_PRESETS_HELP, self.PresetHelp)
        wx.EVT_MENU(self, ID_PRESETS_CUSTOM, self.PresetConfig)
        wx.EVT_MENU(self, ID_SET_OUTPUT, self.SetOut)
        wx.EVT_MENU(self, ID_HELP_HELP, self.OnHelp)
        wx.EVT_MENU(self, ID_HELP_ABOUT, self.OnAbout)
        wx.EVT_MENU(self, ID_FILE_LIST_SAVE, self.FileListSave)
        wx.EVT_MENU(self, ID_FILE_LIST_LOAD, self.FileListLoad)
        wx.EVT_MENU(self, ID_FILE_LIST_CLEAR, self.FileListClear)
        # place combo box of presets
        self.instructions = wx.StaticText(self,
                                          label="Select your preset:",
                                          pos=(8, 120))
        self.hide_directories = wx.CheckBox(self, -1, 'Hide Directories',
                                            pos=(300, 110))
        self.presetlist = Functions.readPresets()
        self.choose_preset = wx.ComboBox(self, pos=(8, 135), size=(180, -1),
                                         choices=self.presetlist,
                                         style=wx.CB_DROPDOWN | wx.CB_READONLY)
        self.Bind(wx.EVT_COMBOBOX, self.PresetChoice, self.choose_preset)
        # create a listbox
        self.list_box_label = wx.StaticText(self,
                                            label="Files Loaded:",
                                            pos=wx.Point(8, 8))
        self.file_list_box = wx.ListBox(choices=[],
                                        name='file_list_box',
                                        parent=self,
                                        pos=(8, 28),
                                        size=wx.Size(380, 80),
                                        style=0)
        # place the run button and give it id=1
        wx.EVT_CHECKBOX(self, self.hide_directories.GetId(),
                        self.HideDirs)
        wx.Button(self, 1, '   Preview Settings   ', (8, 180))
        wx.Button(self, 2, ' Get Cell Wall Widths ', (128, 180))
        wx.Button(self, 3, 'Get Area and Perimeter', (252, 180))
        wx.Button(self, 4, 'Run All', (310, 150))
        wx.Button(self, 5, 'Update Preset List', (190, 135))
        self.Bind(wx.EVT_BUTTON, self.OnPreview, id=1)
        self.Bind(wx.EVT_BUTTON, self.GetCWW, id=2)
        self.Bind(wx.EVT_BUTTON, self.GetAP, id=3)
        self.Bind(wx.EVT_BUTTON, self.RunAll, id=4)
        self.Bind(wx.EVT_BUTTON, self.UpdatePresetList, id=5)
        # put the image up on the panel
        self.MaxImageSize = 200

    def HideDirs(self, evt):
        global full_file_list
        if self.hide_directories.GetValue():
            full_file_list = self.file_list_box.GetStrings()
            self.file_list_box.Clear()
            for f in full_file_list:
                self.file_list_box.Append(os.path.split(f)[1])
        if not self.hide_directories.GetValue():
            self.file_list_box.Clear()
            for f in full_file_list:
                self.file_list_box.Append(f)

    def SaveSettings(self, evt):
        settings_dict = {}
        settings_dict['outpath'] = outpath
        file_list = self.file_list_box.GetStrings()
        settings_dict['file_list'] = '\n'.join(file_list)
        preset_choice = self.choose_preset.GetValue()
        settings_dict['preset_name'] = preset_choice
        settings_dict['preset_values'] = presets[preset_choice]
        #print settings_dict
        dlg = wx.FileDialog(self, message="Save file list as ...",
                            defaultDir=os.getcwd(), defaultFile="",
                            wildcard="JSON Files (*.json)|*.json",
                            style=wx.SAVE | wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            with open(path, 'wb') as f:  # create a new empty file
                json.dump(settings_dict, f)
        else:
            pass
        dlg.Destroy()

    def LoadSettings(self, evt):
        dlg = wx.FileDialog(self, message="Choose file list ...",
                            defaultDir=os.getcwd(), defaultFile="",
                            wildcard="JSON Files (*.json)|*.json",
                            style=wx.OPEN | wx.CHANGE_DIR)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            with open(path, 'r') as f:
                loaded_preset = json.load(f)
            #print loaded_preset['file_list']
            #print loaded_preset['outpath']
            #print loaded_preset['preset_name']
            #print loaded_preset['preset_values']
            if loaded_preset['preset_name'] in Functions.readPresets():
                self.importAllBut(loaded_preset)
                new_name = False
            elif loaded_preset['preset_name'] not in Functions.readPresets():
                dlg2 = wx.MessageDialog(None,
                                        duplicate_found,
                                        'Duplicate Preset Name Found',
                                        wx.YES_NO | wx.YES_DEFAULT |
                                        wx.ICON_QUESTION)
                if dlg2.ShowModal() == wx.ID_YES:
                    dlg2.Destroy()
                    dlg3 = RenamePreset()
                    dlg3.ShowModal()
                    dlg3.Destroy()
                    loaded_preset['preset_name'] = new_name
                elif dlg2.ShowModal() == wx.ID_NO:
                    new_name = loaded_preset['preset_name']
                    dlg2.Destroy()
                    self.importAllBut(loaded_preset)
                else:
                    dlg2.Destroy()
                    new_name = False
            else:
                pass
            #print Functions.formatXML(loaded_preset['preset_values'],
            #                          new_name)
            dlg.Destroy()

    def importAllNew(self, preset):
        global outpath
        old_file_list = preset['file_list'].split('\n')
        outpath = preset['outpath']
        for entry in old_file_list:
            self.file_list_box.Append(entry)

    def importAllBut(self, preset):
        global outpath
        old_file_list = preset['file_list'].split('\n')
        outpath = preset['outpath']
        self.choose_preset.SetStringSelection(preset['preset_name'])
        for entry in old_file_list:
            self.file_list_box.Append(entry)

    def SetOut(self, evt):
        global outpath
        dd = wx.DirDialog(None, "Select Output Directory ...",
                          "Output Directory", 0, (10, 10), wx.Size(400, 300))
        ret = dd.ShowModal()
        if ret == wx.ID_OK:
            outpath = dd.GetPath()
        else:
            pass

    def UpdatePresetList(self, evt):
        self.choose_preset.SetItems(Functions.readPresets())

    def OnPreview(self, evt):
        if self.hide_directories.IsChecked():
            file_list = full_file_list
        else:
            file_list = self.file_list_box.GetStrings()
        preset_choice = self.choose_preset.GetValue()
        for each_file in file_list:
            (file_out, png_name) = name_files(each_file, outpath)
            print file_out, png_name
            print each_file
            formatted = []
            formatted = Functions.formatValues(presets[preset_choice])
            print formatted
            (im_raw, labels_open, y_center, x_center,
             contours) = process_image(each_file,
                                       png_name,
                                       formatted[0],
                                       formatted[1],
                                       formatted[2],
                                       formatted[3],
                                       formatted[4],
                                       formatted[5],
                                       formatted[6],
                                       formatted[7])
            plot_image(im_raw,
                       labels_open,
                       labels_open,
                       y_center,
                       x_center,
                       contours,
                       png_name,
                       True)

    def GetCWW(self, evt):
        if self.hide_directories.IsChecked():
            file_list = full_file_list
        else:
            file_list = self.file_list_box.GetStrings()
        for each_file in file_list:
            formatted = []
            formatted = Functions.formatValues(presets[preset_choice])
            print formatted
            (file_out, png_name) = name_files(each_file, outpath)
            (im_raw, labels_open, y_center, x_center,
             contours) = process_image(each_file,
                                       png_name,
                                       formatted[0],
                                       formatted[1],
                                       formatted[2],
                                       formatted[3],
                                       formatted[4],
                                       formatted[5],
                                       formatted[6],
                                       formatted[7])
            cell_wall_widths(formatted[4],
                             labels_open,
                             file_out,
                             png_name)
            cell_aggregates(formatted[4],
                            labels_open,
                            file_out,
                            png_name)

    def GetAP(self, evt):
        if self.hide_directories.IsChecked():
            file_list = full_file_list
        else:
            file_list = self.file_list_box.GetStrings()
        for each_file in file_list:
            (file_out, png_name) = name_files(each_file, outpath)
            print file_out, png_name
            print each_file
            formatted = []
            formatted = Functions.formatValues(presets[preset_choice])
            print formatted
            (im_raw, labels_open, y_center, x_center,
             contours) = process_image(each_file,
                                       png_name,
                                       formatted[0],
                                       formatted[1],
                                       formatted[2],
                                       formatted[3],
                                       formatted[4],
                                       formatted[5],
                                       formatted[6],
                                       formatted[7])
            area_perim(int(presets[preset_choice][5]),
                       int(presets[preset_choice][6]),
                       labels_open,
                       contours,
                       file_out)

    def RunAll(self, evt):
        file_list = self.file_list_box.GetStrings()
        #labels_open_eroded = [[]
        # print file_list
        for each_file in file_list:
            (file_out, png_name) = name_files(each_file, outpath)
            formatted = []
            formatted = Functions.formatValues(presets[preset_choice])
            print formatted
            (im_raw, labels_open, y_center, x_center,
             contours) = process_image(each_file,
                                       png_name,
                                       formatted[0],
                                       formatted[1],
                                       formatted[2],
                                       formatted[3],
                                       formatted[4],
                                       formatted[5],
                                       formatted[6],
                                       formatted[7])
            cell_wall_widths(int(presets[preset_choice][4]),
                             labels_open,
                             file_out,
                             png_name)
            cell_aggregates(int(presets[preset_choice][4]),
                            labels_open,
                            file_out,
                            png_name)
            area_perim(int(presets[preset_choice][5]),
                       int(presets[preset_choice][6]),
                       labels_open,
                       contours,
                       file_out)

    def scaleImage(self, evt, image_file):
        img = wx.Image(image_file, wx.BITMAP_TYPE_ANY)
        # scale the image, preserving the aspect ratio
        W = img.GetWidth()
        H = img.GetHeight()
        if W > H:
            NewW = self.MaxImageSize
            NewH = self.MaxImageSize * H / W
        else:
            NewH = self.MaxImageSize
            NewW = self.MaxImageSize * W / H
        img = img.Scale(NewW, NewH)

    def openDir(self, evt):
        dlg = wx.DirDialog(self, "Choose a directory:",
                           style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            dirpath = dlg.GetPath()
            print "You selected: %s" % dirpath
            dlg.Destroy()
            print self.getImageFilesInDir(dirpath)
            return dirpath
        else:
            dlg.Destroy()
            return

    def getImageFilesInDir(self, dirpath):
        global image_file_paths
        image_files = []
        image_file_paths = []
        os.chdir(dirpath)
        print dirpath
        for files in filetypes:
            image_files.extend(glob.glob(files))
        for item in image_files:
            temp = os.path.join(dirpath, item)
            image_file_paths.append(temp)
        for item in image_file_paths:
            self.file_list_box.Append(item)
            full_file_list.append(item)
        os.chdir(app_path)
        return image_file_paths

    def openFile(self, evt):
        global mypath
        dlg = wx.FileDialog(self, "Choose a file", os.getcwd(),
                            "Image Files", imagetypes,
                            wx.OPEN | wx.FD_MULTIPLE)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            mypath = os.path.abspath(path)
            print "You selected: %s" % mypath
            full_file_list.append(mypath)
            self.file_list_box.Append(mypath)
        dlg.Destroy()

    def ToDo(self, evt):
        dlg = wx.MessageDialog(self, 'Not Yet Impliminted'
                               'ToDo', wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def OnClose(self, evt):
        dlg = wx.MessageDialog(self, 'Do you really want to exit?',
                               "Confirm Exit",
                               wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            self.Destroy()

    def OnAbout(self, evt):
        dlg = AboutBox()
        dlg.ShowModal()
        dlg.Destroy()

    def OnHelp(self, evt):
        dlg = HelpBox()
        dlg.ShowModal()
        dlg.Destroy()

    def PresetConfig(self, evt):
        dlg = ConfigurePresets()
        dlg.ShowModal()
        dlg.Destroy()

    def SelectPreset(self, evt):
        dlg = SelectPresetWindow()
        dlg.ShowModal()
        dlg.Destroy()

    def PresetHelp(self, evt):
        dlg = PresetsHelp()
        dlg.ShowModal()
        dlg.Destroy()

    def PresetChoice(self, evt):
        global preset_choice
        preset_choice = evt.GetString()
        preset_values = Functions.xmlread()[preset_choice]
        print preset_values

    def FileListSave(self, evt):
        saveLB = self.file_list_box.GetStrings()
        saveFL = '\n'.join(saveLB)
        dlg = wx.FileDialog(self, message="Save file list as ...",
                            defaultDir=os.getcwd(), defaultFile="",
                            wildcard="Text Files (*.txt)|*.txt",
                            style=wx.SAVE | wx.FD_OVERWRITE_PROMT)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            flp = file(path, 'w')  # create a new empty file
            flp.write(saveFL)
            flp.close()
        else:
            pass
        dlg.Destroy()

    def FileListClear(self, evt):
        global full_file_list
        self.file_list_box.Clear()
        full_file_list = []

    def FileListLoad(self, evt):
        global full_file_list
        dlg = wx.FileDialog(self, message="Choose file list ...",
                            defaultDir=os.getcwd(), defaultFile="",
                            wildcard="Text Files (*.txt)|*.txt",
                            style=wx.OPEN | wx.CHANGE_DIR)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            flp = file(path, 'r')  # opens the file
            listEntry = flp.read().splitlines()
            print listEntry
            for entry in listEntry:
                self.file_list_box.Append(entry)
                full_file_list.append(entry)
                print full_file_list
            dlg.Destroy()


class RenamePreset(wx.Dialog):
    def __init__(self):
        wx.Dialog.__init__(self, None, -1, "Rename Preset",
                           style=wx.DEFAULT_DIALOG_STYLE | wx.THICK_FRAME |
                           wx.TAB_TRAVERSAL, size=(300, 100))
        #pnl = wx.Panel(self)
        self.rename_lbl = wx.StaticText(self,
                                        label="Please Choose a New Name:",
                                        pos=wx.Point(8, 8))
        self.rename_box = wx.TextCtrl(self,
                                      value="",
                                      pos=(8, 24),
                                      size=(200, -1))
        self.rename_btn = wx.Button(self,
                                    label="Rename",
                                    pos=(210, 24))
        self.Bind(wx.EVT_BUTTON, self.rename_preset, self.rename_btn)

    def rename_preset(self, event):
        global new_name
        new_name = self.rename_box.GetValue()
        new_name = new_name.replace(" ", "_")
        if new_name in Functions.readPresets():
            self.preset_name_found()
        elif new_name == "":
            pass
        else:
            self.Destroy()

    def preset_name_found(self):
        dlg = wx.MessageDialog(self, 'Choose another name...',
                               'Preset Name Found',
                               wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()


class App(wx.App):
    def OnInit(self):
        frame = Frame(None, -1, 'pyCWW - GUI - Powered by wxPython')
        frame.Show(True)
        self.SetTopWindow(frame)
        return True


class HelpBox(wx.Dialog):
    def __init__(self):
        wx.Dialog.__init__(self, None, -1, "Help for pyCWW",
                           style=wx.DEFAULT_DIALOG_STYLE | wx.THICK_FRAME |
                           wx.RESIZE_BORDER | wx.TAB_TRAVERSAL)
        hwin = HtmlWindow(self, -1, size=(400, 200))
        hwin.SetPage(helpText)
        btn = hwin.FindWindowById(wx.ID_OK)
        irep = hwin.GetInternalRepresentation()
        self.SetClientSize(hwin.GetSize())
        self.CentreOnParent(wx.BOTH)
        self.SetFocus()


class PresetsHelp(wx.Dialog):
    def __init__(self):
        wx.Dialog.__init__(self, None, -1, "Help for pyCWW Presets",
                           style=wx.DEFAULT_DIALOG_STYLE | wx.THICK_FRAME |
                           wx.RESIZE_BORDER | wx.TAB_TRAVERSAL)
        hwin = HtmlWindow(self, -1, size=(400, 200))
        hwin.SetPage(presetsHelp)
        btn = hwin.FindWindowById(wx.ID_OK)
        irep = hwin.GetInternalRepresentation()
        self.SetClientSize(hwin.GetSize())
        self.CentreOnParent(wx.BOTH)
        self.SetFocus()


class AboutBox(wx.Dialog):
    def __init__(self):
        wx.Dialog.__init__(self, None, -1, "About pyCWW",
                           style=wx.DEFAULT_DIALOG_STYLE | wx.THICK_FRAME |
                           wx.RESIZE_BORDER | wx.TAB_TRAVERSAL)
        hwin = HtmlWindow(self, -1, size=(400, 200))
        hwin.SetPage(aboutText)
        btn = hwin.FindWindowById(wx.ID_OK)
        irep = hwin.GetInternalRepresentation()
        #hwin.setSize((irep.GetWidth() + 25, irep.GetHeight() + 10))
        self.SetClientSize(hwin.GetSize())
        self.CentreOnParent(wx.BOTH)
        self.SetFocus()


class ConfigurePresets(wx.Dialog):
    def __init__(self):
        wx.Dialog.__init__(self, None, -1, "Configure Presets",
                           style=wx.CAPTION | wx.CLOSE_BOX | wx.THICK_FRAME |
                           wx.SYSTEM_MENU, size=(500, 255))
        pnl = wx.Panel(self)
        main_lbl = "Experiment with these values to improve"
        main_lbl += " the results of pyCWW."
        self.main_label = wx.StaticText(self, label=main_lbl, pos=(2, 2))
        self.threshold_lbl = wx.StaticText(self,
                                           label="Threshold:",
                                           pos=(2, 18))
        self.gauss_lbl = wx.StaticText(self,
                                       label="Gaussian Blur:",
                                       pos=(2, 62))
        self.bin_open = wx.StaticText(self,
                                      label="Binary Opening Iterations:",
                                      pos=(2, 109))
        self.bin_close = wx.StaticText(self,
                                       label="Binary Closing Iterations:",
                                       pos=(2, 156))
        self.dilations = wx.StaticText(self,
                                       label="Dilation Iterations:",
                                       pos=(150, 18))
        self.area_cut = wx.StaticText(self,
                                      label="Area Cutoff:",
                                      pos=(150, 62))
        self.perim_cut = wx.StaticText(self,
                                       label="Perimeter Cutoff:",
                                       pos=(150, 109))
        self.preset_name = wx.StaticText(self,
                                         label="Preset Name:",
                                         pos=(150, 156))
        self.preset_name = wx.StaticText(self,
                                         label="Structuring Element:",
                                         pos=(300, 18))
        self.select_elem_lbl = wx.StaticText(self,
                                             label="Select Predefined " +
                                             "Structuring Element:",
                                             pos=(300, 120))
        self.select_preset = wx.StaticText(self,
                                           label="Select Preset to View/Edit:",
                                           pos=(300, 160))
        self.edit_thresh = wx.TextCtrl(self,
                                       value="",
                                       pos=(2, 36),
                                       size=(140, -1))
        self.edit_gauss = wx.TextCtrl(self,
                                      value="",
                                      pos=(2, 80),
                                      size=(140, -1))
        self.edit_bin_o = wx.TextCtrl(self,
                                      value="",
                                      pos=(2, 127),
                                      size=(140, -1))
        self.edit_bin_c = wx.TextCtrl(self,
                                      value="",
                                      pos=(2, 174),
                                      size=(140, -1))
        self.edit_dilations = wx.TextCtrl(self,
                                          value="",
                                          pos=(150, 36),
                                          size=(140, -1))
        self.edit_area = wx.TextCtrl(self,
                                     value="",
                                     pos=(150, 80),
                                     size=(140, -1))
        self.edit_perim = wx.TextCtrl(self,
                                      value="",
                                      pos=(150, 127),
                                      size=(140, -1))
        self.edit_name = wx.TextCtrl(self,
                                     value="",
                                     pos=(150, 174),
                                     size=(140, -1))
        self.edit_elem = wx.TextCtrl(self,
                                     value="",
                                     pos=(300, 36),
                                     size=(160, 75),
                                     style=wx.TAB_TRAVERSAL | wx.TE_MULTILINE
                                     | wx.TE_LINEWRAP | wx.TE_PROCESS_ENTER
                                     )
        self.pred_elem = wx.ComboBox(self,
                                     choices=struct_elem_choices,
                                     pos=(300, 135),
                                     size=(160, 18),
                                     style=wx.CB_DROPDOWN | wx.CB_READONLY)
        self.presetlist = Functions.readPresets()
        self.preset_select = wx.ComboBox(self,
                                         choices=self.presetlist,
                                         pos=(300, 175),
                                         size=(160, 18),
                                         style=wx.CB_DROPDOWN | wx.CB_READONLY)
        self.save_btn = wx.Button(self, label="Save", pos=(200, 200))
        self.reset_btn = wx.Button(self,
                                   label="Default Presets",
                                   pos=(100, 200))
        self.preview_btn = wx.Button(self, label="Preview Settings",
                                     pos=(8, 200))
        self.Bind(wx.EVT_BUTTON, self.OnSave, self.save_btn)
        self.Bind(wx.EVT_BUTTON, self.Reset, self.reset_btn)
        self.Bind(wx.EVT_BUTTON, self.OnPreview, self.preview_btn)
        self.Bind(wx.EVT_COMBOBOX, self.OnSelect, self.pred_elem)
        self.Bind(wx.EVT_COMBOBOX, self.PresetSelect, self.preset_select)

    def OnPreview(self, event):
        error_happen = False
        new_values = []
        new_values.append(self.edit_thresh.GetValue())
        new_values.append(self.edit_gauss.GetValue())
        new_values.append(self.edit_bin_o.GetValue())
        new_values.append(self.edit_bin_c.GetValue())
        new_values.append(self.edit_dilations.GetValue())
        new_values.append(self.edit_area.GetValue())
        new_values.append(self.edit_perim.GetValue())
        new_values.append(str(self.edit_elem.GetValue()))
        chk = Errors.check_threshold(new_values[0], 2)
        if chk[0]:
            error_happen = True
            self.OnError(chk[1])
        for i in range(1, 6):
            chk = Errors.check_int(i, new_values[i])
            if chk[0]:
                error_happen = True
                self.OnError(chk[1])
        # check the structuring element
        chk = Errors.check_structure(new_values[7])
        print full_file_list
        if not chk[0]:
            error_happen = True
            self.OnError(chk[1])
        if not error_happen:
            test_file = full_file_list[0]
            (file_out, png_name) = name_files(test_file, outpath)
            formatted = Functions.formatValues(new_values)
            print formatted
            (im_raw, labels_open, y_center, x_center,
             contours) = process_image(test_file,
                                       png_name,
                                       formatted[0],
                                       formatted[1],
                                       formatted[2],
                                       formatted[3],
                                       formatted[4],
                                       formatted[5],
                                       formatted[6],
                                       formatted[7])
            plot_image(im_raw,
                       labels_open,
                       labels_open,
                       y_center,
                       x_center,
                       contours,
                       png_name,
                       True)


    def PresetSelect(self, event):
        item = event.GetSelection()
        preset_values = presets[self.presetlist[item]]
        self.edit_thresh.SetValue(preset_values[0])
        self.edit_gauss.SetValue(preset_values[1])
        self.edit_bin_o.SetValue(preset_values[2])
        self.edit_bin_c.SetValue(preset_values[3])
        self.edit_dilations.SetValue(preset_values[4])
        self.edit_area.SetValue(preset_values[5])
        self.edit_perim.SetValue(preset_values[6])
        self.edit_elem.SetValue(preset_values[7])
        self.edit_name.SetValue(self.presetlist[item])

    def OnSelect(self, event):
        item = event.GetSelection()
        #self.edit_elem.SetFocus()
        self.edit_elem.SetValue(struct_elem_values[item])

    def OnSave(self, event):
        error_happen = False
        new_values = []
        new_values.append(self.edit_thresh.GetValue())
        new_values.append(self.edit_gauss.GetValue())
        new_values.append(self.edit_bin_o.GetValue())
        new_values.append(self.edit_bin_c.GetValue())
        new_values.append(self.edit_dilations.GetValue())
        new_values.append(self.edit_area.GetValue())
        new_values.append(self.edit_perim.GetValue())
        new_values.append(str(self.edit_elem.GetValue()))
        #print new_values
        name = self.edit_name.GetValue()
        if name in self.presetlist:
            msg = "A preset named %s already exists" % name
            self.OnError(msg)
        else:
            # check the threshold
            print Errors.check_threshold(new_values[0], 2)
            chk = Errors.check_threshold(new_values[0], 2)
            if chk[0]:
                error_happen = True
                self.OnError(chk[1])
            # check the other values
            for i in range(1, 6):
                chk = Errors.check_int(i, new_values[i])
                if chk[0]:
                    error_happen = True
                    self.OnError(chk[1])
            # check the structuring element
            #print new_values[7]
            #print Errors.check_structure(new_values[7])
            chk = Errors.check_structure(new_values[7])
            if not chk[0]:
                error_happen = True
                self.OnError(chk[1])
            # ask to save if nothing messed up
            if not error_happen:
                dlg = wx.MessageDialog(self, 'Are you sure you want to save?',
                                       'Confirm Save?',
                                       wx.OK | wx.CANCEL | wx.ICON_INFORMATION)
                result = dlg.ShowModal()
                if result == wx.ID_OK:
                    print new_values, name
                    print new_values[3]
                    Functions.xmlUpdate(name, new_values)
                    dlg.Destroy()
                    self.Destroy()
                else:
                    dlg.Destroy()

    def Reset(self, event):
        dlg = wx.MessageDialog(self,
                               'Are you sure you want to reset config.xml?',
                               'Confirm Reset?',
                               wx.OK | wx.CANCEL | wx.ICON_INFORMATION)
        result = dlg.ShowModal()
        if result == wx.ID_OK:
            Functions.xmlreset()
            dlg.Destroy()
        else:
            dlg.Destroy()

    def OnError(self, message):
        dlg = wx.MessageDialog(self, message,
                               'Error!', wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()


class SelectPresetWindow(wx.Dialog):
    def __init__(self):
        wx.Dialog.__init__(self, None, -1, "Choose Your Preset",
                           style=wx.DEFAULT_DIALOG_STYLE | wx.THICK_FRAME,
                           size=(250, 100))
        self.instructions = wx.StaticText(self,
                                          label="Select Your Preset:",
                                          pos=(10, 10))
        self.presetlist = Functions.readPresets()
        self.choose_preset = wx.ComboBox(self, pos=(10, 30), size=(95, -1),
                                         choices=self.presetlist,
                                         style=wx.CB_DROPDOWN)
        self.close_btn = wx.Button(self, label="Close", pos=(100, 80))
        self.Bind(wx.EVT_COMBOBOX, self.PresetChoice, self.choose_preset)
        self.Bind(wx.EVT_BUTTON, self.Close, self.close_btn)

    def PresetChoice(self, event):
        global preset_choice
        print "You chose %s" % event.GetString()
        preset_choice = event.GetString()
        print Functions.xmlread()[preset_choice]

    def Close(self, event):
        self.Destroy()


class HtmlWindow(wx.html.HtmlWindow):
    def __init__(self, parent, id, size=(600, 400)):
        wx.html.HtmlWindow.__init__(self, parent, id, size=size)
        if "gtk" in wx.PlatformInfo:
            self.SetStandardFonts()

    def OnLinkClicked(self, link):
        wx.LaunchDefaultBrowser(link.GetHref())


class Functions:
    @staticmethod
    def formatXML(preset, name):
        thresh = preset[0]
        gauss = preset[1]
        binO = preset[2]
        binC = preset[3]
        dila = preset[4]
        area = preset[5]
        perim = preset[6]
        elem = preset[7]
        return xml_preset_format % (name, thresh, gauss, binO, binC,
                                    dila, area, perim, elem, name)

    @staticmethod
    def xmlAdd(preset):
        xmlFile = "config.xml"
        xml_in = open(xmlFile, 'r')
        lines = xml_in.readlines()
        with open(xmlFile, 'w') as xml_out:
            for line in lines:
                xml_out.write(line)
                if line == "<Presets>\n":
                    xml_out.write(preset)

    @staticmethod
    def xmlread():
        global presets
        presets = {}
        ######################################################
        # xml data should have the following format:         #
        # Threshold         presets[preset_choice][0]        #
        # Gaussian Blur     presets[preset_choice][1]        #
        # Binary Open Iter  presets[preset_choice][2]        #
        # Binary Close Iter presets[preset_choice][3]        #
        # Dilation Iter     presets[preset_choice][4]        #
        # Area Cutoff       presets[preset_choice][5]        #
        # Perim Cutoff      presets[preset_choice][6]        #
        # Structuring Elem  presets[preset_choice][7]        #
        ######################################################
        xmlFile = "config.xml"
        tree = et.parse(xmlFile)
        root = tree.getroot()
        for child in root:
            child_values = []
            for value in child:
                child_values.append(value.text)
            presets[child.tag] = child_values
        return presets

    @staticmethod
    def xmlUpdate(name, new_values):
        xmlFile = "config.xml"
        xml_in = open(xmlFile, 'r')
        lines = xml_in.readlines()
        thresh_line = '\t\t<threshold>%s</threshold>\n'
        gauss_line = '\t\t<gauss_blur>%s</gauss_blur>\n'
        bin_open = '\t\t<binary_open_iterations>%s'
        bin_open += '</binary_open_iterations>\n'
        bin_close = '\t\t<binary_close_iterations>%s'
        bin_close += '</binary_close_iterations>\n'
        dil_iter = "\t\t<dilation_iterations>%s"
        dil_iter += "</dilation_iterations>\n"
        area_line = "\t\t<area_cutoff>%s"
        area_line += "</area_cutoff>\n"
        perim_line = "\t\t<perimeter_cutoff>%s"
        perim_line += "</perimeter_cutoff>\n"
        struct_line = "\t\t<structuring_element>%s"
        struct_line += "</structuring_element>\n"
        print lines
        with open(xmlFile, 'w') as xml_out:
            for line in lines:
                xml_out.write(line)
                if line == "<Presets>\n":
                    xml_out.write('\t<%s>\n' % name)
                    xml_out.write(thresh_line % new_values[0])
                    xml_out.write(gauss_line % new_values[1])
                    xml_out.write(bin_open % new_values[2])
                    xml_out.write(bin_close % new_values[3])
                    xml_out.write(dil_iter % new_values[4])
                    xml_out.write(area_line % new_values[5])
                    xml_out.write(perim_line % new_values[6])
                    xml_out.write(struct_line % new_values[7])
                    xml_out.write('\t</%s>\n' % name)

    @staticmethod
    def xmlreset():
        xmlFile = "config.xml"
        with open(xmlFile, 'w') as xml:
            xml.write('<?xml version="1.0"?>\n')
            xml.write('<Presets>\n')
            xml.write(default_presets)
            xml.write('</Presets>')

    @staticmethod
    def readPresets():
        xml = Functions.xmlread()
        presets = xml.keys()
        print presets
        return presets

    @staticmethod
    def formatValues(preset_values):
        thresh = preset_values[0]
        gauss = preset_values[1]
        binO = preset_values[2]
        binC = preset_values[3]
        dil = preset_values[4]
        area = preset_values[5]
        perim = preset_values[6]
        elem = preset_values[7]
        if thresh != "mean":
            thresh = int(thresh)
        else:
            pass
        gauss = int(gauss)
        binO = int(binO)
        binC = int(binC)
        dil = int(dil)
        area = int(area)
        perim = int(perim)
        elem = Errors.check_structure(elem)[2]
        return [thresh, gauss, binO, binC, dil, area, perim, elem]


class Errors():
    @staticmethod
    def check_threshold(threshold, Return):
        accept = False
        if threshold == "mean":
            accept = True
            if Return == 2:
                return [False, "good"]
        try:
            int(threshold)
            if Return == 2:
                return [False, "good"]
        except ValueError:
            if accept:
                pass
            else:
                return [True, "Threshold must be 'mean' or an integer!"]

    @staticmethod
    def check_int(var, number):
        try:
            int(number)
            return [False, "good"]
        except ValueError:
            return [True, "Non-threshold value, %s, must be integers" %
                    preset_values_list[var]]

    @staticmethod
    def check_structure(elem):
        msg = ""
        elem = str(elem)
        rtrn_array = []
        if elem[0:2] == "[[":
            #elem = elem[1:]
            brackets = elem.split("],[")
            for i in brackets:
                if i.startswith("[["):
                    rtrn_array.append(i[2:].strip(",").split(","))
                elif i.endswith("]]"):
                    rtrn_array.append(i.strip("]]").split(","))
                else:
                    rtrn_array.append(i.split(","))
            #print rtrn_array
            success = True
            msg = "good"
        else:
            msg = "Structuring element needs to be in the format:\n"
            msg += "\t[[1,1,1],[1,1,1],[1,1,1]]"
            success = False
        return (success, msg, rtrn_array)


def def_text():
    global aboutText, helpText, default_presets, presetsHelp
    global preset_values_list, struct_elem_choices
    global struct_elem_values, xml_preset_format, duplicate_found

    duplicate_found = "A preset already exists with this setting's"
    duplicate_found += " preset name. Would you like to rename this "
    duplicate_found += "preset?\n(Selecting 'No' loads preset with existing "
    duplicate_found += "name)"

    xml_preset_format = "\t<%s>\n"
    xml_preset_format += "\t\t<threshold>%s</threshold>\n"
    xml_preset_format += "\t\t<gauss_blur>%s</gauss_blur>\n"
    xml_preset_format += "\t\t<binary_open_iterations>%s"
    xml_preset_format += "</binary_open_iteraions>\n"
    xml_preset_format += "\t\t<binary_close_iterations>%s"
    xml_preset_format += "</binary_close_iterations>\n"
    xml_preset_format += "\t\t<dilation_iterations>%s"
    xml_preset_format += "</dilation_iterations>\n"
    xml_preset_format += "\t\t<area_cutoff>%s"
    xml_preset_format += "</area_cutoff>\n"
    xml_preset_format += "\t\t<perimeter_cutoff>%s"
    xml_preset_format += "</perimeter_cutoff>\n"
    xml_preset_format += "\t\t<structuring_element>%s"
    xml_preset_format += "</structuring_element>\n"
    xml_preset_format += "\t</%s>\n"

    preset_values_list = ['Threshold', 'Gaussian Blur',
                          'Binary Opening Iterations',
                          'Binary Closing Iterations',
                          'Dilation Iterations', 'Area Cutoff',
                          'Perimeter Cutoff', 'Structuring Element']

    struct_elem_choices = ['2x2 Square', '3x3 Square', '3x3 Right Triangle',
                           '3x3 Cross', '3x3 "X"',
                           '4x4 Square', '4x4 Right Triangle',
                           '4x4 Cross', '4x4 "X"', '5x5 Square',
                           '5x5 Right Traingle', 'Custom']

    struct_elem_values = ['[[1,1],[1,1]', '[[1,1,1],[1,1,1],[1,1,1]]',
                          '[[1,0,0],[1,1,0],[1,1,1]]',
                          '[[0,1,0],[1,1,1],[0,1,0]]',
                          '[[1,0,1],[0,1,0],[1,0,1]]',
                          '[[1,1,1,1],[1,1,1,1],[1,1,1,1],[1,1,1,1]]',
                          '[[1,0,0,0],[1,1,0,0],[1,1,1,0],[1,1,1,1]]',
                          '[[0,1,1,0],[1,1,1,1],[1,1,1,1],[0,1,1,0]]',
                          '[[1,0,0,1],[0,1,1,0],[0,1,1,0],[1,0,0,1]]',
                          '[[1,1,1,1,1],[1,1,1,1,1],[1,1,1,1,1],[1,1,1,1,1]' +
                          '[1,1,1,1,1]]',
                          '[[1,0,0,0,0],[1,1,0,0,0],[1,1,1,0,0],[1,1,1,1,0]' +
                          '[1,1,1,1,1]]',
                          '']

    aboutText = """
    <p>This program was developed at the University of Tennessee - Knoxville
    by Caroline Rempe and Joshua N. Grant to quantify cell characteristics,
    from images of plant cells. Joe Hughes developed the method of
    finding cell wall widths. This program was written in Python with use of
    numpy, scipy.ndimage, wxpython, ....</p>
    """

    helpText = """
    <h1>Documentation for pyCWW</h1>
    <p>This is a tool intended to find a distribution of plant cell wall
    widths in addition to cell area and perimeter. The results are output to
    text files and can be visualized with plots of the input image.</p><br>
    <p>For all analyses, the first step is image processing. An image must be
    selected from a saved file and then processing variables must be set.
    There are 4 preset options with variables optimized to image types that
    this tool was designed for. Please see Custom Preset Help for more details
    about what each variable does.</p><br>
    <p>Once variables have been selected, use Preview to visualize the current
    processing methods and verify that they meet your needs. When you are
    satisfied, you can continue analysis by measuring cell wall widths or
    calculating area and perimeter. Or, if you would like to do all three of
    these tasks, click Run All.</p><br>
    <p>Cell wall widths and area and perimeter each create their own data
    output files, [naming scheme]. A plot of cell wall width distributions is
    also created, and an image with centroids marked by red dots and labeled
    objects indicated by different shades of gray is both opened and saved to
    a png file with Preview.</p>
    """

    default_presets = ('\t<Confocal>\n'
                       '\t\t<threshold>170</threshold>\n'
                       '\t\t<gauss_blur>3</gauss_blur>\n'
                       '\t\t<binary_open_iterations>1'
                       '</binary_open_iterations>\n'
                       '\t\t<binary_close_iterations>'
                       '1</binary_close_iterations>\n'
                       '\t\t<dilation_iterations>15</dilation_iterations>\n'
                       '\t\t<area_cutoff>3000</area_cutoff>\n'
                       '\t\t<perimeter_cutoff>350</perimeter_cutoff>\n'
                       '\t\t<structuring_element>[[1,1,1],[1,1,1],[1,1,1]]'
                       '</structuring_element>\n'
                       '\t</Confocal>\n'
                       '\t<Confocal_Avg>\n'
                       '\t\t<threshold>mean</threshold>\n'
                       '\t\t<gauss_blur>3</gauss_blur>\n'
                       '\t\t<binary_open_iterations>1'
                       '</binary_open_iterations>\n'
                       '\t\t<binary_close_iterations>'
                       '1</binary_close_iterations>\n'
                       '\t\t<dilation_iterations>15</dilation_iterations>\n'
                       '\t\t<area_cutoff>3000</area_cutoff>\n'
                       '\t\t<perimeter_cutoff>350</perimeter_cutoff>\n'
                       '\t\t<structuring_element>[[1,1,1],[1,1,1],[1,1,1]]'
                       '</structuring_element>\n'
                       '\t</Confocal_Avg>\n'
                       '\t<Bright_Field>\n'
                       '\t\t<threshold>70</threshold>\n'
                       '\t\t<gauss_blur>4</gauss_blur>\n'
                       '\t\t<binary_open_iterations>4'
                       '</binary_open_iterations>\n'
                       '\t\t<binary_close_iterations>4'
                       '</binary_close_iterations>\n'
                       '\t\t<dilation_iterations>15</dilation_iterations>\n'
                       '\t\t<area_cutoff>3000</area_cutoff>\n'
                       '\t\t<perimeter_cutoff>350</perimeter_cutoff>\n'
                       '\t\t<structuring_element>[[1,1,1],[1,1,1],[1,1,1]]'
                       '</structuring_element>\n'
                       '\t</Bright_Field>\n'
                       '\t<Dark_Field>\n'
                       '\t\t<threshold>30</threshold>\n'
                       '\t\t<gauss_blur>2</gauss_blur>\n'
                       '\t\t<binary_open_iterations>'
                       '4</binary_open_iterations>\n'
                       '\t\t<binary_close_iterations>4'
                       '</binary_close_iterations>\n'
                       '\t\t<dilation_iterations>15</dilation_iterations>\n'
                       '\t\t<area_cutoff>3000</area_cutoff>\n'
                       '\t\t<perimeter_cutoff>350</perimeter_cutoff>\n'
                       '\t\t<structuring_element>[[1,1,1],[1,1,1],[1,1,1]]'
                       '</structuring_element>\n'
                       '\t</Dark_Field>\n'
                       '\t<Cell_Culture>\n'
                       '\t\t<threshold>30</threshold>\n'
                       '\t\t<gauss_blur>2</gauss_blur>\n'
                       '\t\t<binary_open_iterations>3'
                       '</binary_open_iterations>\n'
                       '\t\t<binary_close_iterations>3'
                       '</binary_close_iterations>\n'
                       '\t\t<dilation_iterations>15</dilation_iterations>\n'
                       '\t\t<area_cutoff>3000</area_cutoff>\n'
                       '\t\t<perimeter_cutoff>350</perimeter_cutoff>\n'
                       '\t\t<structuring_element>[[1,1,1],[1,1,1],[1,1,1]]'
                       '</structuring_element>\n'
                       '\t</Cell_Culture>\n')
    presetsHelp = """<h1>Presets Help</h1>
    <p>The Confocal preset is designed for flourescently labeled
    cross-sections of plant vascular material. This preset was designed to
    optimally calculate cell wall widths of plant vascular cells.</p><br>
    <p>The Brightfield preset was intended for use with brightfield images, in
    which lighter grays dominate over blacks.</p><br>
    <p>The Custom preset allow the user to adjust and save whatever settings
    are useful for his/her applications. Threshold is the value at which a
    binary (black/white) cutoff is made, and must be within the range of 0 and
    255, or a mean of pixel values in the input image can be calculated with
    'mean'. Gaussian blur iterations, used to blur away noise in an image, can
    be adjusted with gauss_blur values. Iterations of binary opening and
    closing to clean noise surrounding objects and within objects can be
    specified. Also, the maximum number of cell wall widths output is
    controlled by the number of dilation iterations. Cut-offs (in pixels) of
    area and perimeter can also be specified.
    </p>"""


def main():
    global ID_FILE_OPEN_FILE, ID_FILE_OPEN_DIR, ID_FILE_EXIT
    global ID_PRESETS_HELP, ID_PRESETS_CUSTOM, ID_HELP_ABOUT
    global ID_HELP_HELP, aboutText, helpText, filetypes, imagetypes
    global ID_PRESETS_RESET, app_path, default_presets, presetsHelp
    global ID_FILE_LIST_SAVE, ID_FILE_LIST_LOAD, ID_FILE_LIST_CLEAR
    global ID_SET_OUTPUT, ID_CWW, ID_AP, ID_PREVIEW, ID_RUN_ALL
    global ID_SETTINGS_SAVE, ID_SETTINGS_LOAD, outpath, new_name
    global full_file_list
    full_file_list = []
    new_name = ""
    app_path = os.path.dirname(os.path.abspath(__file__))
    outpath = app_path
    def_text()
    if os.path.isfile('config.xml'):
        pass
    else:
        with open('config.xml', 'wb') as out:
            out.write('<?xml version="1.0"?>\n')
            out.write("<Presets>\n")
            out.write(default_presets)
            out.write("</Presets>\n")

    ID_RUN_ALL = wx.NewId()
    ID_CWW = wx.NewId()
    ID_AP = wx.NewId()
    ID_PREVIEW = wx.NewId()
    ID_FILE_OPEN_FILE = wx.NewId()
    ID_FILE_OPEN_DIR = wx.NewId()
    ID_FILE_EXIT = wx.NewId()
    ID_PRESETS_HELP = wx.NewId()
    ID_PRESETS_CUSTOM = wx.NewId()
    ID_PRESETS_RESET = wx.NewId()
    ID_HELP_HELP = wx.NewId()
    ID_HELP_ABOUT = wx.NewId()
    ID_FILE_LIST_SAVE = wx.NewId()
    ID_FILE_LIST_LOAD = wx.NewId()
    ID_FILE_LIST_CLEAR = wx.NewId()
    ID_SET_OUTPUT = wx.NewId()
    ID_SETTINGS_SAVE = wx.NewId()
    ID_SETTINGS_LOAD = wx.NewId()
    filetypes = ('*.jpg', '*.JPG', '*.png', '*.PNG', '*.jpeg', '*.JPEG',
                 '*.tif', '*.TIF', '*.bmp', '*.BMP')
    imagetypes = "*.jpg;*.JPG;*.png;*.PNG;*.jpeg;*.JPEG;"
    imagetypes += "*.tif;*.TIF;*.bmp;*.BMP"
    #Functions.xmlreset() #  uncomment this if you break your xml bad, yo
    #for i in struct_elem_values:
        #print Errors.check_structure(str(i))
    app = App(0)
    app.MainLoop()


if __name__ == '__main__':
    main()
