class PromptFormatter():
    def format_instruction(self, instruction_dict):
        instruction_prompt = "Instructions:\n"
        for key, value in instruction_dict.items():
            instruction_prompt += f"{key}: {value}\n"
        return instruction_prompt

    def format_history(self, history):
        history_prompt = "History:\n"
        for i, entry in enumerate(history):
            history_prompt += f"{i}:\n"
            for entity, response in entry.items():
                history_prompt += f"{entity}: {response}\n"
        return history_prompt

    def format(self, query, **kwargs):
        instruction_prompt = ""
        history_prompt = ""
        if "instruction_dict" in kwargs:
            instruction_dict = kwargs["instruction_dict"]
            # print("instruction recieved >>", instruction_dict)
            assert type(instruction_dict) is dict, "Instruction should be a dictionary"
            instruction_prompt = self.format_instruction(instruction_dict)
            # print("instruction_prompt >>", instruction_prompt)

        if "history" in kwargs:
            history = kwargs["history"]
            assert type(history) is list, "History should be a list of dictionaries"
            history_prompt = self.format_history(history)
        
        query = f"""Final Query: {query}"""
        final_prompt = f"{instruction_prompt}\n{history_prompt}\n{query}"

        return final_prompt 