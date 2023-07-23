Tag Matching in |project_name|
==============================

Tags in |project_name| is a mechanism introduced to allow developers to quickly pick out the models that meet the needs of their applications,
with the minimum amount of code.

In essence, a tag is nothing more than an XML-form "convenient filter" which is referred to by a name associated with it.
As a result, a tag specifies a certain feature (an aspect) of a model's behavior;
only models whose manifests matches the filter corresponding to the tag are considered to have that feature.
A model can have more than one tag, and a tag can be present on multiple models.
If you are familiar with Rust, think of a tag as a trait and a model as a struct.

As an example, think of a tag named "text-in-text-out" which matches a manifest only when the input and output of types of the model are both string.
Such a tag defines a "text-in-text-out" feature that are present only on models which input & output text.

Typically, a model publisher specifies a number of tags applicable to (matching) the model in a special section in its manifest.
However, the tags in this special section may not be exhaustive; the model may be determined to match more tags at run-time through implicit matching,
a mechanism discussed later.

|project_name| provides these "convenient filters" so that developers can skip the hassle of writing XML-form filters
and instead refer to predefined filters by their names.
Basically, that's all the tag machanism does.

Implicit & Explicit Tags
----------------------------

In essence, a tag defines a certain feature of a model through an XML-form filter;
a model is said to match that tag as long as its manifest matches the filter corresponding to that tag.

Tags may be implicit or explicit.
Implicit tags does not require the matching model to include them in the manifest,
while explicit ones do.

For example, here is an implicit tag named "gt-1":

.. code-block:: xml

    <dict filter="all">
        <named-field name="data">
            <int filter="gt">1</int>
        </named-field>
    </dict>

When using the XML below, the tag becomes explicit:

.. code-block:: xml

    <dict filter="all">
        <named-field name="data">
            <int filter="gt">1</int>
        </named-field>

        <named-field name="tags">
            <tag-collection filter="explicit-tag-match">
                <tag>gt-1</tag>
            </tag-collection>
        </named-field>
    </dict>

Basically, the above XML for explicit tag specifies that this tag named "gt-1" matches a manifest
only when the manifest contains an integer field which is greater than 1,
and that there is a section named "tags" which explicitly contains a tag named "gt-1" (which is the tag itself).
In contrast, the XML filter for implicit tag matches as long as the manifest contains an integer field which is greater than 1.
This is the difference between implicit and explicit tags:
explicit tags requires the matching model to **explicitly** include the tag in its manifest,
while implicit tags does not.

The :ref:`related section in the filter syntax specification<tag-collection-filter-element-specification>` explains the details of
what `tag-collection`, `tag` and `explicit-tag-match` means.

You may wonder why we need explicit tags.
Explicit tags are provided because sometimes the matching system alone is insufficient to determine whether a certain feature is present on a model.
In this case, the model publisher must explicitly mark the model as having that feature.

For example, think of two tags named "question-answering" and "text-continuation".
A model matching the "question-answering" tag is expected to take in a question as a string and return the answer as another string,
while a model matching the "text-continuation" tag is expected to take in some incomplete text as a string, imagine how the text would continue,
and return the complete text as a string.

In this case, the "hard-requirements" that these tags have on a matching model are exactly the same:
the model must take in a string as input and return another string as output.
However, the **semantic meanings** of the input & output are starkly different.

Therefore, we cannot say that a model matches the "question-answering" tag just because it expects strings as inputs and returns strings as outputs;
we are sure that this is a question-answering model only when the model publisher explicitly marks it as such.
In this case, the "question-answering" tag should be made explicit,
and should only match a model if its manifest explicitly contains this tag (same for the "text-continuation" tag).

Implicit & Explicit Matching
----------------------------

Similar to how tags can be implicit or explicit, the requirements on tags in a filter can also be implcit or explicit.
For details, see the :ref:`related section in the filter syntax specification<tag-collection-filter-operations-specification>`.

Notice that if the tag itself is explicit, a matching manifest is still required to explicitly include the tag
even if you're using implicit matching.

Tag Matching Trees
------------------

The XML-form filter of a tag may contain a `tag-collection` element,
in which case a model matching the tag must also match the tags specified in that `tag-collection` element.
The filters of those tags may further contain `tag-collection` elements with `implicit-tag-match` filter operations, and so on.
In this case, one tag actually represents a tree of tags;
when |project_name| matches this tag against a model, the "top-level" tag is compared first,
a `tag-collection` element is found, and the tags contained in that element are also compared.
Such a process happens recursively, and the model matches the tag only if it matches all tags in this "tag tree".

Tag Hierarchy, Naming Rules and Condensed Tags Representation
-------------------------------------------------------------

Tags are not independent of each other; also, the meaning of a tag may be different in different contexts.

For example, a tag named `cloud`, which specifies that a model is deployed on the cloud,
may require the manifest to specify the cost incurred per image in case of an image-generation model,
or the cost per token in case of a language model like GPT-3.5-turbo.
In this case, the meaning of `cloud`, and correspondingly, the XML filter that the tag should point to, is different in different contexts.

Additionally, certain tags may be applicable to a model only if the model has certain features.
For example, a tag named `question-answering` typically applies to language models only,
and a tag named `photo-realism` may apply to image-generation models only.

Namespaces are introduced for these occasions to avoid ambiguity.
The names of most tags contains a namespace prefix to restrict the scope in which it is applicable.

For example, the tag for specifying cloud-deployment on a language model might be `language-model::cloud`,
while its counterpart defined for image-generation models might be `image-generation::cloud`.
In this case, `language-model::` and `image-generation::` are namespace prefixes,
specifying the contexts in which each tag is applicable.

Namespaces can be nested. For example, you make see tag names in the form of `root-namespace::child-namespace::another-namespace::tag-name`.
The string `::` is the C++ style namespace delimiter used to separate different components of a name.

When developers wants to pick out the models that they can use in their applications,
they would typically want to specify a set of tags which a model must match,
instead of a single tag, because a tag typically makes sense only in a specific context (namespace).
For example, when a developer wants to select all the image-generation models that are cloud deployed,
two tags, namely `image-generation` and `image-generation::cloud` must be specified;
it is insufficient to specify just `image-generation::cloud` because the tag makes sense only on image-generation models.

However, specifying all tags one by one can be quite verbose.
For this, |project_name| allows **condensed tags representation** to specify multiple tags in a consise way.
As an example, `image-generation` and `image-generation::cloud` can be specified as `image-generation.cloud`.

The syntax of the condensed tags representation is as follows:

- `.` is the `concatenation delimiter`. `<a>.<b>` means both `<a>` and `<a>::<b>`, where `<a>` and `<b>` are two tags.
  
  You can chain multiple name components in this way.
  For example, `a.b.c` represents 3 tags: `a`, `a::b`, and `a::b::c`.

- `::` is the `namespace delimiter`. `<a>::<b>` means `<a>::<b>` only.

- You can mix `.` and `::` to achieve the effect you desire.
  For example, `a::b.c::d.e` represents 4 tags: `a::b`, `a::b::c`, `a::b::c::d` and `a::b::c::d::e`.

- You can also use brackets to add multiple "branches" after a namespace.
  
  For example, `a.b.{c, d, e}` represents 5 tags: `a`, `a::b`, `a::b::c`, `a::b::d` and `a::b::e`.

For a practical example, a developer may use condensed tags representation `text-continuation.{cloud, transformer}` to pick out
all text-continuation models deployed on the cloud which uses the transformer architecture.
Such a representation expands to 3 tags: `text-continuation`, `text-continuation::cloud` and `text-continuation::transformer`.
