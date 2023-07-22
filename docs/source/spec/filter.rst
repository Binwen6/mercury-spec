Filter Syntax Specification
===========================

In |project_name|, filters are used by application developers to specify the requirements on deep learning models.
When a model's manifest satisfy all requirements described in a filter, the manifest is said to **match** the filter;
otherwise, we say there is a **match failure**.
At run-time, |project_name| compares the filters defined in the application to all deep learning models available on the user's platform;
only the models that matches the filters are considered to fit the needs of the application.
Then, |project_name| selects one model among them for use in the application, according to some preference defined by the developer, such as price.

Similar to manifests, filters are also written in XML form
(although helper functions which allow developers to construct filters quickly and concisely are often available)
and has a set of similar syntactical rules.
The requirements specified in a filter are organized into a hierarchy of typed elements (similar to manifests),
where each element (called **filter element**) corresponds to an element (called **manifest element**)
at the same position in the manifest which is being matched against.
When a manifest is matched against a filter, the elements are matched recursively,
meaning that the children are matched first,
then the match result of the parent is determined by the match results on the children and the **filter operation** of the parent.

**Filter operation** specifies how the parent's match result is derived from those of its children.
For example, if the parent's filter operation is "none", the parent is considered to match no matter what the children's match results are
(in fact, the parent filter element **must** not have children in this case);
if the parent's filter operation is "all", typically all children are required to match for the parent to be considered match success.
Additionally, the element in the filter and the corresponding element in the manifest must have the same tag,
otherwise the elements are considered not to match (even if the filter operation is `none`).
Except for "auxiliary elements" like `named-field` elements,
every filter element **must** specify its filter operation type in the `filter` attribute.

Next, we detail the types of elements and the available filter operations on each of them.
Similar to manifests, the filter elements are grouped into data elements, which specify requirements on concrete data;
type-declaration elements, which specify requirements on type declarations;
and compositors, which combines several sub-filters into a composition.

For brevity, the `none` filter operation is omitted.
Except for an extremely few, explicitly documented cases, filter operation `none` is always available in all elements described below;
if the filter operation is `none`, the filter element and the corresponding manifest element matches
as long as they are the same type (i.e., they have the same tag).

Data Elements
-------------------

`dict`
......

A `dict` denotes requirements for a collection of key-value pairs.
If the element at the same position in the manifest is not a `dict`, the elements are always considered not to match.

Similar to manifest syntax, all children of a `dict` must be `named-field` elements.

Available Filter Operations
###########################

**all**

In context of a `dict`, the filter operation `all` means that (assuming the corresponding manifest element is also a `dict`)
the `dict` elements in the filter & manifest are considered to match if and only if
every pair of (manifest child element - filter child element) matches.
However, the filter type only requires that the `dict` in the manifest **contains** all keys specified in the filter element;
the manifest element **can** have additional keys.

As an example, if the filter element is:

.. code-block:: xml

    <dict filter="all">
        <named-field name="key1">
            <string filter="none"/>
        </named-field>
    </dict>

Then the following manifest element is considered to match, even though it contains a key that the filter element does not have:

.. code-block:: xml

    <dict>
        <named-field name="another key">
            <int>1</int>
        <named-field>

        <named-field name="key1">
            <string>test</string>
        <named-field>
    </dict>

In contrary, the following manifest element is considered not to match,
because the tag of the value corresponding to "key1" does not match that specified in the filter element, which is `string`:

.. code-block:: xml

    <dict>
        <named-field name="key1">
            <int>1</int>
        </named-field>
    </dict>

`list`
......

A `list` represents requirements for an array of elements which may or may not be the same type.

Available Filter Operations
###########################

**all**

In context of a `list`, filter operation `all` means that every pair of children in the filter and manifest elements must match
for the `list` element in the manifest to match that in the filter.
However, the `list` in the manifest **can** have more elements than that in the filter.

As an example, if the filter element is:

.. code-block:: xml

    <list filter="all">
        <string filter="none"/>
    </list>

Then the following manifest element matches:

.. code-block:: xml

    <list>
        <string>test</string>
        <int>1</int>
    </list>

The following manifest element does not match, because the first element's type is not `string`:

.. code-block:: xml

    <list>
        <int>1</int>
    </list>

`string`, `bool`, `int` and `float`
...................................

"Terminal elements" like `string`, `bool` `int` and `float` represents requirements on a specific value.
All such elements **must** have no children.

Available Filter Operations
###########################

**equals**

`string`, `bool` `int` and `float` all have the **equals** filter operation,
which specifies that the content of the corresponding element
(typically represented in the text enclosed between the starting and closing tags)
in the manifest **must** be equal that of the filter element for them to match.

As an example, if the filter element is:

.. code-block:: xml

    <string filter="equals">test</string>

Then the following manifest element matches:

.. code-block:: xml

    <string>test</string>

The following manifest element does not match:

.. code-block:: xml

    <string>not test</string>

**lt, le, gt, ge**

Besides `equals`, numeric elements (`int` and `float`) also have filter operations for numeric comparisons,
which are `lt` (less than), `le` (less than or equal), `gt` (greater than) and `ge` (greater than or equal).
For example, the `lt` operation specifies that the filter and manifest elements matches only if
the numeric value of the manifest element is less than that of the filter element.
If the filter element is:

.. code-block:: xml

    <int filter="lt">1</int>

Then the following manifest element matches: 

.. code-block:: xml

    <int>0</int>

The following manifest element does not match:

.. code-block:: xml

    <int>1</int>

`le`, `gt` and `ge` works similarly to `lt`.

`type-declaration`
..................

A `type-declaration` defines the requirements on a type declaration.
If the filter operation is `type-match`, the `type-declaration` element **must** have exactly one child
specifying the requirements for the declaration.

Available Filter Operations
###########################

**type-match**

The `type-match` filter operation specifies that the corresponding element in the manifest
must be a type declaration hierarchy that matches the requirements specified in the child element in the filter.
The :ref:`type declaration elements section <type-declaration-elements>` describes the details of
how a type-declaration hierarchy in a manifest and its counterpart in a filter are determined to match or not to match.

As an example, if the filter element is:

.. code-block:: xml

    <type-declaration filter="type-match">
        <type-string filter="none">
    </type-declaration>

Then **only** the following manifest element matches:

.. code-block:: xml

    <type-declaration>
        <type-string/>
    </type-declaration>

.. _type-declaration-elements:

Type Declaration Elements
-------------------------

`type-named-value-collection`
.............................

As in manifest syntax, all children of a `type-named-value-collection` in a filter **must** be `type-named-value` elements.

Available Filter Operations
###########################

**all**

In context of a `type-named-value-collection`, the filter operation `all` means that (assuming the corresponding manifest element is also a `type-named-value-collection`)
the `type-named-value-collection` elements in the filter & manifest are considered to match if and only if
the keys in the filter element and those in the manifest are **exactly the same**,
and for each key, the corresponding child element in the manifest matches that in the filter element.

The thing to notice is that, the filter and manifest elements are considered **not** to match if manifest element contains keys that are not in the filter.

For example, if the filter element is:

.. code-block:: xml

    <type-named-value-collection filter="all">
        <type-named-value name="key1">
            <type-string filter="none"/>
        </type-named-value>
    </type-named-value-collection>

Then **only** the following manifest element matches:

.. code-block:: xml

    <type-named-value-collection>
        <type-named-value name="key1">
            <type-string/>
        </type-named-value>
    </type-named-value-collection>

`type-list`
...........

Available Filter Operations
###########################

**all**

In context of a `type-list`, the filter operation `all` means that (assuming the corresponding manifest element is also a `type-list`)
the `type-list` elements in the filter & manifest are considered to match if and only if
the type declaration of the element in the manifest matches (i.e., satisfies) the requirements specified in the child element of the `list` in the filter
(recall that all elements in a `type-list` **must** have the same type at run-time, whose declaration is specified in the child of the `list` element).

Similar to manifest syntax, the `list` **must** have exactly one child if the filter operation is `all`.

For example, if the filter element is:

.. code-block:: xml

    <type-list filter="all">
        <type-string filter="none"/>
    </type-list>

Then **only** the following manifest element matches:

.. code-block:: xml

    <type-list>
        <type-string/>
    </type-list>

If the filter element is:

.. code-block:: xml

    <type-list filter="all">
        <type-tuple filter="none">
        </type-tuple>
    </type-list>

The the following manifest element matches:

.. code-block:: xml

    <type-list>
        <type-tuple>
            <type-int/>
        </type-tuple>
    </type-list>

The following manifest element also matches:

.. code-block:: xml

    <type-list>
        <type-tuple>
            <type-string/>
            <type-int/>
            <type-tuple>
                <type-bool>
            </type-tuple>
        </type-tuple>
    </type-list>

`type-tuple`
............

Available Filter Operations
###########################

**all**

In context of a `type-tuple`, the filter operation `all` means that (assuming the corresponding manifest element is also a `type-tuple`)
the `type-tuple` elements in the filter & manifest are considered to match if and only if
each child of the `tuple` element in the manifest matches its counterpart in the filter.

For example, if the filter element is:

.. code-block:: xml

    <type-tuple filter="all">
        <type-string filter="none"/>
        <type-bool filter="none">
    </type-tuple>

Then **only** the following manifest element matches:

.. code-block:: xml

    <type-tuple>
        <type-string/>
        <type-bool/>
    </type-tuple>

`type-tensor`
.............

Available Filter Operations
###########################

**all**

In context of a `type-tensor`, the filter operation `all` means that (assuming the corresponding manifest element is also a `type-tensor`)
the `type-tensor` elements in the filter & manifest are considered to match if and only if
each child of the `type-tensor` element in the manifest, which must be a `dim`, matches its counterpart in the filter.
For details on matching rules of `dim` elements, see the specification for :ref:`dim<dim-element>` element .

For example, if the filter element is:

.. code-block:: xml

    <type-tensor filter="all">
        <dim filter="lt">3</dim>
    </type-tensor>

Then the following manifest element matches when `n` is an integer and :math:`0 < n < 3`:

.. code-block:: xml

    <type-tensor>
        <dim>n</dim>
    </type-tensor>

.. _dim-element:

`dim`
.....

Available Filter Operations
###########################

The available filter operations on `dim` are similar to those on numeric types like `int` and `float`.
Concretely, the following filter operations are available:

- **equals**: manifest and filter element matches if and only if the axis size specified by the manifest element is **equal to** that specified by the filter element.
- **lt**: manifest and filter element matches if and only if the axis size specified by the manifest element is **less than** that specified by the filter element.
- **le**: manifest and filter element matches if and only if the axis size specified by the manifest element is **less than or equal to** that specified by the filter element.
- **gt**: manifest and filter element matches if and only if the axis size specified by the manifest element is **greater than** that specified by the filter element.
- **ge**: manifest and filter element matches if and only if the axis size specified by the manifest element is **greater than or equal to** that specified by the filter element.

For example, if the filter element is:

.. code-block:: xml

    <dim filter="equals">3</dim>

Then **only** the following manifest element matches:

.. code-block:: xml

    <dim>3</dim>

`lt`, `le`, `gt`, and `ge` works similarly.

`type-string`, `type-bool`, `type-int` and `type-float`
.......................................................

These elements are "terminal elements" in a type-declaration hierarchy.
They are always leaves in the hierarchy tree and represents requirements on the type of a scalar value.
Only the `none` filter operation is available in all of these four elements.

In contrast to `string`, `bool`, `int` and `float`,
`type-string`, `type-bool`, `type-int` and `type-float` does not have filter operations like `equals`, `lt`, `le`, `gt`, and `ge`.
This is because these elements are type declarations and define only **types**, instead of concrete values.
As a result, filter operations which requires comparison of concrete values are not available.

Compositors
------------

`logical`
.........

The `logical` element uses logical operations such as `and` and `or` to combine sub-filters into a composition.

Notice that for `and` and `or` filter operations,
there must be two or more children for the filter element to be valid;
in case of `not`, there must be exactly one.

The `none` filter operation is **NOT** available in the `logical` element.

Available Filter Operations
###########################

**and**

The `and` operations means that the filter matches if and only if all sub-filters match.

For example, if the filter element is:

.. code-block:: xml

    <logical filter="and">
        <int filter="gt">10</int>
        <int filter="lt">15</int>
    </logical>

Then the following manifest element matches only when `n` is an integer and :math:`10 < n < 15`.

.. code-block:: xml

    <int>n<int>

**or**

Similar to `and`, `or` means that the filter matches if and only if at least one sub-filter matches.

**not**

Similarly, `not` means that the filter matches if and only if the sub-filter does not match.

Special Filter Elements
-----------------------

.. _tag-collection-filter-element-specification:

`tag-collection`
.................

A `tag-collection` represents a collection of tags which can be either explicitly or implicitly matched against a manifest.

All children of a `tag-collection` must be `tag` elements.

A `tag` element is a special "auxiliary" element which must have no children.
Neither can it have a `filter` attribute because the filter operation type is specified in its `tag-collection` parent instead.
However, it must have non-empty text content enclosed between the starting and closing tags, which specifies the tag name.

For example, the following `tag` element represents a tag named "text-continuation":

.. code-block:: xml

    <tag>text-continuation</tag>

Tag matching is itself an important feature of |project_name| which is not the focus of this document on general filter syntax specification.
For details on tag matching, refer to :doc:`this page </spec/tag-matching>`.

This section will assume you are familiar with tag matching and will not explain related concepts.

.. _tag-collection-filter-operations-specification:

Available Filter Operations
###########################

**implicit-tag-match**

The `implicit-tag-match` filter operation means that the filter matches if and only if
for each tag in the tag collection, the XML-form filter it points to matches the manifest.
Notice that, when matching a tag, the matching process does not start from the tag element and the corresponding element in the manifest;
instead, |project_name| looks up the defined tags, finds the XML filter corresponding to that tag and matches that filter against the manifest from the root.

For example, if the filter is:

.. code-block:: xml

    <dict filter="all">
        <named-field name="data">
            <int filter="gt">1</int>
        </named-field>

        <named-field name="tags">
            <tag-collection filter="implicit-tag-match">
                <tag>tag1</tag>
            <tag-collection>
        </named-field>
    </dict>

Where the tag named "tag1" points to such an XML filter:

.. code-block:: xml

    <dict filter="all">
        <named-field name="data">
            <int filter="lt">10</int>
        </named-field>
    </dict>

Then the following manifest matches if and only if :math:`n` is an integer and :math:`1 < n < 10`:

.. code-block:: xml

    <dict>
        <named-field name="data">
            <int>n</int>
        </named-field>

        <named-field name="tags">
            <tag-collection/>
        </named-field>
    </dict>

In essence, the filter requires that the XML filter which "tag1" points to must also match for the filter to considered to match.

**explicit-tag-match**

The filter operation `explicit-tag-match` is provided to handle cases where the features of a model needs to be marked explicitly,
typically because the matching system alone is not sufficient to determine whether a certain feature is present in the model.
The most common examples are call schemes, where matching the input & output type declarations alone are not sufficient to determine
whether the model follows a certain call scheme because two models may have inputs with the same type but different semantic meanings.

In short, if the filter operation is `explicit-tag-match`,
then the filter matches if and only if all tags present in the filter element are also present in the corresponding manifest element.

For instance, with `explicit-tag-match` being the filter operation type, the example provided in the **implicit-tag-match** section
would not match any more because even though :math:`n` matches the tag named "tag1" when :math:`1 < n < 10`,
the manifest does not **explicitly** include that tag in its `tag-collection` element.

However, the following manifest element does match because "tag1" is explicitly included:

.. code-block:: xml

    <dict>
        <named-field name="data">
            <int>n</int>
        </named-field>

        <named-field name="tags">
            <tag-collection>
                <tag>tag1</tag>
            </tag-collection>
        </named-field>
    </dict>
