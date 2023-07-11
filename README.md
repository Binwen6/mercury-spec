# Mercury: A DNN Specification for Developers

## We need your help!

Mercury is still young and not yet fully-fledged.
We need help in the following aspects:

1. The most urgent thing is to write more Mercury
extensions, so that developers can access a large collection of
deep learning services through Mercury.
We need people who publish deep learning models (e.g., LLAMA, Alpaca, etc.)
to write extensions for their models and make their models compatible with and accessible from Mercury.

2. We also need beta-tester developers to use Mercury for application development
and provide feedback for potential improvement in the core specification, which includes improvement in Mercury XML syntax, definitions of new tags / call schemes, etc.
This will make Mercury more sophisticated and more suitable for application development.
You don't need any sign-up process to become a beta-tester;
just install Mercury, use it, and provide feedback if you would like to.

The goal of Mercury is to promote open source, open access AI
and make AI easy to use and accessible for everyone.
As we move forward to achieving this goal,
we highly value feedback & pull requests from both the development and the research community!

Our contact email: **trentfellbootman@gmail.com**.

## Quick Links

[Documentation](https://mercurynn.readthedocs.io/en/latest/)

[Project Homepage](https://trent-fellbootman.github.io/mercury.io/)

[Test PyPI](https://test.pypi.org/project/mercury-nn/)

## What is Mercury?

Mercury is a specification for deep neural networks (DNNs) that is specifically designed for application developers.
Mercury enforces a unified interface among the myriad of DNNs and makes it easy for application developers
to utilize the power of AI in their applications in a model-agnostic and cross-platform manner.
Moreover, Mercury enables developers to avoid depending on specific, concrete models and instead depend on common aspects and capabilities
(like being able to answer questions or following a particular input / output format) of the models,
through its filtering and duck-typing system.

## Why do we need a specification for deep neural networks?

With the (not so) recent development in deep learning, there have been some trends that motivates a framework like Mercury.
Specifically:

1. Deep learning has matured to a point where it is ready to be directly used in production & consumer application
with no develop-time debugging, finetuning or adaptation.
Hence, now is the appropriate time to create a unified specification
and abstract DNNs as GPU-like resources that you can use directly with no special tuning,
so that developers can easily access a myriad of models without having domain knowledge in deep learning
or adapting their applications to specific models.

2. Modern deep learning models are no longer quirky problem-makers that exhibit undefined behavior
on sensible (not adversarially-constructed) inputs with a non-negligible probability.
Their behavior are becoming more predictable in a way that makes it possible to extract the commonalities
(e.g., the ability to answer factual questions) among the same type of models.
This makes it possible to design a framework that select the best model available on the user's platform at runtime,
which is obviously much better than hardcoding the application to use a specially-adapted model at develop time.
Such an observation is also the technological basis behind Mercury's design philosophy: depend on capabilities, not implementations,
which means developers only specify **what the model should be able to do** at develop time,
and the framework would automatically pick the best available model at runtime.

## Join us in building the future of AI applications!

Mercury is the first developer-oriented AI specification that abstracts DNNs in a way similar to GPUs in human history;
developing such a specification is not an easy thing,
as it requires developers and researchers to work together
to explain the expected behavior of deep neural networks in a way that is easy both for developers to understand and for researchers to implement.

Thus, we highly value help, feedback, suggestions and collaboration from developers, researchers and AI companies.
Mercury is designed to be an open-source standard driven by both the research and the development community;
we accept any pull requests and suggestions that make Mercury better,
no matter it's a bug fix, a feature addition or even a change in the architecture.
As Mercury is still young, it is even possible to rewrite the whole specification using a different set of design principles.

Contact us at **trentfellbootman@gmail.com** if you are interested in contributing to Mercury or becoming part of the team!

## NOTICE

Current progress:

- Currently there is binding for Python only.
May need to consider implementing bindings for more languages & frameworks (e.g., Flutter) if we want developers to use Mercury in production environments.
- Currently the only supported extension is ChatGPT; we need to contact more researchers & model providers and adapt more models so that developers can access a larger set of models with Mercury.
