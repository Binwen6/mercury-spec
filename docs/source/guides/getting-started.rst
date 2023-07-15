Getting Started with |project_name|
===================================

This tutorial introduces some basic concepts in |project_name| and
walks you through the basic steps of creating an AI-powered application with |project_name|.
Basically, they are:

1. Defining the requirements for the deep learning models that you use in your application;
2. Selecting an available model on the user's platform;
3. Using the model.

In this tutorial, you will create your very first application with |project_name|:
An AI-powered chatbot that outputs text with image illustrations.
In principle, |project_name| is a language-independent specification with bindings for multiple programming languages,
which means you can use |project_name| from any supported language.
For simplicity, however, this tutorial uses the Python binding.

While this tutorial is designed to get your hands dirty with |project_name|,
it also serves as a good introduction to developing AI-powered applications.
Throughout the tutorial, you will be introduced to several fundamental concepts,
methods and principles for developing applications that use AI.

Notice that this tutorial requires that you have at least a chat-completion model and an image-generation model available on your device.
If you don't, follow the instructions in the :ref:`installation guide <sample-extensions-installation>` to install the model extensions for ChatGPT and DALL E;
they are known to work with this tutorial.

In addition, this tutorial requires `matplotlib`.

Defining your needs
-------------------

|project_name| Follows Duck-Typing
##################################

In |project_name|, you never hardcode what model you use at build-time,
as that will be very hard to maintain and won't work in a cross-platform manner.
Instead, |project_name| follows the design philosophy of "**duck typing**":
you define what requirements a model must satisfy to be a good fit for your application,
and |project_name| selects a compatible model on the target platform at run-time.

Requirements are Specified as Filters
#####################################

A set of such "requirements" that constrain the expected behavior of a model is called a "**filter**".
Filters can define any requirements for a model's behavior,
but the two most important types of requirements are **call scheme** and **capabilities**.

A call scheme defines the expected input / output formats when the model is called,
as long as the semantics of the inputs & outputs.
For example, the call scheme of ChatGPT might be:

.. code-block:: yaml

    input:
        type: list[tuple[string, bool]]
        semantics: |
            A list of tuples. For each tuple, the first element is the message sent,
            the second being whether the message is sent by the user or the AI.
    output:
        type: string
        semantics: The next AI-sent message.

Notice that using YAML is for simplicity only; actual filters are written in XML instead.

While **call scheme** defines the "hard" constraints on input / output formats,
**capabilities** defines what the model is capable of.
For example, the **capabilities** of ChatGPT may include
"high-school-math" (capable of solving basic calculus),
"imagination" (capable of coming up with original, ficticious stories), etc.
On the other hand, a smaller, locally-deployed chat-completion model may have no special capabilities.

Another important concept with filter is **tags**.
A **tag** is simply a predefined "convenient filter" with predefined requirements specified.
For example, a **tag** named "ChatGPT-like" may mean that models satisfying this tag are expected to have the same call scheme as ChatGPT,
and have extensive factual knowledge in fields such as mathematics, history and programming.

How do you define a filter?
###########################

Under the hood, |project_name| uses XML to represent requirements defined in a filter.
While being very flexible and expressive, the XML filter syntax is rather wordy,
and you rarely need to define a filter in XML by yourself.
Instead, you will typically use predefined convenient methods that constructs XML filters with simple arguments.

Defining Filters for a Chatbot
##############################

In our simple chatbot app, we will need two models: one for chat completion and another for image generation.
For chat completion, we need not just a model that can chat;
in addition, we need the model to be able to understand simple instructions,
such as when the user wants to end the conversation.
Hence, we define the filter in the following way:

.. code-block:: python

    # import libraries
    import mercury_nn as mc
    import matplotlib.pyplot as plt


    chat_filter = mc.Filter.fromArgs(callScheme="chat-completion",
                                    capabilities=["instruction-comprehension"])

Typically, you will use `mc.Filter` to construct filters.

For the image generation model, we don't need any special capabilities, so we can define the filter as:

.. code-block:: python

    image_generation_filter = mc.Filter.fromArgs(callScheme="image-generation")

Now that we have defined the filters, let's move on to model selection.

Selecting & Instantiating a model
---------------------------------

The next step is selecting the models.
This typically involves 3 steps:

1. Enumerate all available models with `mercury.enumerateAvailableModels()`;
2. Filter out the models that satisfy the requirements of the application with the `ModelCollection.select` method;
3. Select one model from the models returned in the previous step according to some criteria (e.g., price).

First, we call `mercury.enumerateAvailableModels()`.
This would return all available models on the user's platform at run-time so that your application works in a cross-platform manner.

.. code-block:: python

    # mercury was previous imported as mc
    model_collection = mc.enumerateAvailableModels()

The return value of `mercury.enumerateAvailableModels` is a `ModelCollection` object which stores the metadata of all available models.

`ModelCollection` has a convenient `select` method which returns another model collection with only models in the collection that satisfies the filter,
and we use this method to retrieve the compatible models with the filters defined previously:

.. code-block:: python

    chat_models = model_collection.select(chat_filter)
    image_generation_models = model_collection.select(image_generation_filter)

For simplicity, we just select the first model that satisfies the requirements:

.. code-block:: python

    
    # `ModelCollection` implements `__getitem__` method
    chat_model = chat_models[0]
    image_generation_model = image_generation_models[0]

In production environment, however, the model should be selected according to some criteria, such as price.

Finally, we need to instantiate the model with `mercury.instantiateModel`.
This methods looks at the metadata of the model stored in the provided model entry (an element in a `ModelCollection` object),
loads the implementation files provided by the model's publisher, and returns a callable model that is ready to be used.
The publisher must ensure that no interaction is needed when instantiating a model.
For example, for ChatGPT, the user may need to fill in the API key in a configuration file or export it as an environment variable,
so that model instantiation would run smoothly without throwing some "NO API KEY ERROR".

We instantiate the models with the following code:

.. code-block:: python

    chat_model = mc.instantiateModel(chat_model)
    image_generation_model = mc.instantiateModel(image_generation_model)

Using the model
---------------

Now that we have created the models, we can use them to build the user experience.

Warm Greeting
#############

The first thing the user should see after starting up the application is, of course, a greeting:

.. code-block:: python

    greeting = "Hi! I'm a chatbot. Let's chat!"
    print(greeting)

Multimedia Interaction
######################

Next, we implement the chat functionality.
In each round of conversation, the user sends a message to the AI, and the AI returns another message,
optionally with an image for illustration.
Hence, we will need the AI to determine whether or not to generate an illustration,
and if so, what prompt to feed in to the image generation model.

We implement such functionality with the following code:

.. code-block:: python

    messages = [("""
    You are a chatbot talking to a user.
    Although you are a text-based chatting model,
    you now have the ability to generate images,
    because each time you say something, I will analyze what you said and see if you intend to create an image.
    Just speak normally as if you can generate images,
    and when you do need to create an image, ALWAYS LEAVE A PLACEHOLDER in your response, e.g., "[image-placeholder]".
    There is no delay in image generation; each time you show the intent to make an image, the image is generated instantly,
    so there is no need to say things like "wait a moment".""", True)]

    while True:
        # retrieve user input
        user_input = input('>>> ')
        # append user input to message history (boolean value indicates who sent the message, True for user and False for AI)
        messages.append((user_input, True))
        # retrieve AI's response
        ai_response = chat_model.call(messages)
        # append AI's response to message history
        messages.append((ai_response, False))

        # illustration generation
        illustration_decision_input = f"""
    You are talking to a user. You decided to respond to the user:

    {ai_response}

    Do you think there is image content in the above response?
    If yes, output a description for the image and NOTHING ELSE;
    if you are SURE there is no image content, output "NO" and NOTHING ELSE.
    If there is an image-placeholder in your response (e.g., [image-placeholder]), it is guaranteed that there is image content;
    in this case, you should output the description for the image, and DO NOT output "NO".
    """

        illustration_decision = chat_model.call([(illustration_decision_input, True)])

        image = None
        if illustration_decision != "NO":
            # generate image
            image = image_generation_model.call(illustration_decision)

        # print AI's message
        print(ai_response)

        if image is not None:
            print(f"I also made an illustration.")
            plt.figure(figsize=(10, 10))
            plt.imshow(image)
            plt.title('illustration')
            plt.axis('off')
            plt.show()


If you are new to AI application development, the above code might be a lot to take in even if you are familiar with deep learning.
The `while` loop is self-explanatory; each iteration represents one round of interaction.
The first few lines inside the `while` loop is easy to understand:
we are asking the user for input and adding the message from the user to the message history.
Since deep learning models are, in essense, stateless function approximators
(meaning that they do not store "state" objects like previous messages),
we need to pass in the entire message history as input and retrieve the new chat message that the model generates.
Then, we also append the AI's message to the message history.

The lines after that may need some explanations.
First, we are **multiplexing** the chat-completion model and using it to decide whether or not to generate an illustration,
and if so, what to feed into the image-generation model.
This is what the `illustration_decision_input` prompt do.
Notice that we are giving to the model only that prompt, instead of the whole message history.
If the model decides to generate an illustration, we call the image generation model,
then retrieve and use matplotlib to show the generated image.
In a real application, of course, you should use something more user-friendly than `matplotlib.pyplot`.
The lines after that are self-explanatory.

Graceful Shutdown
#################

Obviously, it is a bad idea to have a user kill the application when he/she wants to shut it down.
Hence, we will need to allow the user the shutdown the application with inputs.
A straightforward way to implement such a functionality is to check if the user's input is equal to some predefined command (e.g., "QUIT"),
and if so, shutdown the application.
A more elegant way, however, is to also use AI to determine when to shut down.

To achieve this, we append the following code to the `while` loop's body:

.. code-block:: python

    shutdown_decision_prompt = f"""
    You are chatting with a user. The user says:

    {user_input}

    Does the user want to end the conversation? Output "YES" or "NO" ONLY and NOTHING ELSE.
    """

    response = chat_model.call([(shutdown_decision_prompt, True)])

    if response == "YES":
        break

In the above code, we ask the AI to determine whether or not the user wants to end the conversation,
and break the `while` loop (and hence shuts down the application) if the answer is affirmative.

Summary
-------

Congratulations! In this tutorial, you have learned the basics of |project_name|, as well as AI application development.

If you try using the chat bot, you may notice that it often fails to generate images.
As this is just a simple tutorial with a few lines of code, such a "bug" is expected.
If you would want the application to perform better, you will need to adopt additional techniques which requires more code,
or use a toolkit for AI application development, such as Athena (**# TODO: Athena is still under development**).

Next, check out the tutorial on :doc:`extension development </guides/extension-development>`
to learn how to allow |project_name| to use deep learning models that you developed!
