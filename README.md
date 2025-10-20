# An LLM powered Agile Workflow Assistant 
### Created by Nithin Gandhi Simanand as a Master's Project
---
## Problem Statement and Motivation

Enterprise-scale organisations routinely operate across a complex matrix of interdependent projects, movement across teams, and extensive resource portfolios.
To maintain operational coherence and deliver value efficiently these firms typically rely on structured project management frameworks such as PRINCE2, PMBOK, or Agile-based hybrids. 
While such methodologies have demonstrated clear benefits in improving project visibility, governance, and stakeholder alignment, they remain susceptible to inherent inefficiencies. 
These stem largely from the rigidities of hierarchical communication, bureaucratic inertia, and the sheer scale of coordination required in large corporate environments.

Despite adherence to best practices, many firms continue to experience avoidable project delays, resource misallocation, and suboptimal decision-making cycles. 
A significant portion of these inefficiencies can be traced to human limitations in managing high-dimensional data, repetitive administrative tasks, and the cognitive overload associated with large-scale project orchestration. 
This presents a critical bottleneck: even with mature frameworks in place, enterprise project management often lacks the real-time adaptability and computational agility required to fully optimise performance at scale.

The emergence of Large Language Models (LLMs) and Machine Learning (ML) systems offers a transformative opportunity to address these structural inefficiencies. 
These technologies excel at pattern recognition, predictive analysis, and automating low-level cognitive functions, all attributes that align closely with the pain points of modern project management. 
By offloading repetitive, computation-heavy, and data-intensive components of project workflows to intelligent systems, organisations can enable human stakeholders to concentrate on strategic, creative, and high-context tasks where human judgment is irreplaceable.

However, due to the ever-growing importance of data protection, firms are increasingly hesitant to integrate cloud-based AI providers into their workflows. 
Concerns surrounding the ambiguity of how data is processed, where it is transmitted, and which datasets were used to train these models have created a significant barrier to adoption. 
While some organisations attempt to mitigate this risk by deploying locally hosted LLMs, these models typically function as open-ended chatbots. 
Consequently, the quality and relevance of their outputs are highly dependent on the user's ability to craft precise, context-aware prompts. 
Given the diversity in LLM interfaces, capabilities, and task specialisation, employees without training in prompt engineering or a deep understanding of model behavior often struggle to extract meaningful value, effectively neutralising the potential gains these tools could offer.

This research is motivated by the need to bridge the gap between the theoretical capabilities of intelligent automation systems and their practical usability in real-world enterprise settings. 
The core problem lies not only in technical implementation, but also in aligning these systems with organisational workflows, ensuring security and compliance, and designing interfaces and processes that make advanced tools accessible to non-expert users.
The goal is to explore how LLM- and ML-driven solutions can be securely, effectively, and intuitively integrated into large-scale project environments enabling genuine improvements in efficiency, responsiveness, and decision quality as well as ensuring projects are deliveres on time without compromising data integrity or overwhelming the workforce.

## Current State of Affairs

The aim for the project was simple. To test whether it is possible to create an app(lication) that deals with all the boring, time consuming, administrative work that relies very heavily on tasks such as optimisation to assist in the "traditional agile workflow". 
In short, it should allow employees to just do their jobs instead of spending their time planning to do their jobs.
A very basic UI was created using QT python
A db was created 
A variety of LLM models were used and to do an "extensive smoke test". Essentially, testing enough to demonstrate that it's possible but not with enough sample size to provide any meaningful figures on efficacy. 
This was mostly due to a time limitation.

## Where next?

The next stages would be to nail down a model. Switching between deepseek and ollama has shown that there's a clear difference in their capabilities and responses, not even considering the number of parameters. Further testing will allow me to pick *one* model that is most suited for this program...  for now. 
The final product should still be modular in design, with users given a choice of which model they would like to use/ different models being employed for different tasks.

Following this, the full *command palette* should be decided. As this is ***NOT*** a chat bot, users have a predestined list of things that they can do in the program. All of these should be noted so that the corresponding prompts can be created. Advanced users can potentially be given a greater degree of control but the intention is to ensure that it is not possible to get a bad result due to poor prompting.

The interface needs to be updated. QTPython was fantastic as a temporary solution to the problem. It allowed me to quickly create the pages I needed, do some UI adjustments, connect to the backend and demonstrate the capabilities for the master's. However, it simply isn't modern enough or slick enough for a LLM powered app created in 2025...

Networking capabilities need to be added. Having a central processor to run the models for more intensive tasks greatly reduces the lag experienced by the user as well as ensures that resources are effectively utilised. While the testing done for the master's demonstrated that all the main functionalities could be performed on an Intel i7-9750H Laptop CPU with no GPU assistance, no NPUs, 16gb of RAM and with other background tasks running, Increasing complexity of the prompts, context and number of parameters could prove too much. The focus is still very much privacy first, no internet or cloud based LLM tools and no moving data outside of the user's control.
