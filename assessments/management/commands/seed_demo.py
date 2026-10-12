import json
from django.core.management.base import BaseCommand
from assessments.models import Answer, Choice, Question, QuestionSet, Submission

class Command(BaseCommand):
    help = "Reset demo data and create exactly one question of each supported type."

    def handle(self, *args, **options):
        # Demo reset: remove old sets/submissions first so protected question references are gone.
        Answer.objects.all().delete()
        Submission.objects.all().delete()
        QuestionSet.objects.all().delete()
        Question.objects.all().delete()

        q1 = Question.objects.create(
            prompt="Enter the value of the expression: 2.3 · (4 + 12)",
            question_type=Question.Type.MATHLIVE,
            correct_answer="36.8", order=1, is_active=True,
        )

        q2 = Question.objects.create(
            prompt="Which value is equal to 1 1/2 + (-1/2)?",
            question_type=Question.Type.MULTIPLE_CHOICE,
            correct_answer="1", order=2, is_active=True,
        )
        for i, text in enumerate(["-2","-1","0","1"], 1):
            Choice.objects.create(question=q2, text=text, value=text, order=i)

        q3 = Question.objects.create(
            prompt="Move each ordered pair into the correct quadrant on the grid.",
            question_type=Question.Type.DRAG_DROP_IMAGE,
            correct_answer="", order=3, is_active=True,
            drag_config={
                "image":"assessments/coordinate-plane.svg",
                "choices":[
                    {"id":"neg_neg","label":"(−2, −1)"},{"id":"neg_pos","label":"(−2, 1)"},
                    {"id":"pos_neg","label":"(2, −1)"},{"id":"pos_pos","label":"(2, 1)"}],
                "correct":{"neg_neg":"q3","neg_pos":"q2","pos_neg":"q4","pos_pos":"q1"},
            },
        )

        q4 = Question.objects.create(
            prompt="Select all the expressions that are equivalent to 8(t + 4).",
            question_type=Question.Type.MULTI_SELECT,
            correct_answer=json.dumps(["choice_2","choice_5"]),
            order=4, is_active=True,
        )
        choices=[
            "2(4t + 2)",
            "8t + 32",
            "4t + 4 + 4t",
            "(8 + t) + (8 + 4)",
            "(8 × t) + (8 × 4)",
        ]
        for i,text in enumerate(choices,1):
            Choice.objects.create(question=q4, text=text, value=f"choice_{i}", order=i)

        q5 = Question.objects.create(
            prompt="Does replacing the unknown number with 7 make each equation true? Select Yes or No for each equation.",
            question_type=Question.Type.YES_NO_MATRIX, order=5, is_active=True,
        )
        matrix_rows=[("6 × □ = 36",False),("8 × □ = 64",False),("49 ÷ □ = 7",True),("54 ÷ □ = 6",False)]
        expected={}
        for i,(text,yes) in enumerate(matrix_rows,1):
            value=f"row_{i}"
            Choice.objects.create(question=q5,text=text,value=value,order=i)
            expected[value]=yes
        q5.correct_answer=json.dumps(expected)
        q5.save(update_fields=["correct_answer"])

        Question.objects.create(
            prompt="Maya says that a rhombus cannot also be a rectangle.\n\nShow Maya that her statement is not true.\nDraw a rhombus that is also a rectangle.",
            question_type=Question.Type.GRID_LINE_DRAWING, order=6, is_active=True,
            drag_config={"grid_cols":20,"grid_rows":20,"snap":True,"min_lines":1},
        )

        # Keep the Render/PostgreSQL demo data in sync with the newer question types.
        Question.objects.create(
            prompt=(
                "Christy has $60 to spend on plants.\n"
                "She buys a peach tree for $23 and a plum tree for $19.\n\n"
                "She wants to buy one more plant.\n\n"
                "• Drag the numbers to the boxes and the symbols to the circles to create an equation "
                "to show how much money Christy has left to spend.\n\n"
                "• Select one plant she could buy with the money she has left."
            ),
            question_type=Question.Type.EQUATION_BUILDER,
            correct_answer=json.dumps({"slots":["60","−","23","−","19","18"],"plant":"grapevines"}),
            drag_config={
                "operators":["+","−","×","÷"],
                "numbers":["18","19","23","37","41","60","102"],
                "slots":["number","operator","number","operator","number","number"],
                "plants":[["grapevines","Grapevines, $16"],["apple","Apple tree, $18"],["pear","Pear tree, $20"]],
            },
            order=7, is_active=True,
        )

        Question.objects.create(
            prompt="Drag each fraction to the correct location on the number line.",
            question_type=Question.Type.NUMBER_LINE_DRAG,
            correct_answer=json.dumps({"4/1":"4","1/4":"0.25","2/4":"0.5","4/4":"1"}),
            drag_config={
                "min":0,"max":4,"step":0.25,
                "positions":[str(x/4).rstrip("0").rstrip(".") if x % 4 else str(x//4) for x in range(17)],
                "choices":[
                    {"value":"4/1","n":"4","d":"1"},
                    {"value":"1/4","n":"1","d":"4"},
                    {"value":"2/4","n":"2","d":"4"},
                    {"value":"4/4","n":"4","d":"4"},
                ],
            },
            order=8, is_active=True,
        )


        passage = """A Few New Neighbors
by Kerry McGee

One afternoon, Jessie spotted a tiny bird fluttering around Mrs. Baxter’s front door. Mrs. Baxter had just moved into an apartment.

It’s probably looking for somebody to fill the bird feeders, Jessie thought.

The bird perched on the edge of the wreath. Then it disappeared.

Disappeared? Jessie ran over to Mrs. Baxter’s door. Where had it gone?

A jumble of sticks and grass stuck out from the middle of the wreath. Suddenly, Jessie understood. A nest! A bird’s nest sat right in the middle of Mrs. Baxter’s wreath. The bird poked its head out and looked at Jessie. Then it fluttered away.

Jessie crept up to the front door. Tucked inside the nest were four speckled blue eggs.

Jessie ran home to call Mrs. Baxter. “Guess who moved into your old wreath!” Jessie said. “A family of birds!”

Mrs. Baxter sounded just as excited as Jessie was. “Tell me what they look like. What color are the eggs?”

Jessie and Mrs. Baxter talked about the birds for a while. “They sound like house finches,” Mrs. Baxter said. “Keep an eye on them for me, will you?”

“I will,” Jessie said.

And she did. Jessie checked the nest whenever she could. Sometimes the mother finch was there. Other days, the red-headed papa was nearby. Jessie tried to notice everything so she could tell Mrs. Baxter.

One morning, Jessie saw a pink head poking out of the nest. Babies! Jessie strained her neck to get a better look.

Jessie told her dad about the baby birds at Mrs. Baxter’s house.

“That reminds me,” Dad said, “Mrs. Baxter has movers coming tomorrow to clear out the house. I told her I’d unlock the door for them.”

“But what about the nest?”
Dad shook his head. “We’ll just have to tell the movers to be careful.”

Jessie thought about the movers tromping in and out, squeezing heavy boxes and furniture past the tiny nest. She thought about the door swinging and slamming all day long. It seemed risky.

The next morning, Jessie watched the moving truck pull up in front of Mrs. Baxter’s house. Dad saw the truck, too, and came outside with the key.

Jessie jumped up. She ran ahead of the movers and Dad to Mrs. Baxter’s front door. “Wait!” she shouted, spinning around to face them.

Behind her, the mama bird burst out of its nest. It landed in a tree. The movers looked at Jessie in surprise.

“You can’t use this door,” Jessie said, holding her arms out stiff.

“I’m sorry,” one of the movers said. “We have a job to do.”

Jessie didn’t move. “There’s a nest in the wreath,” Jessie explained. “If you open the door, it will fall.”
The other mover sighed, “Do you have any ideas?”

Jessie nodded. “I do have an idea. Dad, can I have the key?”

As carefully as she could, Jessie unlocked the front door and eased it open. When it was just wide enough to slip through, she ducked into Mrs. Baxter’s house.

She’d been in there many times, so it didn’t take her long to find the side door and unlock it from the inside.

“Got it!” Jessie called, running around to the front of the house. “The side door is open!”

One of the movers was peering into the wreath. “Hey,” he said, “There are babies in there.” He grinned at Jessie. “I bet that mama bird is glad you’re watching out for her babies.”

Jessie smiled as she and Dad thanked the movers for their help. Then she ran and disappeared into her own house. She couldn’t wait to call Mrs. Baxter.

“A Few New Neighbors” by Kerry McGee, from Highlights for Children. Copyright © 2013 by Highlights for Children, Inc."""

        Question.objects.create(
            subject=Question.Subject.ENGLISH,
            prompt="Read the sentence and the directions that follow.\n\nChildren and adults can work together.\n\nChoose the two details that best support this conclusion.",
            question_type=Question.Type.PASSAGE_SENTENCE_SELECT,
            correct_answer=json.dumps([2, 3]), order=9, is_active=True,
            drag_config={
                "passage": passage,
                "sentences":[
                    "One afternoon, Jessie spotted a tiny bird fluttering around Mrs. Baxter’s front door.",
                    "Mrs. Baxter had just moved into an apartment.",
                    "Jessie and Mrs. Baxter talked about the birds for a while.",
                    "“They sound like house finches,” Mrs. Baxter said. “Keep an eye on them for me, will you?”"
                ]
            }
        )

        Question.objects.create(
            subject=Question.Subject.ENGLISH,
            prompt="This question has two parts. First, answer part A. Then, answer part B.",
            question_type=Question.Type.PASSAGE_TWO_PART,
            correct_answer=json.dumps({"a":0,"b":3}), order=10, is_active=True,
            drag_config={
                "passage": passage,
                "part_a":{
                    "prompt":"Which sentence best describes the lesson of the passage?",
                    "choices":[
                        {"text":"Animals should be protected.","correct":True},
                        {"text":"Birds should only nest in trees.","correct":False},
                        {"text":"Movers should listen to children.","correct":False},
                        {"text":"Children should stay away from birds.","correct":False}
                    ]
                },
                "part_b":{
                    "prompt":"Which sentence from the passage best supports your answer in part A?",
                    "choices":[
                        {"text":"A bird’s nest sat right in the middle of Mrs. Baxter’s wreath.","correct":False},
                        {"text":"Jessie and Mrs. Baxter talked about the birds for a while.","correct":False},
                        {"text":"One morning, Jessie saw a pink head poking out of the nest.","correct":False},
                        {"text":"‘You can’t use this door,’ Jessie said, holding her arms out stiff.","correct":True}
                    ]
                }
            }
        )

        # Additional questions linked to the same reading passage.
        english_items = [
            (Question.Type.PASSAGE_EVENT_ORDER,
             "Arrange the events from the passage in the order in which they happen.\nChoose the sentences to drag them into the correct locations.",
             {"events": ["Mrs. Baxter moved from her house into an apartment.", "Jessie saw four speckled blue eggs in the nest.", "Jessie unlocked the side door to Mrs. Baxter's house.", "Jessie calls Mrs. Baxter to tell her about the nest.", "The movers arrive to remove Mrs. Baxter's belongings."]}, [0,1,3,4,2]),
            (Question.Type.PASSAGE_CHOICE,
             "Read the sentence from the passage.\n\nA jumble of sticks and grass stuck out from the middle of the wreath.\n\nWhat does the word jumble most likely mean?",
             {"choices": ["a tall pile of items", "a neat pile of items", "a small group of items", "a messy group of items"]}, 3),
            (Question.Type.PASSAGE_MULTI,
             "Why is including dialogue important to understanding the passage? Pick three choices.",
             {"choices": ["It helps the reader understand Jessie’s actions.", "It helps the reader imagine the sounds made by the birds.", "It helps the reader know the reason why Mrs. Baxter moved.", "It helps the reader know how the movers feel about the birds.", "It helps the reader imagine what Jessie will do after the movers leave.", "It helps the reader understand Mrs. Baxter and Jessie’s interest in the birds."]}, [0,3,5]),
            (Question.Type.PASSAGE_CHOICE,
             "Read the sentence from the passage.\n\nAs carefully as she could, Jessie unlocked the front door and eased it open.\n\nWhat does the phrase ‘eased it open’ tell the reader about Jessie?",
             {"choices": ["Jessie is quiet and shy.", "Jessie is able to unlock the door.", "Jessie is nervous to enter the house.", "Jessie is a gentle and thoughtful person."]}, 3),
        ]
        for offset,(kind,prompt,config,correct) in enumerate(english_items,11):
            Question.objects.create(subject=Question.Subject.ENGLISH,prompt=prompt,question_type=kind,correct_answer=json.dumps(correct),order=offset,is_active=True,drag_config={"passage":passage,**config})

        self.stdout.write(self.style.SUCCESS(
            "Question Bank reset: 14 demo questions created (8 Mathematics + 6 English)."
        ))
