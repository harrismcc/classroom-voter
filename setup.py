import setuptools, os


with open("README.md", "r") as fh:
    long_description = fh.read()



def saveVersion(version):
    with open("version.txt", "w") as f:
        f.write(version)

def getLastVersion():
    with open("version.txt", "r") as f:
        oldVersion = f.read()

    return oldVersion

def getBuildNumber():
    stream = os.popen('git log master --pretty=oneline | wc -l')
    out = stream.read().rstrip()
    return out

def getNewVersion():
    lastVersion = getLastVersion()
    split = lastVersion.split(".")
    
    if len(split) == 4:
        #Then there is a build number
        split[3] = getBuildNumber()
    
    out = ".".join(split)
    saveVersion(out)

    return out

setuptools.setup(
    name="classroom-voter", # Replace with your own username
    version=getNewVersion(),
    author="Harris McCullers, Jay Rodolitz, Douglas Webster, Ishaan Gandhi",
    author_email="harrismcc+classroom-voter@gmail.com",
    description="A secure CLI classroom polling system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/harrismcc/classroom-voter",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'pycryptodome',
        'pycryptodomex'
    ]   
)