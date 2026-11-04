from django import forms
from django.forms import inlineformset_factory
from .models import Choice, Question, QuestionSet

class QuestionSetCreateForm(forms.Form):
    title = forms.CharField(label="Question set title", max_length=200, initial="", required=False)
    questions = forms.ModelMultipleChoiceField(label="Select questions", queryset=Question.objects.none(), widget=forms.CheckboxSelectMultiple)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["questions"].queryset = Question.objects.filter(
            is_active=True,
            question_type__in=[
                Question.Type.MAP_ARRAY_INPUT,
                Question.Type.MAP_IMAGE_CHOICE,
                Question.Type.MAP_NUMBER_SYMBOL,
                Question.Type.MATHLIVE,
                Question.Type.MULTIPLE_CHOICE,
                Question.Type.MULTI_SELECT,
                Question.Type.YES_NO_MATRIX,
                Question.Type.GRID_LINE_DRAWING,
                Question.Type.EQUATION_BUILDER,
                Question.Type.NUMBER_LINE_DRAG,
                Question.Type.DRAG_DROP_IMAGE,
                Question.Type.PASSAGE_SENTENCE_SELECT,
                Question.Type.PASSAGE_TWO_PART,
                Question.Type.PASSAGE_EVENT_ORDER,
                Question.Type.PASSAGE_CHOICE,
                Question.Type.PASSAGE_MULTI,
            ],
        ).prefetch_related("choices")
    def save(self):
        question_set = QuestionSet.objects.create(title=self.cleaned_data["title"])
        for index, question in enumerate(self.cleaned_data["questions"]):
            question_set.items.create(question=question, order=index)
        return question_set

class TeacherQuestionForm(forms.ModelForm):
    subject = forms.ChoiceField(label="Subject", choices=Question.Subject.choices)
    drag_values = forms.CharField(
        label="Draggable Values", required=False,
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "(-2,-1); (-2,1); (2,-1); (2,1)"}),
        help_text="Separate ordered pairs with semicolons or newlines. Plain values may be comma-separated (e.g. 1,1,1,1).",
    )
    map_directions = forms.CharField(label="Directions", required=False, initial="Use the information to answer the question.")
    map_description = forms.CharField(label="Description", required=False, widget=forms.Textarea(attrs={"rows":2}))
    map_array_image = forms.ImageField(label="Array image (upload in Edit)", required=False)
    map_image_a = forms.ImageField(required=False)
    map_image_b = forms.ImageField(required=False)
    map_image_c = forms.ImageField(required=False)
    map_image_d = forms.ImageField(required=False)
    map_image_e = forms.ImageField(required=False)
    passage_text = forms.CharField(label="Passage", required=False, widget=forms.Textarea(attrs={"rows":12,"placeholder":"Paste the reading passage here."}))
    selectable_sentences = forms.CharField(label="Selectable sentences", required=False, widget=forms.Textarea(attrs={"rows":6,"placeholder":"One selectable sentence per line."}))
    part_a_prompt = forms.CharField(label="Part A prompt", required=False, widget=forms.Textarea(attrs={"rows":3}))
    part_b_prompt = forms.CharField(label="Part B prompt", required=False, widget=forms.Textarea(attrs={"rows":3}))
    part_a_choices = forms.CharField(label="Part A choices", required=False, widget=forms.Textarea(attrs={"rows":5,"placeholder":"One choice per line; prefix correct choice with *"}))
    part_b_choices = forms.CharField(label="Part B choices", required=False, widget=forms.Textarea(attrs={"rows":5,"placeholder":"One choice per line; prefix correct choice with *"}))
    question_type = forms.ChoiceField(label="Question Type", choices=[
        (Question.Type.MAP_ARRAY_INPUT, "MAP Array Numeric Input"),
        (Question.Type.MAP_IMAGE_CHOICE, "MAP Image Choice (A–E)"),
        (Question.Type.MAP_NUMBER_SYMBOL, "MAP Number & Symbol Placement"),
        (Question.Type.MATHLIVE, "Value Input"),
        (Question.Type.MULTIPLE_CHOICE, "Multiple Choice"),
        (Question.Type.MULTI_SELECT, "Multi-select"),
        (Question.Type.YES_NO_MATRIX, "Yes / No Matrix"),
        (Question.Type.GRID_LINE_DRAWING, "Grid Line Drawing"),
        (Question.Type.EQUATION_BUILDER, "Equation Builder"),
        (Question.Type.NUMBER_LINE_DRAG, "Number Line Drag"),
        (Question.Type.DRAG_DROP_IMAGE, "Drag and Drop Image"),
        (Question.Type.PASSAGE_SENTENCE_SELECT, "Passage Sentence Select"),
        (Question.Type.PASSAGE_TWO_PART, "Passage Two-Part (A/B)"),
        (Question.Type.PASSAGE_EVENT_ORDER, "Reading Event Sequencing"),
        (Question.Type.PASSAGE_CHOICE, "Reading Multiple Choice"),
        (Question.Type.PASSAGE_MULTI, "Reading Multiple Select"),
    ])
    class Meta:
        model = Question
        fields = ["subject", "question_type", "prompt", "correct_answer", "is_active"]
        labels = {"prompt":"Question Text","correct_answer":"Correct Answer","is_active":"Available in Question Bank"}
        widgets = {
             "prompt": forms.Textarea(attrs={"rows":5,"placeholder":"Enter the question text students will see."}),
            "correct_answer": forms.TextInput(attrs={"placeholder":"Example: 36.8","autocomplete":"off"}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cfg = self.instance.drag_config or {} if self.instance and self.instance.pk else {}
        if self.instance.question_type == Question.Type.DRAG_DROP_IMAGE:
            existing = cfg.get("choices") or []
            self.fields["drag_values"].initial = "; ".join(str(c.get("label", "")) for c in existing if isinstance(c, dict)) if existing else "(-2,-1); (-2,1); (2,-1); (2,1)"
        self.fields["map_directions"].initial = cfg.get("directions", "Use the information to answer the question.")
        self.fields["map_description"].initial = cfg.get("description", "")
        self.fields["passage_text"].initial = cfg.get("passage", "")
        
        try:
            correct_sentence_indexes = set(__import__("json").loads(self.instance.correct_answer or "[]")) if self.instance.question_type == Question.Type.PASSAGE_SENTENCE_SELECT else set()
        except Exception:
            correct_sentence_indexes = set()
        self.fields["selectable_sentences"].initial = "\n".join(("*" if i in correct_sentence_indexes else "") + x for i,x in enumerate(cfg.get("sentences", [])))
        self.fields["part_a_prompt"].initial = cfg.get("part_a", {}).get("prompt", "")
        self.fields["part_b_prompt"].initial = cfg.get("part_b", {}).get("prompt", "")
        def lines(part):
            out=[]
            for c in cfg.get(part, {}).get("choices", []): out.append(("*" if c.get("correct") else "") + c.get("text", ""))
            return "\n".join(out)
        self.fields["part_a_choices"].initial = lines("part_a")
        self.fields["part_b_choices"].initial = lines("part_b")

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("question_type") == Question.Type.DRAG_DROP_IMAGE:
            import re
            raw = (cleaned.get("drag_values") or "").strip()
            # Semicolon/newline delimiters allow coordinate pairs to contain commas.
            if ";" in raw or "\n" in raw:
                labels = [v.strip() for v in re.split(r"[;\n]+", raw) if v.strip()]
            else:
                # A sequence of ordered pairs is also supported without semicolons.
                pairs = re.findall(r"\(\s*[+-]?\d+(?:\.\d+)?\s*,\s*[+-]?\d+(?:\.\d+)?\s*\)", raw)
                if pairs and not re.sub(r"\(\s*[+-]?\d+(?:\.\d+)?\s*,\s*[+-]?\d+(?:\.\d+)?\s*\)|[\s,]+", "", raw):
                    labels = pairs
                else:
                    labels = [v.strip() for v in raw.split(",") if v.strip()]
            if not labels:
                labels = ["(-2,-1)", "(-2,1)", "(2,-1)", "(2,1)"]
            if len(labels) != 4:
                self.add_error("drag_values", "Enter exactly four draggable values for the four quadrants.")
            cleaned["parsed_drag_values"] = labels
        if cleaned.get("question_type") == Question.Type.MAP_ARRAY_INPUT:
            if cleaned.get("subject") != Question.Subject.MATH_MAP:
                self.add_error("subject", "Array Numeric Input must use Math (MAP).")
            if not (cleaned.get("correct_answer") or "").strip().isdigit():
                self.add_error("correct_answer", "Enter the numeric correct answer, e.g. 12.")
        if cleaned.get("question_type") == Question.Type.MAP_IMAGE_CHOICE:
            if cleaned.get("subject") != Question.Subject.MATH_MAP:
                self.add_error("subject", "MAP Image Choice must use Math (MAP).")
            if (cleaned.get("correct_answer") or "").upper() not in ("A", "B", "C", "D", "E"):
                self.add_error("correct_answer", "Choose A, B, C, D, or E.")
        if cleaned.get("question_type") == Question.Type.MAP_NUMBER_SYMBOL:
            if cleaned.get("subject") != Question.Subject.MATH_MAP:
                self.add_error("subject", "Number & Symbol Placement must use Math (MAP).")
            if not (cleaned.get("correct_answer") or "").strip():
                self.add_error("correct_answer", "Enter the correct answer, for example 17¢.")
        if cleaned.get("question_type") == Question.Type.MATHLIVE and not (cleaned.get("correct_answer") or "").strip():
            self.add_error("correct_answer", "Enter the correct value.")
        return cleaned

class ChoiceForm(forms.ModelForm):
    is_correct = forms.BooleanField(required=False, label="Correct")
    class Meta:
        model = Choice
        fields = ["text", "value", "order"]
        widgets = {"text":forms.TextInput(attrs={"placeholder":"Answer choice"}),"value":forms.HiddenInput(),"order":forms.HiddenInput()}

ChoiceFormSet = inlineformset_factory(Question, Choice, form=ChoiceForm, extra=0, can_delete=True)
