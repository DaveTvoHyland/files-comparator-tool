# 🔍 File Migration Comparator

**File Migration Comparator** is a standalone Python tool with a simple GUI that compares files between two folders (before and after migration). It generates a clean, interactive HTML report that highlights file changes just like GitHub Pull Requests do.

## 🚀 Features

- ✅ GUI-based (Tkinter): No CLI needed
- ✅ Deep comparison of files in subfolders
- ✅ Syntax-highlighted, side-by-side HTML report
- ✅ Collapse/expand each file's comparison
- ✅ Summary includes:
  - Unchanged files
  - Changed files
  - Missing files (in Search folder)
  - Extra files (new in Search folder)
- ✅ Opens the report automatically in your browser

---

## 📂 How It Works

### **Inputs via GUI:**
1. **Base Folder** – the folder before migration
2. **Search Folder** – the folder after migration
3. **Output File** – path to save the generated HTML report

The tool recursively compares all files from Base Folder with Search Folder.

---

## 🖥️ Using the Tool
Open 
A GUI window will open. Select:
1. Base Folder (preferable after migration)
2. Search Folder (preferable before migration)
3. Output file path (e.g. report.html)
4. The comparison will run, and the resulting report will open in your browser.
5. Exampled results:
   
![image](https://github.com/user-attachments/assets/b53b6ce1-0411-4ec3-8288-c91ad168f2bb)


### ✅ Run via Python / build standalone application

1. Run via Python (Python 
python files_migration_comparator.py

- 📦 Requirements: Python 3.7+
- Works on Windows (tested), should work on macOS/Linux with Python installed

2. Build a Standalone .exe (No Python Required)

- Install PyInstaller
'pip install pyinstaller'

- Build the Executable
From the same folder as your script:
'pyinstaller --onefile --windowed files_migration_comparator.py'
- Find Your Executable
Your .exe will be in the dist/ folder:
dist/files_migration_comparator.exe
