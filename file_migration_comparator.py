import os
import difflib
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from html import escape
import webbrowser

def generate_side_by_side_diff(before_lines, after_lines):
    differ = difflib.SequenceMatcher(None, before_lines, after_lines)
    table = ['<table class="diff">']
    table.append('<tr><th>Base #</th><th>Base</th><th>Search #</th><th>Search</th></tr>')

    i1 = j1 = 1
    for tag, i1_start, i1_end, j1_start, j1_end in differ.get_opcodes():
        for i in range(max(i1_end - i1_start, j1_end - j1_start)):
            left_line = escape(before_lines[i1_start + i] if i1_start + i < i1_end else '')
            right_line = escape(after_lines[j1_start + i] if j1_start + i < j1_end else '')
            left_num = i1_start + i + 1 if i1_start + i < i1_end else ''
            right_num = j1_start + i + 1 if j1_start + i < j1_end else ''

            row_class = ''
            if tag == 'replace':
                row_class = 'replace'
            elif tag == 'delete':
                row_class = 'delete'
                right_line = ''
                right_num = ''
            elif tag == 'insert':
                row_class = 'insert'
                left_line = ''
                left_num = ''
            else:
                row_class = 'equal'

            table.append(f'<tr class="{row_class}"><td>{left_num}</td><td>{left_line}</td>'
                         f'<td>{right_num}</td><td>{right_line}</td></tr>')
    table.append('</table>')
    return '\n'.join(table)

def find_matching_file(search_dir, relative_path):
    candidate = search_dir / relative_path
    if candidate.exists():
        return candidate

    matches = list(search_dir.glob(f'**/{relative_path.name}'))
    return matches[0] if matches else None

def generate_report(base_dir, search_dir, output_file):
    base_dir = Path(base_dir)
    search_dir = Path(search_dir)
    output_path = Path(output_file)

    total_files = matched_files = changed_files = missing_files = 0
    missing_file_paths = []
    unchanged_file_paths = []

    report = [
        '<html><head><style>',
        'body { font-family: Arial; }',
        'table.diff { width: 100%; border-collapse: collapse; font-family: monospace; }',
        'table.diff td, table.diff th { border: 1px solid #ccc; padding: 4px; vertical-align: top; }',
        'tr.insert td { background-color: #ddffdd; }',
        'tr.delete td { background-color: #ffdddd; }',
        'tr.replace td { background-color: #ffffcc; }',
        'summary { cursor: pointer; font-weight: bold; margin-top: 10px; }',
        '</style></head><body>'
    ]
    report.append(f"<h1>Migration Comparison Report</h1>")
    report.append(f"<p><strong>Base Folder:</strong> {base_dir}<br><strong>Search Folder:</strong> {search_dir}</p><hr>")

    report_body = []

    for root, _, files in os.walk(base_dir):
        for file in files:
            total_files += 1
            base_file = Path(root) / file
            rel_path = base_file.relative_to(base_dir)
            search_file = find_matching_file(search_dir, rel_path)

            section = [f"<details><summary>{escape(str(rel_path))}</summary>"]

            if not search_file or not search_file.exists():
                section.append("<p style='color:red;'>Missing in Search Folder.</p></details>")
                report_body.append(''.join(section))
                missing_file_paths.append(str(rel_path))
                missing_files += 1
                continue

            try:
                with open(base_file, 'r', encoding='utf-8', errors='ignore') as f1, \
                     open(search_file, 'r', encoding='utf-8', errors='ignore') as f2:
                    base_lines = f1.readlines()
                    search_lines = f2.readlines()

                if base_lines == search_lines:
                    section.append("<p style='color:green;'>No changes.</p></details>")
                    unchanged_file_paths.append(str(rel_path))
                    matched_files += 1
                else:
                    diff_html = generate_side_by_side_diff(base_lines, search_lines)
                    section.append(diff_html + "</details>")
                    changed_files += 1
            except Exception as e:
                section.append(f"<p>Error comparing file {rel_path}: {str(e)}</p></details>")

            report_body.append('\n'.join(section))

    # Summary block
    report.append("<h2>Summary</h2>")
    report.append(f"<ul>"
                  f"<li>Total files compared: {total_files}</li>"
                  f"<li>Files unchanged: {matched_files}</li>"
                  f"<li>Files changed: {changed_files}</li>"
                  f"<li>Files missing in Search Folder: {missing_files}</li>"
                  f"</ul>")

    # List unchanged files
    if unchanged_file_paths:
        report.append("<details><summary>Unchanged Files</summary><ul>")
        for path in unchanged_file_paths:
            report.append(f"<li>{escape(path)}</li>")
        report.append("</ul></details>")

    # List missing files
    if missing_file_paths:
        report.append("<details><summary>Missing Files in Search Folder</summary><ul>")
        for path in missing_file_paths:
            report.append(f"<li>{escape(path)}</li>")
        report.append("</ul></details>")

    report.append("<hr>")
    report.extend(report_body)
    report.append('</body></html>')

        # Collect all base and search files for cross-reference
    base_files_set = set()
    for root, _, files in os.walk(base_dir):
        for file in files:
            rel_path = Path(root).joinpath(file).relative_to(base_dir)
            base_files_set.add(rel_path)

    search_files_set = set()
    for root, _, files in os.walk(search_dir):
        for file in files:
            rel_path = Path(root).joinpath(file).relative_to(search_dir)
            search_files_set.add(rel_path)

    extra_files_in_search = sorted(search_files_set - base_files_set)

    # Add extra files section
    if extra_files_in_search:
        report.append("<details><summary>Extra Files in Search Folder (not in Base Folder)</summary><ul>")
        for path in extra_files_in_search:
            report.append(f"<li>{escape(str(path))}</li>")
        report.append("</ul></details>")


    with open(output_path, 'w', encoding='utf-8') as out:
        out.write('\n'.join(report))

    return output_path


# --- GUI Class ---
class MigrationComparerApp:
    def __init__(self, master):
        self.master = master
        master.title("File Migration Comparator")

        self.base_label = tk.Label(master, text="Base Folder:")
        self.base_entry = tk.Entry(master, width=60)
        self.base_button = tk.Button(master, text="Browse", command=self.browse_base)

        self.search_label = tk.Label(master, text="Search Folder:")
        self.search_entry = tk.Entry(master, width=60)
        self.search_button = tk.Button(master, text="Browse", command=self.browse_search)

        self.output_label = tk.Label(master, text="Output HTML File:")
        self.output_entry = tk.Entry(master, width=60)
        self.output_button = tk.Button(master, text="Browse", command=self.browse_output)

        self.run_button = tk.Button(master, text="Generate Report", command=self.run_comparison)

        self.base_label.grid(row=0, column=0, sticky="w")
        self.base_entry.grid(row=0, column=1)
        self.base_button.grid(row=0, column=2)

        self.search_label.grid(row=1, column=0, sticky="w")
        self.search_entry.grid(row=1, column=1)
        self.search_button.grid(row=1, column=2)

        self.output_label.grid(row=2, column=0, sticky="w")
        self.output_entry.grid(row=2, column=1)
        self.output_button.grid(row=2, column=2)

        self.run_button.grid(row=3, column=1, pady=10)

    def browse_base(self):
        path = filedialog.askdirectory()
        if path:
            self.base_entry.delete(0, tk.END)
            self.base_entry.insert(0, path)

    def browse_search(self):
        path = filedialog.askdirectory()
        if path:
            self.search_entry.delete(0, tk.END)
            self.search_entry.insert(0, path)

    def browse_output(self):
        path = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML files", "*.html")])
        if path:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, path)

    def run_comparison(self):
        base_path = self.base_entry.get()
        search_path = self.search_entry.get()
        output_file = self.output_entry.get()

        if not all([base_path, search_path, output_file]):
            messagebox.showerror("Missing Input", "Please provide all three paths.")
            return

        try:
            result_path = generate_report(base_path, search_path, output_file)
            messagebox.showinfo("Success", f"Report generated at:\n{result_path}")
            webbrowser.open(f"file://{result_path.resolve()}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

# --- Run GUI ---
if __name__ == "__main__":
    root = tk.Tk()
    app = MigrationComparerApp(root)
    root.mainloop()
