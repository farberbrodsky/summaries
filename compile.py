import os
import sys
import subprocess
from shutil import rmtree, copyfile
from jinja2 import Template
import htmlmin

try:
    os.mkdir("cache")
except:
    pass
try:
    os.mkdir("docs")
except:
    pass

# remove all pdf files except docs
for root, dirs, files in os.walk("."):
    if not root.startswith("./.git") and not root.startswith("./docs"):
        for filename in files:
            if filename.endswith(".pdf"):
                # found a pdf file, remove it
                path = os.path.join(root, filename)
                print("removing", path)
                os.remove(path)

# compile all lyx files
pdf_files = []
used_caches = set()
for root, dirs, files in os.walk("."):
    if not root.startswith("./.git"):
        for filename in files:
            if filename.endswith(".lyx"):
                # found a lyx file, compile it
                place = os.path.join(root, filename)

                # calculate md5 for cache
                print("hasing", place)
                md5_cmd = subprocess.Popen(["/usr/bin/md5sum", filename], cwd=root, stdout=subprocess.PIPE)
                md5 = md5_cmd.communicate()[0].decode("utf-8").split(" ")[0]
                used_caches.add(md5)

                cached = True
                try:
                    cache_path = ""
                    with open("./cache/cache_" + md5, "r") as f:
                        cache_path = f.read()

                    print("cached", place, "at", cache_path)
                    copyfile("./docs" + cache_path, "." + place[1:-4] + ".pdf")
                    pdf_files.append(place[1:-4] + ".pdf")

                except FileNotFoundError:
                    cached = False

                if not cached:
                    print("compiling", place)
                    subprocess.Popen(["/usr/bin/lyx", "--export", "pdf2", filename], cwd=root).communicate()

                    # save to cache
                    with open("./cache/cache_" + md5, "w") as f:
                        f.write(place[1:-4] + ".pdf")

                    pdf_files.append(place[1:-4] + ".pdf")

# remove unused caches
for fname in os.listdir("cache"):
    if not (fname[6:] in used_caches):
        os.remove(os.path.join("./cache/", fname))

# remove docs completely now
rmtree("./docs/")
os.mkdir("docs")

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
    copyfile("." + pdf_file, "./docs" + pdf_file)
    os.remove("." + pdf_file)
    print("copy", "." + pdf_file, "to", "./docs" + pdf_file)

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

    for k, v in subdirs:
        make_website_recursively(v, where + k + "/")

make_website_recursively(pdf_directories, "")
print("generated website")
print("done")
