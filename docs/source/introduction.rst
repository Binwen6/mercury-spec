Introduction
============

What is |project_name|?
-----------------------

At its core, |project_name| is a specification for deep neural networks like ChatGPT and Stable Diffusion.
|project_name| enforces a uniform interface for accessing deep learning models and
allows developers to utilize models developed by different organizations and deployed on different hardware backends
in a platform-, vendor- and backend-agnostic manner.

Why |project_name|?
-------------------

Why should developers use a specification like |project_name| instead of an existing toolkit such as PyTorch or TensorFlow?
The answer is two-fold:

- Easy, uniform interface to AI.
  
  |project_name| uses the same interface (or at least interfaces that follow the same rules)
  to access all supported deep learning models.
  With |project_name|, developers no longer need to adapt their applications to the specific interfaces
  of specific models or write abstraction layers for AI by themselves.

  This is a huge improvement over existing deep learning toolkits like PyTorch
  with which developers must lookup the documentation of the specific model they want to use,
  and make changes in code if they were to use another model later.

  In addition, |project_name| also unifies locally- and cloud- deployed models.
  Both types of the models follow the same interface; the only difference are in their parameters (e.g., latency, cost, etc.).

- Depend on features, instead of specific models.
  
  An even greater advantage of |project_name| is that it allows developers to depend on **features** of models,
  instead of actual models with specific weights and architectures.

  In |project_name|, a developer never needs to know what specific model they are working with;
  the only thing he/she knows is that the model follows a certain **usage scheme**
  (which basically means the expected input / output formats)
  and has certain **capabilities** (e.g., the model has domain knowledge about computer architecture).
  In fact, the actual model used in the application may change at runtime depending on user preferences
  or service availability (e.g., when there is no network coverage, locally-deployed model is used).

  Such a "depend on features, not concrete models" scheme is impossible with traditional frameworks like Tensorflow,
  and brings several significant benefits to developers:

  1. A developer no longer needs to be familiar with deep learning in order to employ
     such a technology in an application.

     In the old days (okay, maybe not so old), a developer would need to manually search for the models
     that meet their specific needs, then use that model throughout the application.
     When he/she wishes to use another model, he/she typically needs to make some changes in code to adapt to the new model.

     With |project_name|, this is no longer the case.
     When using |project_name|, a developer would first specify the requirements that a model must satisfy to be a good fit for the application.
     Then, |project_name| searches through all the available models and returns the ones that meet those requirements.
     The application then ranks those models according to some criteria, selects the best fit, and then use that model in the application.
     Developers no longer needs to know which models do what and their specific quirks - just specify what the application needs,
     and the framework would find a good model that does the job.
  
  2. Build once, deploy everywhere.

     As mentioned before, an application built with |project_name|
     would search for available models that meet the requirements of the application at run-time.
     On different platforms, |project_name| would always return the best fit for the application that is available.
     For example, on a compute cluster, |project_name| might return a locally-deployed model for lower latency and cost;
     on a mobile device, |project_name| would use a cloud-deployed model since compute capability is limited.

     However, the developer never needs to worry about platform-specific issues or select a specific model to use -
     just build the application in a model- and platform- agnostic manner,
     and |project_name| will ensure that the application runs on all platforms,
     as long as there is one model that fits the application.
     Such a characteristic makes |project_name| a particularly good fit for developing consumer applications (e.g., mobile apps).

  3. The application gets better performance when a better model comes out, requiring no change in code.

     When a model with better performance is released and installed on the target platform,
     |project_name| will automatically select that model for use in the application,
     and consequently, the performance of the application will improve.
     Such a performance gain requires neither change in code nor rebuilding the application.

Essentially, |project_name| makes deep learning models appear to developers as GPUs:
no knowledge about GPU architecture is required for application development,
one application works with any compatible graphics cards,
and performance of the application gets better on a better GPU by itself.

What does |project_name| look like?
-----------------------------------

An example usage of |project_name| with Python might look like the following:

**# TODO: Test whether the code sample works as expected**

.. code-block:: python

   import mercury as mc

   import logging

   model_collection = mc.enumerateAvailableModels()

   try:
      # get all models that fits the application
      chat_completion_models = model_collection.select(
         mc.Filter.fromArgs(callScheme="chat-completion",
                        capabilities=["imagination"]))
      
      # find the cheapest model available
      selected_model = sorted(chat_completion_models,
                              key=lambda model: model.price)[0]

   except mc.exceptions.ModelNotFoundException:
      logging.critical("Failed to find compatible model!")

   model = mc.instantiateModel(selected_model)

   request = input('Please tell me what kind of story you want to create: ')

   # "True" indicates that the message is user-sent
   response = model.call([
      f"""A user has made a request to create a story. Here is the user's request:

   {request}

   Please generate a story for the user. Output the story ONLY and NOTHING ELSE.""", True
   ])

   print(f'Here is your story:\n{response}')



In 31 lines of code, we have implemented an application that tells stories with the power of AI.
In the above code, we "enumerate" all available models available on user's platform,
filter out the chat-completion models with the capability (the "**feature**"") of imagination,
select the cheapest model for use, and call the model using the unified interface provided by |project_name|.
In |project_name|, same type of models ("chat-completion" in this case) all use the same interface.


.. toctree::
    :maxdepth: 2
    :caption: Contents
