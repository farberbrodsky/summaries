import os
import sys
from shutil import rmtree, copyfile
from jinja2 import Template
import htmlmin

# remove all pdf files
for root, dirs, files in os.walk("."):
    if not root.startswith("./.git"):
        for filename in files:
            if filename.endswith(".pdf"):
                # found a pdf file, remove it
                path = os.path.join(root, filename)
                print("removing", path)
                os.remove(path)

# compile all lyx files
pdf_files = []
for root, dirs, files in os.walk("."):
    if not root.startswith("./.git"):
        for filename in files:
            if filename.endswith(".lyx"):
                # found a lyx file, compile it
                place = os.path.join(root, filename)
                print("compiling", place)
                if os.popen(f"cd {root} && lyx --export pdf2 {filename} && lyx --export xhtml {filename}").close() != None:
                    print("Error in compilation")
                    sys.exit()
                pdf_files.append(place[1:-4])
print("finished compiling LyX")

# generate pages
# pdf_files is ['/discrete-mathematics/ultimate-summary-misha/summary', '/intro-to-computer-science/dutz-misha/dutz', '/B/sikum']
pdf_directories = {}
for file_name in pdf_files:
    curr_dir = pdf_directories
    slashed = file_name[1:].split('/')
    for dir_name in slashed[:-1]:
        if dir_name not in curr_dir:
            curr_dir[dir_name] = {}
        curr_dir = curr_dir[dir_name]
    if not "files" in curr_dir:
        curr_dir["files"] = []
    
    curr_dir["files"].append(slashed[-1])

# pdf_directories is {'discrete-mathematics': {'ultimate-summary-misha': {'files': ['summary']}}, 'intro-to-computer-science': {'dutz-misha': {'files': ['dutz']}}, 'B': {'files': ['sikum']}}

folder_template = None
with open("./website/folder.jinja2", "r") as folder_template_file:
    folder_template = Template(folder_template_file.read())
file_template = None
with open("./website/file.jinja2", "r") as file_template_file:
    file_template = Template(file_template_file.read())

try:
    rmtree("./docs")
except:
    pass
os.popen("cp -r ./website/public ./docs").close()

# Copy PDF files to website
for pdf_file in pdf_files:
    try:
        os.makedirs("./docs" + "/".join(pdf_file.split("/")[:-1]))
        print("mkdir", "./docs" + "/".join(pdf_file.split("/")[:-1]))
    except:
        pass
    copyfile("." + pdf_file + ".pdf", "./docs" + pdf_file + ".pdf")
    copyfile("." + pdf_file + ".xhtml", "./docs" + pdf_file + ".xhtml")
    print("copy", "." + pdf_file + ".xhtml", "to", "./docs" + pdf_file + ".xhtml")

def make_website_recursively(dirs, where):
    _keys = list(sorted(dirs.items(), key=lambda x: x[0]))
    subdirs = [(k, v) for k, v in _keys if not (type(v) is list)]
    files = [v for k, v in _keys if type(v) is list]
    files = [y for x in files for y in x] # flatten

    try:
        os.makedirs("./docs/" + where)
    except:
        pass

    with open("./docs/" + where + "index.html", "w") as my_file:
        entries = [('dir', x[0]) for x in subdirs] + [('file', x) for x in files]
        # Make a page for the directory
        my_file.write(htmlmin.minify(folder_template.render(dirname="/" + where, entries=entries)))
    # Make a page for each file
    for filename in files:
        with open("./docs/" + where + filename + ".html", "w") as my_file:
            # Make a page for the file
            try:
                with open("./docs/" + where + filename + ".xhtml", "r") as lyxhtml_file:
                    lyxhtml = lyxhtml_file.read()
                    print("found", lyxhtml.find("<body dir=\"auto\">"), lyxhtml.find("</body>"))
                    lyxhtml = lyxhtml[(lyxhtml.find("<body dir=\"auto\">") + 17):(lyxhtml.find("</body>"))]
                    my_file.write(htmlmin.minify(file_template.render(filename="/" + where + filename, lyxhtml=lyxhtml)))
            except:
                pass


    for k, v in subdirs:
        make_website_recursively(v, where + k + "/")

make_website_recursively(pdf_directories, "")
print("generated website")
print("done")
