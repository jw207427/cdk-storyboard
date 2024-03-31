class PromptTemplate:
    def __init__(self):
        self.template = ""

    def set_template(self, template):
        self.template = template

    def get_template(self):
        return self.template

    def get_scenes_template(self):

        template = """
            Human: You are an award wining director, create number of scenes from the <StoryIdea> for storyboarding. 
            <StoryIdea>
            {idea}
            </StoryIdea>

            When you reply, first generate the scene description inside <Scenes></Scenes> XML tags for each scene. No explanation needed.
            This is a space for you to write down ideas and will not be shown to the user.  
            Once you are done with the scenes, describe a image that best represent that scene. Following the following <format> for the final response:

            <format>
            [
            {"scene": 1, "description": "A young girl is in the kitchen, rummaging through the pantry, looking for a snack. She hears a strange noise coming from the back of the pantry and becomes startled.", "imagery": "A dimly lit pantry with shelves stocked with various food items, and a young girl peering inside, her face expressing curiosity and a hint of fear." },
            {"scene": 2, "description": "The girl grabs a broom and cautiously approaches the back of the pantry, ready to confront whatever is making the noise. She slowly opens the door, and a small figure darts out, knocking over a few cans.", "imagery": "A close-up shot of the girl's determined face, holding a broom like a weapon, with a shadowy figure darting out from the pantry, causing a commotion." },
            {"scene": 3, "description": "The girl drops the broom and bursts out laughing at the absurdity of the situation. Her brother joins in, and they both collapse on the floor, giggling uncontrollably.", "imagery": "The girl and her brother sitting on the kitchen floor, surrounded by the mess they've created, holding their stomachs and laughing heartily." },
            ...
            ]
            </format>

            The theme of the story is {theme}. Please generate {number} scenes that describe the end-to-end story. Given me the final response ONLY. do not share the <Scenes>
            
            Assistant:
            """

        return template