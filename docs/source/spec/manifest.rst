Manifest Syntax Specification
=============================

In |project_name|, the behavior of deep learning models are defined in a language-independent way by manifests,
which are XML files that must follow a set of predefined rules.
The information in a manifest are organized into a hierarchy of typed elements,
by using "compositor" XML elements defined in the |project_name| specification,
such as dictionaries, lists and tuples.
The "type" of an XML element is just its tag.

The manifest syntax can be further divided into two sets of syntactical rules.
One of them is called **data syntax**, which defines how the parameters of the model,
(such as name, publisher, cost per invocation, publishment date, etc.) should be specified;
the other is called **type declaration syntax**, which is used to define the types of the model's input & output
(e.g., for an image classification model, the input type is an image, and the output type is a class).

Next, we describe the details of the data and type declaration syntaxes.

Data Syntax
-----------

Currently, there are 2 types of compositor elements,
which are used to organize data into a hierarchy,
as well as 5 types of "primitive" elements,
which are typically used to define concrete data
and are considered "leaves" in a data syntax hierarchy.

It is worth noting that a type declaration element is considered a leaf in the data syntax hierarchy,
but root in a type declaration hierarchy.

Compositor Elements
...................

dict
####

A `dict` element represents a collection of key-value pairs,
where each pair corresponds to a child element tagged `named-field`;
it is illegal for a `dict` to have a direct child whose tag is not `named-field`.

Each `named-field` element must have a `name` attribute, whose value corresponds to its key in the `dict`.

**Valid Example**:

.. code-block:: xml

    <dict>
        <named-field name="key1">
            <string>value1</string>
        </named-field>

        <named-field name="key2">
            <int>1</int>
        </named-field>
    </dict>

The above `dict` is equivalent to `{ "key1": "value1", "key2": 1 }` in JSON.

**Invalid Examples**:

.. code-block:: xml

    <dict>
        <named-field>
            <string>value1</string>
        </named-field>

        <named-field name="key2">
            <int>1</int>
        </named-field>
    </dict>

The above XML is invalid because a `named-field` must have a `name` attribute.

.. code-block:: xml

    <dict>
        <list>
            <string>value1</string>
        </list>

        <named-field name="key2">
            <int>1</int>
        </named-field>
    </dict>

The above XML is invalid because the direct children of a `dict` **must** all be `named-field`.

list
####

A `list` element represents an array of elements.
Each child element in a `list` is considered an element in the array.

Notice that an empty `list` is also legal.

**Valid Example**

.. code-block:: xml

    <list>
        <string>element1</string>
        <string>element2</string>
    </list>

In JSON, the above `list` element is equivalent to `["element1", "element2"]`.

**Invalid Example**

.. code-block:: xml

    <list>
        <named-value>
            <string>value1</string>
        </named-value>
    </list>

The above code is illegal because a `named-value` can only be used as a direct child of a `dict`.

Primitive Elements
..................

string
######

A `string` element represents a string whose value corresponds to the text enclosed between the start and end tags.
A `string` **must** have no children.

**Example**

.. code-block:: xml

    <string>test</string>

The above `string` element is equivalent to "test" in JSON.

bool
####

A `bool` element represents a bool whose value corresponds to the text enclosed between the start and end tags.
A `bool` **must** have no children.

**Example**

.. code-block:: xml

    <bool>true</bool>

The above `bool` element is equivalent to `true` in JSON.

int
###

A `int` element represents a int whose value corresponds to the text enclosed between the start and end tags.
A `int` **must** have no children.

**Example**

.. code-block:: xml

    <int>1</int>

The above `int` element is equivalent to `1` in JSON.

float
#####

A `float` element represents a float whose value corresponds to the text enclosed between the start and end tags.
A `float` **must** have no children.

**Example**

.. code-block:: xml

    <float>0.5</float>

The above `float` element is equivalent to `0.5` in JSON.

type-declaration
################

A `type-declaration` element is the root of a type-declaration hierarchy which defines the input / output type of a model.

See the :ref:`type declaration syntax section <type-declaration-syntax>` for details.

**Example**

.. code-block::

    <type-declaration>
        <type-string/>
    </type-declaration>

.. _type-declaration-syntax:

Type Declaration Syntax
-----------------------

The type declaration elements are also organized into compositor and primitive elements,
which are detailed below.

Notice that the tags of all type declaration elements are prefixed with "type-".

Compositor Elements
...................

type-named-value-collection
###########################

A `type-named-value-collection` represents the type of a collection of key-value pairs.
Each key-value pair corresponds to a child element tagged `type-named-value`
which must have a `name` attribute whose value represents the key.
The child element of that `type-named-value` represents the type of the value in the key-value pair.

**Example**

.. code-block:: xml

    <type-declaration>
        <type-named-value-collection>
            <type-named-value name="key1">
                <type-string>
            </type-named-value>
        </type-named-value-collection>
    </type-declaration>

The above `type-declaration` declares a dictionary with only one key named "key1".

A `type-named-value-collection` is similar to a dictionary, with the crucial difference being that
the set of keys and the types of corresponding values are **immutable**.

For example, if you specify the input type of your model as in the above example,
then passing `{ "key1": 1.5 }`, `{ "key1": "test" }`, `{ "key1": "test", "key2": "test-new" }` are all considered illegal,
because either the set of keys or the types of the values differ;
only a dictionary with exactly one key named "key1" whose corresponding value is a string is considered a legal input.

type-list
#########

A `type-list` declares the type of an array of data elements,
where the length of the list can vary, but the type of all elements are **exactly** the same.

**Example**

.. code-block:: xml

    <type-declaration>
        <list>
            <type-string/>
        </list>
    </type-declaration>

The above example declares a variable-length list of strings;
if you define your model's input like this, then `[]`, `["a"]`, `["a", "b"]` are all considered valid inputs.

Besides the length of `type-list` being variable at run-time, another crucial difference between a `type-list` element and a `list` element is that
a `list` element can have children of different types, while all elements of a `type-list` must have the same type.

type-tuple
##########

A `type-tuple` declares the type of a tuple with a fixed number of elements.
The types of the elements can be different, but the number of the elements is fixed.

**Example**

.. code-block:: xml

    <type-declaration>
        <type-tuple>
            <type-string/>
            <type-float>
        </type-tuple>
    </type-declaration>

Primitive Elements
..................

type-string
###########

A `type-string` declares a placeholder for an integer and **must** have no children or enclosed text.
The recommended practice for writing "terminal types" like `type-string`, `type-int`, `type-float` and `type-bool`
is to use a self-closing XML tag.

**Example**

.. code-block:: xml

    <type-declaration>
        <type-string/>
    </type-declaration>

type-int
########

A `type-int` declares a placeholder for an integer and **must** have no children or enclosed text.
The recommended practice for writing "terminal types" like `type-string`, `type-int`, `type-float` and `type-bool`
is to use a self-closing XML tag.

**Example**

.. code-block:: xml

    <type-declaration>
        <type-int/>
    </type-declaration>

type-float
##########

A `type-float` declares a placeholder for an integer and **must** have no children or enclosed text.
The recommended practice for writing "terminal types" like `type-string`, `type-int`, `type-float` and `type-bool`
is to use a self-closing XML tag.

**Example**

.. code-block:: xml

    <type-declaration>
        <type-float/>
    </type-declaration>

type-bool
##########

A `type-bool` declares a placeholder for an integer and **must** have no children or enclosed text.
The recommended practice for writing "terminal types" like `type-string`, `type-int`, `type-float` and `type-bool`
is to use a self-closing XML tag.

**Example**

.. code-block:: xml

    <type-declaration>
        <type-bool/>
    </type-declaration>

type-tensor
###########

A `type-tensor` declares a placeholder for multi-dimensional array with a fixed shape.
If you are familiar with NumPy, PyTorch or TensorFlow, think of a `type-tensor`
as a `numpy.array`, a `torch.Tensor` or a `tensorflow.Tensor`, with its shape being fixed.

The children of a `type-tensor` **must** all be `dim`.
Such `dim` elements specify the number of axes and the size of each axis (dimension) of the tensor.
The enclosed text in the starting and closing tags of a `dim` specify the size of that dimension;
a `dim` **must** have no child elements.

**Example**

.. code-block:: xml

    <type-declaration>
        <type-tensor>
            <dim>3</dim>
            <dim>4</dim>
            <dim>5</dim>
        </type-tensor>
    </type-declaration>

The above declaration is equivalent to a `numpy.array` with its shape being `(3, 4, 5)`.

The Base Model Filter
---------------------

The data and type declaration syntaxes only define syntactical rules for manifests.
In addition, however, a manifest for a model must also follow a specific structure,
the **base model filter**.

The base model filter is just a filter defined in the |project_name| specification.
The syntax rules for filters are detailed in :doc:`/spec/filter`, but for now,
think of them as structural templates which a filter can either match or not match.
Basically, a filter defines a specific structure for the manifest file.
|project_name| compares a filter to a manifest and determines whether the manifest has a structure compatible to the filter.
When the answer is yes, the manifest is said to **match** the filter; otherwise, we say there is a **match failure**.

As an example, the XML filter below specifies that the manifest must be a dictionary which contains
at least three keys named "key1", "key2" and "key3", and the values corresponding to those keys must be
string, integer and float:

.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <dict>
        <named-field name="key1">
            <string filter="none">
        </named-field>

        <named-field name="key2">
            <int filter="none">
        </named-field>

        <named-field name="key2">
            <float filter="none">
        </named-field>
    </dict>

A base model filter defines the structure that **all** manifests must follow to be considered valid.

The base model filter is for |project_name| 0.0.1 is defined below
(do not try to understand it now; just skim through it and get an idea what this is all about):

.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <!-- The filter is considered to match if the root element matches. -->
    <!-- Tag names are filters themselves, denoting that the respective element's type must be the same as the tag. -->
    <!-- "all" means that all subfilters needs to match. -->
    <!-- Things like "none", "all", etc. have different semantic meanings for different tags. -->
    <dict filter="all">
        <named-field name="specs">
            <dict filter="all">
                <named-field name="header">
                    <dict filter="all">
                        <named-field name="name">
                            <string filter="none"/>
                        </named-field>
                        <named-field name="class">
                            <string filter="none"/>
                        </named-field>
                        <named-field name="description">
                            <string filter="none"/>
                        </named-field>
                    </dict>
                </named-field>
                <named-field name="capabilities">
                    <list filter="none"/>
                </named-field>
                <named-field name="callSpecs">
                    <dict filter="all">
                        <named-field name="callScheme">
                            <string filter="none"/>
                        </named-field>
                        <named-field name="input">
                            <dict filter="all">
                                <named-field name="type">
                                    <type-declaration filter="none"/>
                                </named-field>
                                <named-field name="description">
                                    <string filter="none"/>
                                </named-field>
                            </dict>
                        </named-field>
                        <named-field name="output">
                            <dict filter="all">
                                <named-field name="type">
                                    <type-declaration filter="none"/>
                                </named-field>
                                <named-field name="description">
                                    <string filter="none"/>
                                </named-field>
                            </dict>
                        </named-field>
                    </dict>
                </named-field>
                <named-field name="properties">
                    <dict filter="none"/>
                </named-field>
            </dict>
        </named-field>
        <named-field name="implementations">
            <dict filter="none"/>
        </named-field>
    </dict>

Basically, the above XML form base model filter specifies that:

1. All manifests must include at least two sections at top level, "spec" and "implementations".
   "spec" defines the behavior of the model, and "implementations" specifies how to use the model from different programming languages.
2. The "spec" section must further contain at least 4 sections:
   
   a. The "header" section specifies the model's identity, such as its name,
   class (e.g., whether it is a language model or an image classification model),
   and a brief description.
   b. The "capabilities" section specifies the abilities that the model has.
   For example, if a language model is capable of solving mathematics problems
   and is familiar with programming, this section may include "math" and "code".
   c. The "callSpecs" section specifies how to call the model.
   The "input" field specifies the type of data that the model expects as input and a short description for semantics
   (i.e., the "meaning" of each part of the data);
   the "output" field denotes the type of data that the model will return as output, as well as a short semantics description.
   There are some common schemes for input / output types, such as "string goes in, string comes out" for text continuation models like GPT-3,
   or "image goes in, class goes out" for image classification models like AlexNet.
   If your model uses one of these common schemes, specify that information in the "callScheme" field;
   this would immediately tell the developer how to call your model without having to look at the input / output types.
   Also, when filtering the models, developers would typically select models that implement a certain call scheme,
   instead of specifying the input / output types directly.
   As a result, specifying a call scheme for your model would increase its chance to be used by a developer.
3. The "properties" section allows you to specify additional properties for your model,
   such as price per token, deployment type (local / cloud), and whether your model supports homomorphic encryption
   (a technology that allows a cloud-deployed model to process data in encrypted form,
   which makes a cloud-deployed model as safe as a locally deployed counterpart).
