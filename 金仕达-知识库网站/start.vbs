Set shell = CreateObject("WScript.Shell")
shell.CurrentDirectory = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
shell.Run "cmd /c mkdocs serve --dev-addr localhost:8899", 0, False
WScript.Echo "Knowledge Base started!" & vbCrLf & vbCrLf & "Open browser: http://localhost:8899" & vbCrLf & "Run stop.bat to shut down."
