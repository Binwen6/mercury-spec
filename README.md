# The Athena Initiative: A Cross-platform Specification for Intelligent Hardware

This repository contains code for the athena initiative,
a project aiming for a platform-independent specification for the modern deep learning models.

## What is the Athena Initiative?

Simply put, Athena is an **abstraction layer between developers and deep learning models** like ChatGPT.
It is a specification for deep learning models which provides a unified interface for calling models
with different input/output interface, different hardware backends, and different venders.

The aim of the Athena Initiative is to allow developers to access deep learning models
without the need to depend on a specific vendor (like Open AI) or a specific model.
For example, by using the Chat API abstraction provided by Athena,
you can seamlessly switch between using ChatGPT, Alpaca and any chat-based models.

## Why do we need a specification for deep learning models?

The short answer is, **developers will need a platform & vendor independent way
to access a myriad of deep learning models in their applications**.

With the advent of highly-capable models like ChatGPT,
deep learning has matured into a production-ready technology
which can be used in applications just like any other
software / hardware resources like GPUs.
In the near future, the world will see an eruption of
providers (either companies like Open AI or models like LLAMA)
offering models with different capabilities (e.g., text, image or 3D models),
features (e.g., low cost or high quality),
and I/O interfaces (e.g., different JSON request formats for API calls).

Although deep learning models typically have different weights, I/O formats
and even implementations
(e.g., text continuation models can be implemented with either Transformer or LSTM),
they can be categorized into a few groups based on their capabilities.
From the developer's perspective,
it is unnecessary to know the specifics of each model;
**the only thing developers need to know is what the model does, and how to call it**.
Just like it would be tedious to write a program for each GPU,
**developing programs that work with only a specific model (e.g., ChatGPT) is a bad idea**.
As a result, Athena tries to give developers model-agnostic APIs for accessing deep learning models, just like how OpenGL and Vulkan give developers GPU-agnostic APIs for accessing GPUs.

## The design of Athena

What is the appropriate abstraction for deep learning models?
To answer that question,
it is important to observe that **deep learning models (DLMs for short) are
better abstracted as hardware, rather than software**,
and that they share a lot in common with GPUs, in that:

- **Both rely on a "host device".**
Similarly to how GPUs must be controlled by CPUs,
DLMs must be called from a non-intelligent program like a Python script
(there are exceptions to this, though).
- **Both are specialized computing devices.**
GPUs are specialized for data-parallel computations,
while DLMs are specialized for "human-like", "magical" and "intelligent" operations
(e.g., text generation, image classification, etc.).
- **Both are inflexible about the operations they can perform.**
Typically, GPUs are only used to do graphics or matrix operations;
a specific DLM is usually only capable of doing a specific task
(e.g., image generation).
However, just how GPGPUs are Turing-complete,
there are DLMs that are more general-purpose, such as ChatGPT.

By observing the similarity between DLMs and GPUs,
Athena borrows a lot of concepts from GPU APIs such as Vulkan, in that:

- Each DLM is abstracted as a "physical device".
- Before using a DLM, a "logical device" representing a callable handle
to the corresponding DLM must be created.
- Properties can be queried from "physical devices" (DLMs),
and applications can use the retrieved "device properties"
to select the appropriate "device" (DLM) to use.
In addition to specifying what the model does, "device properties"
may also provide metadata such as the cost & delay for each API call,
the accuracy of the model,
whether the model is deployed locally or on the cloud, etc.

As a result, using a DLM in Athena is largely similar to using a GPU in Vulkan.
Typically, using a DLM in Athena involves:

1. "**Physical Device Selection**":
List the available DLMs (physical devices),
get their properties and decide which model to use.
For example, the application may prefer to use the cheapest model
if budget is limited.
2. "**Logical Device Creation**":
Create a callable logical device from the selected DLM.
This may include filling in the credentials such as an Open AI token,
if the model is deployed on the cloud.
3. "**Queue Submission**":
After the logical device is created,
the application can submit commands to the logical device.
For text-continuation models, for example,
a command might be continuing a prompt.
As it takes significantly more time to execute a command on a DLM
compared to CPU, GLM workloads are typically executed out of order,
just like in GPUs.

## Athena as an open project

Although Athena shares a lot in common with Vulkan, there is a big difference:
when Vulkan was created, there was already a mature GPU market and software ecosystem;
the AI-based software ecosystem, however, is still in its infancy,
and there are a lot uncertainties as for how specifications for deep learning models should be designed.
The design of a hardware specification is a coordinated effort between vendors and application developers,
and we would highly appreciate help and feedback from both AI companies and the developer community.
If you are interested in contributing to the Athena Initiative,
feel free to submit issues and pull requests, or reach out to us!

Our email addresses:

- **trentfellbootman@gmail.com** for Trent Fellbootman
- **bocheng.zou@outlook.com** for Bocheng Zou
