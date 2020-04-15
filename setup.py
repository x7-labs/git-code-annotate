from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    name='annotator-git', 

    version='7.0.0',  # Required
    description='A tool to annotate/code review git based project',

    long_description=long_description,
    long_description_content_type='text/-xrst',
    #url='https://github.com/pypa/sampleproject',  # Optional
    author='Exset LABS',  # Optional

    # This should be a valid email address corresponding to the author listed
    # above.
    author_email='kees.jongenburger@exset.com', 

    # Classifiers help users find your project by categorizing it.
    #
    # For a list of valid classifiers, see https://pypi.org/classifiers/
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Review Tools',

        # Pick your license as you wish
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],

    keywords='git code-annotation', 

    #package_dir={'': 'annotate'},  # Optional

    # You can just specify package directories manually here if your project is
    # simple. Or you can use find_packages().
    #
    # Alternatively, if you just want to distribute a single Python file, use
    # the `py_modules` argument instead as follows, which will expect a file
    # called `my_module.py` to exist:
    #
    py_modules=["gitcodeannotate","gitcodereport"],
    python_requires='>=3.7',

    install_requires=['unidiff'],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # `pip` to create the appropriate form of executable for the target
    # platform.
    #
    # For example, the following would provide a command called `sample` which
    # executes the function `main` from this package when invoked:
    entry_points={  # Optional
        'console_scripts': [
            'git-code-annotate=gitcodeannotate:main',
            'git-code-report=gitcodereport:main',
        ],
    },

    # List additional URLs that are relevant to your project as a dict.
    #
    # This field corresponds to the "Project-URL" metadata fields:
    # https://packaging.python.org/specifications/core-metadata/#project-url-multiple-use
    #
    # Examples listed include a pattern for specifying where the package tracks
    # issues, where the source is hosted, where to say thanks to the package
    # maintainers, and where to support the project financially. The key is
    # what's used to render the link text on PyPI.
    project_urls={  # Optional
#        'Bug Reports': 'https://github.com/pypa/sampleproject/issues',
#        'Funding': 'https://donate.pypi.org',
#        'Say Thanks!': 'http://saythanks.io/to/example',
        'Source': 'https://github.com/x7-labs/git-code-annotate',
    },
)
