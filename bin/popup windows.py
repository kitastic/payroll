import PySimpleGUI as psg
text = psg.popup_get_text('Enter your name', title="Textbox")
print ("You entered: ", text)
file=psg.popup_get_file('Select a file',  title="File selector")
print ("File selected", file)
folder=psg.popup_get_folder('Get folder', title="Folder selector")
print ("Folder selected",folder)
ch = psg.popup_yes_no("Do you want to Continue?",  title="YesNo")
print ("You clicked", ch)
ch = psg.popup_ok_cancel("Press Ok to proceed", "Press cancel to stop",  title="OkCancel")
if ch=="OK":
   print ("You pressed OK")
if ch=="Cancel":
   print ("You pressed Cancel")
psg.popup_no_buttons('You pressed', ch, non_blocking=True)
psg.popup_auto_close('This window will Autoclose')