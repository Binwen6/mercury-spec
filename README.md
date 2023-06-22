# OpenNN: A Cross-platform Specification for Deep Neural Networks

## What is OpenNN?

OpenNN is short for "Open Neural Networks".
At its core, OpenNN is a specification for deep neural networks like ChatGPT and Stable Diffusion.
OpenNN enforces a uniform interface for accessing deep learning models and
allows developers to utilize models developed by different organizations and deployed on different hardware backends
in a platform-, vendor- and backend-agnostic manner.

OpenNN is a specification designed for **developers**, not **researchers**.
It focuses on **using** deep neural networks (e.g., feed inputs and get outputs), not **designing** them (i.e., dataset collection, neural architecture design and training).

## Why do we need a specification for deep neural networks?

There are primarily two reasons that justify the need for a platform-, vendor- and backend-agnostic specification for deep neural networks:
enabling black-box usage of deep neural networks for developers, and separating the interface of a model from its implementation.

### **Developers expect easy, uniform and blackbox usage of deep learning models**

Simply put, there needs to be a specification designed for those who **use** the models (typically developers),
not those who **design** the models (typically researchers).

In the early days, deploying deep learning models in an application is a hard, time-consuming and sometimes expensive process
that requires both domain knowledge and deep learning expertise.
Typically, such a process would require training or at least fine-tuning a model on an application-specific dataset,
and it is almost inevitable that the model would need to be modified (either in architecture or in weights) or debugged to fit the application's needs. Starting from late 2022, that is no longer true.

With the advent of generally-capable models like ChatGPT, it is now possible to utilize deep neural networks in a plug-and-play manner:
just grab the model and use it.
Tell it what you want it to do in the inputs (the "prompt"), and the model will do it.
No environment setup, no dataset collection, and absolutely no training or fine-tuning.
Usually it is even possible to use the model without downloading it, via a cloud API like Open AI's ChatAPI.

In such a context where a model is used in a plug-and-play manner with little or no debugging or modifications,
there is no need for developers to know the details of the model and be able to manipulate its weights and structure.
Developers (especially those who are not familiar with deep learning) would want a simple and easy-to-use interface that abstracts away the weights and network architectures whenever it is possible.
OpenNN satisfies that need.

### **The principle of separating interface v.s. implementation applies to AI applications as well**

There are a gazillion of deep learning models with different architectures and weights.
From an functional perspective, however, many of them do the same thing.
For example, both LSTM and Transformer based models can do text continuation
(i.e., give the model an incomplete chunk of text and let it fill in the rest).

Clearly, it is not a good idea to hardcode an application to use GPT-3 and
having to modify the source code and recompile the whole thing when GPT-4 comes out.
The idea is, all the application needs is a model for text-continuation;
it should be able to work with any model that does that, no matter it's GPT-3,
GPT-4 or an LSTM based model.

From the developer's perspective, the important thing is **what a model does**,
not **how the model does it**.
In other words, developers should depend on **interfaces**,
not **implementations**.

In general, separating the interface and implementation allows applications to treat deep learning models as GPUs:
they work with any compatible model and dynamically selects which one to use based on user preferences,
and when a new model comes out, it benefits from improved model performance with no change in code.

OpenNN effectively separates the interface from implementation:
it defines the interface that all models should implement so that developers can use a uniform interface to access all models,
and asks that the researchers or vendors who develop the models make their creations compatible with the interface.

## Join us in building the future of AI applications!

OpenNN is the first developer-oriented AI specification in human history;
developing such a specification is not an easy thing,
as it requires developers and researchers to work together
to explain the expected behavior of deep neural networks in a way that is easy both for developers to understand and for researchers to implement.

Thus, we highly value help, feedback, suggestions and collaboration from developers, researchers and AI companies.
OpenNN is designed to be an open standard driven by both the research and development community;
we accept any pull requests and suggestions that make OpenNN better,
no matter it's a bug fix, a new feature addition or a change in the architecture.
As OpenNN is still young, it is even possible to rewrite the whole specification using a different set of design principles.

Contact us at **trentfellbootman@gmail.com** if you are interested in contributing to OpenNN!