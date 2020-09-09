import os
import sys

# remove all pdf files
for root, dirs, files in os.walk('.'):
    if not root.startswith("./.git"):
        for filename in files:
            if filename.endswith(".pdf"):
                # found a pdf file, remove it
                path = os.path.join(root, filename)
                print("removing", path)
                os.remove(path)

# compile all lyx files
for root, dirs, files in os.walk('.'):
    if not root.startswith("./.git"):
        for filename in files:
            if filename.endswith(".lyx"):
                # found a lyx file, compile it
                print("compiling", os.path.join(root, filename))
                if os.popen("cd " + root + " && lyx --export pdf2 " + filename).close() != None:
                    print("Error in compilation")
                    sys.exit()
print("done")

