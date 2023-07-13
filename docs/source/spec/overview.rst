|project_name| Specification Overview
=====================================

Behavior Defined by Manifests, Requirements Defined by Filters
--------------------------------------------------------------

At its core, |project_name| is a language-independent specification that
define a set of rules for model publishers to specify the behavior of their models,
and for application developers to specify the requirements the models must meet to fit the needs for the applications.
The behavior of a deep learning model is defined in a **manifest** file typically named `manifest.xml`;
the requirements on a model is defined in a **filter**.
When a model whose behavior is defined in its manifest is considered to meet the requirements defined in a filter,
the manifest and the filter are said to **match**.
Model publishers write the manifest files for their models following the rules defined by |project_name|;
when an application is run, the |project_name| runtime reads the manifests of the installed models,
determines which models fit the needs of the application by matching the manifests to the filters defined by the application developer,
and selects a specific model to use.

Both the manifests the filters are defined in XML and are independent of the programming language used;
their syntax are largely similar but there are some subtle differences.

Valid Usage & Match Failures
---------------------------------------

Manifests and filters must follow a set of syntactical rules defined by the |project_name| specification;
each of these rules is called a **valid usage**.
Valid usage is defined on the XML-form manifests & filters,
and is thus independent of the programming language used.

There are two major motivations to defining valid usages:

1. Valid usages ensures well-defined behavioral consistency across |project_name| bindings of different programming languages.
   It specifies what kind of manifests & filters should be considered valid,
   as well as what errors should be reported when a manifest / filter is not valid.
2. Valid usages make it easy for developers to quickly identify the problem and
   look it up in the documentation when the manifest / filter is invalid.
   For example, a developer publishing a model may use a tool (**# TODO: publish the dev-tool as a pip package**)
   to check if the manifest file he/she wrote is valid.
   In case of an invalid manifest, the tool can report to the developer the exact valid usage that is violated,
   which makes it very clear what the problem is and how to fix it.

Similar to how valid usages define what kind of manifests & filters are considered valid,
**match failures** determine when a manifest is considered to match a filter,
and the situations in which they are considered not to match.
Match failures are also defined on XML and are independent of the programming language used,
ensuring behavior consistency across |project_name| bindings for different languages.

Implementations
---------------

|project_name| only defines the behavior of models, but not how to implement such behavior;
it is the model publishers' job to define concrete implementations for their models.
An implementation of a model is a group of things that allows the model to be used in a certain programming language,
which may include code, weights, library files, etc.

Although |project_name| is language-independent, it does not require models to be available for all programming languages that |project_name| supports.
A model may only support a limited set of programming languages, and when this is the case,
the model will be visible to |project_name| only in those languages.

Since different programming languages can have starkly different working mechanisms (especially between compiled and interpreted languages),
the exact specification on a model's implementation varies by language.
Typically, the model's manifest contains a section which defines the metadata of the implementations for each supported language,
such as the file path of the model's weights.

It is worth noting that |project_name| does NOT take into account the implementations when deciding whether a model fits an application;
all knowledge about a model's behavior comes from the manifest, and filter matching happens at XML level.
This ensures consistent behavior across different programming languages.
