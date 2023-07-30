Developing a Model Extension for |project_name|
===============================================

This tutorial describes how to make an extension for |project_name|
so that |project_name| supports using your model.

What is a |project_name| Model Extension?
-----------------------------------------

If you have read the :doc:`introduction </guides/introduction>` or the :doc:`getting-started tutorial </guides/getting-started>`,
you should know that |project_name| decides which model to use on the user's platform at run-time, instead of develop time.

How does |project_name| find the available models on a platform?
Well, applications developed with |project_name| can only run on platforms with a |project_name| runtime installation (obviously),
and the |project_name| installation includes a "model collection directory" which contains a variety of **Mercury Model Extensions**;
each extension represents a compatible model that |project_name| can find and use when running an application.

In general, a **Mercury Model Extension** is an extension that wraps a deep neural network service
(whether deployed locally or remotely) and makes it compatible with the |project_name| specification,
allowing |project_name| to include it when enumerating available models and instantiate it for use in application at run-time.

Creating an Extension
------------------------------

The Manifest File
#################

Each extension must include a manifest file named `manifest.xml` in the extension root directory.
This manifest file is what allows |project_name| to identify the corresponding model
and assess whether it meets the requirements of a particular application at run-time.

Such a manifest file contains the metadata of the model, such as name, type, author, etc.
The most important information it provides are:

- The call scheme of the model (i.e., what the model expects as input and returns as output)
- The capabilities of the model (i.e., the special abilities of the model, such as the ability to solve calculus problems of a chat completion model)
- The interface to call the model from different programming languages.
- Other important parameters. One example is the price per model invokation (or per token for a language model like ChatGPT).

The manifest file must follow a specific structure defined by the |project_name| specification.
The easiest way to write a such a manifest is to use a template and modify the fields according to the model for which you are developing the extension.
An example template is provided below:

.. literalinclude:: /res/manifest-template.xml
    :language: xml

Notice that the "capabilities" are specified as the keys of a `dict`, instead of a list.
This is because the |project_name| specification specifies `list` elements to be **ordered** arrays,
and as a result, the semantics of the capabilities would change as the order of the capabilities changes if we use a `list`.
If we use a `dict`, however, the order doesn't matter.
Additionally, a `dict` element requires each child to be a `named-field` element representing a key-value pair which must have exactly one child representing the value.
Even though we are only using keys here, we still must specify a child for each `named-field`.
In the |project_name| specification, such a "dummy child" is **required** to be an empty string denoted by `<string/>`.

It is recommended that you make sure the manifest is valid before publishing your |project_name| model extension.
For example, you can use a developer tool like :ref:`mercury-dev-tool <mercury-dev-tool-reference>`.

Language-Specific Implementations
#################################

Syntactically, a `manifest.xml` is all it takes to make a valid extension.
However, to allow |project_name| to instantiate and call your model in a particular programming language,
you must also define the **implementation** for that language.
|project_name| is, in essence, a language-independent specification;
however, there are **bindings** for multiple programming languages.
A **binding** is an interface between |project_name| and a programming language which allows you to use |project_name| in that language.
Typically, an **implementation** would include startup scripts, library files or model weights (for locally-deployed models),
and `manifest.xml` provides metadata about the implementation, such as file locations.

**# TODO: write a guide for implementing an extension for each supported language**

Since different languages have different working mechanisms (especially between compiled and interpreted languages),
what is required to make your model work with |project_name| can be quite different among them.
For simplicity, this tutorial describes how to make a Python implementation.
For the specifics of creating an implementation for each supported language, see the user guide.

The Python Implementation
~~~~~~~~~~~~~~~~~~~~~~~~~

To create an implementation for Python, you need to subclass the `Model` class provided by the |project_name| Python binding.
This is the "startup class" whose constructor is called to instantiate a callable instance of your model.
To define the exact process of calling your model, you must override the `call` method,
which is expected to take some input, feed it to your model, and return the model's output.
The important thing to notice is that **the input and output types of the `call` method
must match those specified in the manifest file**.

As an example, a possible Python implementation for ChatGPT could be:

.. literalinclude:: /../../sample-model-collection/openai/chatgpt/model.py

The corresponding input / output type declaration in the manifest file is as follows:

.. code-block:: xml

    ...

    <named-field name="input">
        <dict>
            <named-field name="type">
                <type-declaration>
                    <type-list>
                    <!-- `list-type` is a variable-length type. The element inside a `list-type` is interpreted -->
                    <!-- as the type of each element. -->
                        <type-tuple>
                            <type-string/>
                            <type-bool/>
                        </type-tuple>
                    </type-list>
                </type-declaration>
            </named-field>
            <named-field name="description">
                <string>An list of chat messages. The first element of the tuple is the content, the second being true if the message is user-sent, false if bot-sent.</string>
            </named-field>
        </dict>
    </named-field>
    <named-field name="output">
        <dict>
            <named-field name="type">
                <type-declaration>
                    <type-string/>
                </type-declaration>
            </named-field>
            <named-field name="description">
                <string>The next bot-sent message.</string>
            </named-field>
        </dict>
    </named-field>

    ...

There are two additional things to notice in the above example.

First, the name of the "entry class" which subclasses `mecury.Model` is "Model".
How does |project_name| know that this is the class from which the callable instance can be created?
Well, you specify that information also in the manifest file.
In the manifest, you would need to specify which file contains the "startup class",
as well as the name of the "startup class" in that file.
When the model is instantiated at runtime,
|project_name| looks at the manifest, locates and loads the Python script that contains the "startup class",
and calls the constructor of that class to create a callable instance.
This instance is the handle that the application retrieves at run-time;
when an application calls your model through that handle,
the `call` method that you have overriden is called.
This is how the Python implementation works at run-time.

The implementation field of the manifest file of the sample model above might look like the following:

.. code-block:: xml

    <named-field name="implementations">
        <dict>
            <named-field name="Python">
                <dict>
                    <named-field name="entryFile">
                        <string>model.py</string>
                    </named-field>
                    <named-field name="entryClass">
                        <string>Model</string>
                    </named-field>
                </dict>
            </named-field>
        </dict>
    </named-field>

As we can see, the "startup script" is specified as "model.py",
and the "startup class" is specified as "Model" (as defined in the Python script).

The completed extension for this sample model should have a file structure hierarchy like the following:

.. code-block::

    - <extensionRootFolder>
        - manifest.xml
        - model.py

As long as your Python implementation is valid and matches your manifest file,
|project_name| should be able to find and instantiate your model correctly at run-time
(provided that the run-time platform has installed your extension in the model collection directory).

Summary
-------

Congratulations! In this tutorial, you have learned how to create a |project_name| Model Extension
and allow |project_name| to use your model.