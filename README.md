![GitHub Workflow Status](https://img.shields.io/github/workflow/status/andrust/git-gerrit/Static-analysis?label=Static-analysis%20status)
![PyPI](https://img.shields.io/pypi/v/gerrit-tui)
# git-gerrit

Console UI for Gerrit CodeReview.
Lots of gerrit functionalities supported like:

- submitting commit
- commenting
- give score
- submit
- etc.

![Gerrit dashboard](docs/git-gerrit.png "Home dashboard")

## Usage

Prerequisits:

- A text editor (now only vim supported)
- git
- Python3 installed
- Pip packages:
    - urwid
    - requests
    - python-dateutil

After installing required packages just run git-gerrit:

```
./git-gerrit.sh
```

### Using Docker based solution

Clone the repository and run the following command to build the environment:

```
docker build -t git-gerrit .
```

After this just run the image with the repo mounted inside:


```
docker run -it --rm -v /path/to/repo:/repo git-gerrit
```

You will get a shell where you have everything what needs for git-gerrit.

### Install it from pypi

To install gerrit-tui just run:

```
pip install gerrit-tui
```

and run it with:

```
gerrit-tui
```

## Contribute

Before contribution please read the [CONTRIBUTING.md](CONTRIBUTING.md)
