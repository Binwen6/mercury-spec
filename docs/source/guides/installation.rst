Installation
============

This guide describes how to install |project_name| and its Python binding.

Overview
--------

To make |project_name| work with a certain programming language, there are three things needed:

1. An installation of the |project_name| specification,
   which is nothing more than a directory containing a bunch of files.
2. A **binding** for the language from which you will be using |project_name|.
   Currently, the only language supported is **Python**.
3. A model collection directory which contains all the installed |project_name| extensions.
   Basically, an extension is an "addon" which allows |project_name| to identify and use
   a deep learning model that is available on your platform.
4. Configure the binding so that it knows where to look for the specification / extensions.

Installing the |project_name| Specification
-------------------------------------------

To "install" the specification, just copy the folder containing the specification files to wherever you like.
Currently, to obtain the specification files, you need to clone the |project_name| GitHub repo:

.. code-block:: bash

    git clone https://github.com/Trent-Fellbootman/mercury.git

Then, locate the folder containing the specification in the cloned repo,
which is `<path-to-cloned-repo>/mercury/spec/src`. Copy this folder to wherever you like and the installation is complete.
For example:

.. code-block:: bash

    cp -r mercury/mercury/spec/src ~/mercury

Installing the Python Binding
-----------------------------

The specification itself does not do much; it is just a collection of XML files specifying the expected behavior of deep learning models.
To actually use |project_name| from a programming language, you need a **binding** for that language.

Currently, the only officially supported language is Python; you can easily install the Python binding using pip:

.. code-block:: bash

    pip install -i https://test.pypi.org/simple/ mercury-nn

Notice that there is only a test release currently, so we are using the TestPyPI index instead of PyPI.

Another thing to notice is that the lowest version of Python that |project_name| officially supports is **Python 3.11**.

You might be unable to automatically install the dependencies when executing the above command
(e.g., there is an error saying something like "cannot find a compatible version of lxml").
This is probably because TestPyPI does not contain releases for the dependencies.
In this case, just install the dependencies manually (currently, the only dependency is lxml >= 4.9.2, <5.0.0):

.. code-block:: bash

    pip install 'lxml >=4.9.2, <5.0.0'

Then, reinstall the Python binding package and everything should go smoothly:

.. code-block:: bash

    pip install -i https://test.pypi.org/simple/ mercury-nn

Adding a Model Collection Directory
-----------------------------------

The final step is to create a model collection directory which will home all the models that |project_name| can find and use.
When you install new models later, they are also installed to this directory.

You can place the model collection directory wherever you like, e.g.:

.. code-block:: bash
    
    mkdir ~/mercury-extensions

.. _sample-extensions-installation:

If you want some predefined models to start with (so that you will be able to use those models in |project_name|),
there are extensions for GPT-3.5 Turbo (i.e., ChatGPT) and DALL E developed for demonstration purposes in the |project_name| GitHub repository,
under `<path-to-cloned-repo>/sample-model-collection/openai`.
To install the extension, copy the extension folder to your model collection directory, e.g.:

.. code-block:: bash

    cp -r <path-to-cloned-repo>/sample-model-collection/openai ~/mercury-extensions

Notice that the Python implementations for the extensions require `openai`, `pillow`, and `numpy` to work.

The procedure above which installs the ChatGPT extension is also applicable to other extensions.
Generally, an extension is just a folder containing a bunch of files (which typically includes a `manifest.xml` at top-level),
and all you need to do to install an extension is to copy that folder to your model collection directory.

Configuring the Binding
-----------------------

The final step is to configure the binding so that it knows where to find the specification and the extensions.
This can differ depending on the language you are installing the binding for.

Python
######

For the Python binding, you need to specify the directory where you installed |project_name| to
(this should typically contain the following folders at top-level: `filters`, `match-filter` and `valid-usage`),
as well as the model collection directory in a Python file.

To locate the exact file in which you should set those directories,
try to import mercury in your Python interpreter and see the error message emitted.

Testing the Installation
------------------------

Now that you have installed all the required components of |project_name|,
you can test whether your installation is correct by trying to use |project_name|.

As an example, for the Python, you can try to list the names of all available models in your model collection directory:

.. code-block:: python

    import mercury_nn as mc


    model_entries = mc.enumerateAvailableModels()

    print([mc.MetadataUtils.getModelName(entry.metadata) for entry in model_entries])

Additionally, check that the the manifest files of the extensions are valid to make sure that the specification directory is configured correctly:

.. code-block:: python

    from lxml import etree as ET
    from mercury_nn import manifest_validation


    base_model_filter = mc.Filter.fromXMLElement(ET.parse(mc.config.Config.baseModelFilterPath).getroot())

    for entry in model_entries:
        assert manifest_validation.checkSyntax(entry.metadata).isValid
        assert mc.filtering.matchFilter(base_model_filter, entry.metadata).isSuccess
