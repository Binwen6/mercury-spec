Diving Deeper into |project_name|
=================================

This guide provides a deeper understanding of |project_name| specification / binding,
their working mechanism, as well as the design choices behind |project_name|.
It is recommended that you read the :doc:`introduction </guides/introduction>`, the :doc:`getting-started tutorial </guides/getting-started>`,
as well as the :doc:`tutorial on extension development </guides/extension-development>`
to get an idea of how to use |project_name|, before you read this more advanced tutorial.

The Design Principles of |project_name|
---------------------------------------

Dependency Inversion Principle Applied to Artificial Intelligence Services
##########################################################################

The most important idea and the primary goal of |project_name| is to apply Dependency Inversion Principle (DIP)
to Artificial Intelligence services.
Dependency Inversion Principle is a design principle which states that:

1. High-level modules should not depend on low-level modules. Both should depend on abstractions.
2. Abstractions should not depend on details (implementations). Details should depend on abstractions.

In briefer terms, DIP means "depend on interfaces, not implementations".
In context of AI application development, DIP means "**depend on abstractions of deep neural networks, not concrete models with weights**".
Here, "abstractions" means the |project_name| specification, which includes call schemes, capabilities, etc.
|project_name| abstracts concrete deep neural networks with specific weights into abstract AI services
which follow certain input / output interfaces and have certain capabilities.
As an example, ChatGPT corresponds to an abstract model that expects as inputs a list of chat messages,
outputs another message that continues the conversation,
and is capable of answering factual questions in a variety of fields including history, programming, philosophy, etc.

DIP is a useful and powerful idea in AI application development because it
allows developers to directly depend on **what is needed in the application**,
and frees them from having to be familiar with deep learning and choose the appropriate model for the application by themselves,
sometimes even to finetune the model on a customized dataset.
Consider the case where a developer wants to develop a chatbot for history education.
Obviously, the model selected must not only chat in natural language, but also provide factual knowledge about world history.
In the old days (okay, maybe not so old), a developer must manually choose a model that fulfills those requirements and explicitly use that model in the application.
Say, for example, that the developer chose ChatGPT. Now, there are two major issues with this:

1. **Portability**: The application won't run for a user who does not have an Open AI account.
2. **Maintainability**: If the developer wants to use another model later (perhaps because a model more powerful than ChatGPT has come out),
   he/she must change the source code to adapt to the new model and rebuild & redistribute the application.

With a framework that implements DIP, the developer would specify only what is needed for the application
(in case, a chat-completion model which has knowledge about history),
and the framework would automatically select the best model available at run-time.
In this way, the application would run on any platform which has access to at least one model
that satisfies the requirements, and when a better model comes out and is installed on a platform,
the framework would automatically select that model and yield an improved user experience.

Language Independence
#####################

Make the Low-Level Interface Verbose, the High-Level Ones Concise
#################################################################

How does |project_name| work exactly?
-------------------------------------