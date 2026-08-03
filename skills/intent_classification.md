# Intent Classification Micro-Skill

## Overview
Intent classification is a crucial component in understanding and processing user inputs in conversational systems. This micro-skill covers two primary methods for classifying user intents: **Regex-based classification** and **Natural Language Processing (NLP)-based classification**. Combining these approaches allows for robust intent recognition across a variety of input formats and complexities.

## 1. Regex-Based Intent Classification

### Description
Regex-based intent classification involves defining patterns using regular expressions to match specific command patterns in user input. This method is particularly effective for identifying commands with a clear and consistent structure, such as `/start`, `/help`, or `/search`.

### Implementation Steps
1. **Define Command Patterns**: Create a list of regex patterns that correspond to different commands or intents.
2. **Match User Input**: Use these patterns to scan the user input and identify matches.
3. **Map to Intents**: Once a match is found, map it to the corresponding intent or action.

### Example Code
```python
import re

# Define regex patterns for different commands
command_patterns = {
    'start': r'^/start\s*$',
    'help': r'^/help\s*$',
    'search': r'^/search\s+(.+)$'
}

def classify_intent_regex(user_input):
    for intent, pattern in command_patterns.items():
        if re.match(pattern, user_input):
            return intent
    return 'unknown'
```

### Error Prevention
- **Case Sensitivity**: Use `re.IGNORECASE` if commands can be in different cases.
- **Anchors**: Use `^` and `$` to ensure the entire input matches the pattern.
- **Escaping Special Characters**: Escape any special characters in commands to avoid regex errors.

### Example Usage
```python
user_input = "/search python"
intent = classify_intent_regex(user_input)
print(intent)  # Output: search
```

## 2. NLP-Based Intent Classification

### Description
NLP-based intent classification leverages natural language processing techniques to understand and categorize user intents based on the semantic meaning of their input. This method is more flexible and can handle a wider range of input variations and complexities.

### Implementation Steps
1. **Preprocessing**: Tokenize and preprocess the user input to prepare it for analysis.
2. **Keyword Matching**: Identify keywords or phrases that are indicative of specific intents.
3. **Semantic Analysis**: Use techniques like word embeddings or machine learning models to understand the context and meaning of the input.
4. **Intent Mapping**: Map the analyzed input to the corresponding intent or action.

### Example Code
```python
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string

# Define keyword mappings for intents
intent_keywords = {
    'ocr': ['ocr', 'optical character recognition'],
    'translate': ['translate', 'translation', 'english', 'spanish', 'french']
}

def classify_intent_nlp(user_input):
    tokens = word_tokenize(user_input.lower())
    tokens = [word for word in tokens if word not in stopwords.words('english') and word not in string.punctuation]
    
    for intent, keywords in intent_keywords.items():
        for keyword in keywords:
            if keyword in tokens:
                return intent
    return 'unknown'
```

### Error Prevention
- **Tokenization**: Ensure proper tokenization to handle punctuation and special characters.
- **Stop Words**: Remove stop words to improve matching accuracy.
- **Case Normalization**: Convert input to lowercase to ensure case-insensitive matching.
- **Partial Matches**: Be cautious with partial matches to avoid false positives.

### Example Usage
```python
user_input = "Please help me OCR this document"
intent = classify_intent_nlp(user_input)
print(intent)  # Output: ocr
```

## Integration of Both Methods

### Combined Classification Strategy
To achieve a more comprehensive intent classification system, integrate both regex-based and NLP-based methods. This approach leverages the strengths of each method:

1. **Initial Regex Check**: First, apply regex patterns to quickly identify explicit commands.
2. **Fallback to NLP**: If no regex match is found, use NLP techniques to analyze the input for more complex or varied intents.

### Example Code
```python
def classify_intent(user_input):
    intent = classify_intent_regex(user_input)
    if intent != 'unknown':
        return intent
    else:
        return classify_intent_nlp(user_input)
```

### Example Usage
```python
user_input1 = "/start"
user_input2 = "I need to translate this to English"
print(classify_intent(user_input1))  # Output: start
print(classify_intent(user_input2))  # Output: translate
```

## Conclusion
By combining regex-based and NLP-based intent classification, you can create a robust system capable of handling a wide range of user inputs. This integrated approach ensures that both explicit commands and more nuanced, context-dependent intents are accurately identified and processed.