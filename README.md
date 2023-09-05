# **ChatPSY_demo**
目前虽然有类似于心理咨询的应用，但只能输出一些机械式的结果：如找专业心理咨询师，多锻炼等，这会使得用户产生不信任感，因为并没有像医院一样提供一些必要的辅助诊断。因此，我们的应用将会利用医院常用的精神量表进行打分，提供一些有参考意义的结果。<br />
该应用用途将十分广泛，因为现代人不分工作，不分场景，或多或少会有精神上的问题，如焦虑，失眠，排除生理性的病患，更多的是心理上的问题。因此，一个初步的诊断结果对于那些犹豫是否去医院检查的人来说，将会十分有帮助。<br />
****
**功能1**：针对用户提出所要咨询的精神疾病，给予详细的介绍与科普。<br />
**功能2**：对于某一类（可能有精神隐患）用户，根据其填写的量表结果，给予诊断。<br />
**功能3**：针对患病程度较轻的用户，提供有效的治疗建议；而对于较严重的用户，应建议去医院接受更多治疗。<br />
****
**初步方案**：通过星火大模型的API接口，结合langchain的内存缓存，进行Few-shot prompting，最后通过huggingface里的gradio进行部署。<br />
****




![1693897473420](https://github.com/ggg1160195735/ChatPSY_demo/assets/144097755/e543963c-e954-49e0-b98d-8c4c3c017ead)
