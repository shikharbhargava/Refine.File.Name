import _winreg

def define_action_on(filetype, registry_title, command, title=None):
    """
    define_action_on(filetype, registry_title, command, title=None)
        filetype: either an extension type (ex. ".txt") or one of the special values ("*" or "Directory"). Note that "*" is files only--if you'd like everything to have your action, it must be defined under "*" and "Directory"
        registry_title: the title of the subkey, not important, but probably ought to be relevant. If title=None, this is the text that will show up in the context menu.
    """
    #all these opens/creates might not be the most efficient way to do it, but it was the best I could do safely, without assuming any keys were defined.
    reg = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, "Software\\Classes", 0, _winreg.KEY_SET_VALUE)
    k1 = _winreg.CreateKey(reg, filetype) #handily, this won't delete a key if it's already there.
    k2 = _winreg.CreateKey(k1, "shell")
    k3 = _winreg.CreateKey(k2, registry_title)
    k4 = _winreg.CreateKey(k3, "command")
    if title != None:
        _winreg.SetValueEx(k3, None, 0, _winreg.REG_SZ, title)
    _winreg.SetValueEx(k4, None, 0, _winreg.REG_SZ, command)
    _winreg.CloseKey(k3)
    _winreg.CloseKey(k2)
    _winreg.CloseKey(k1)
    _winreg.CloseKey(reg)

if __name__ == "__main__":
    define_action_on("*", "UndoByRenameScript", "\"C:\\Python27\\python.exe\" \"C:\\RenameFiles\\rename.series.episode.py\" -U -i \"%1\"", "Undo Files Name, Renamed by Rename Script")
    define_action_on("*", "UndoByRenameScriptByForce", "\"C:\\Python27\\pythonw.exe\" \"C:\\RenameFiles\\rename.series.episode.py\" -U -F -i \"%1\"", "Undo Files Name, Renamed by Rename Script by Force")
    #define_action_on("Directory", "RenameByRenameScriptByForce", "\"C:\\Python27\\pythonw.exe\" \"C:\\RenameFiles\\rename.series.episode.py\" -F -d \"%1\"", "Rename MKV Files by Rename Script by Force")
    #define_action_on("Directory", "RenameByRenameScriptByForceRecursively", "\"C:\\Python27\\pythonw.exe\" \"C:\\RenameFiles\\rename.series.episode.py\" -FR -d \"%1\"", "Rename MKV Files by Rename Script by Force Recursively")