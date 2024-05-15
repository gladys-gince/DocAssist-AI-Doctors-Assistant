import spacy
import re
import pandas as pd

nlp = spacy.load("en_core_web_sm")

input_text = "! Hello Doctor, my name is Gladys. I am 21 years old and female. I have been experiencing persistent cough, high fever and fatigue for the past few days. I got my influenza vaccine a couple of months ago. Hello Gladys, based on your symptoms and recent influenza vaccination, it is likely that you have hypertension. Do you have any underlying health conditions? Are you currently taking any medications? I recently had a bypass surgery. I am regularly taking CTZ tablet. Last time you had prescribed Allegra M tablet. I would prescribe to take shotmax spray every morning and keep an eye on your symptoms. Additionally I recommend a nasal swab test to confirm the hypertension diagnosis and to check for any secondary infections. If there is any worsening, contact our office immediately. Thank you doctor. I will follow your advice and get the nasal swab test done as soon as possible and buy the fist-trap medication."



dataset1 = pd.read_csv('datasets/dataset.csv')
dataset2 = pd.read_csv('datasets/Symptom-severity.csv')
dataset3 = pd.read_csv('datasets/test_surgery.csv')


def extract_medicine_names(input_string, medicine_names):
    pattern = r'\b(?:' + '|'.join(re.escape(name) for name in medicine_names) + r')\b'
    extracted_names = re.findall(pattern, input_string, flags=re.IGNORECASE)
    return extracted_names

def boyer_moore_search(text, pattern):
    last_occurrence = {char: max(1, pattern.rfind(char)) for char in set(pattern)}
    m, n = len(pattern), len(text)
    i = m - 1  # index in the text
    j = m - 1  # index in the pattern

    while i < n:
        if text[i] == pattern[j]:
            if j == 0:
                return True  # Match found
            i -= 1
            j -= 1
        else:
            i += m - min(j, 1 + last_occurrence.get(text[i], -1))
            j = m - 1

    return False  # Pattern not found

def pratham(input_text):
    detected_diseases=''
    detected_surgery=''
    detected_symptoms = []
    detected_tests = []
    output = []

    # Check for diseases and symptoms in the input text
    for index, row in dataset1.iterrows():
        disease = str(row['Disease']).lower()
        if disease in input_text.lower():
            detected_diseases = disease

    # Check for diseases and symptoms in the input text
    for index, row in dataset2.iterrows():
        symptom = str(row['Symptom']).lower()
        if symptom in input_text.lower():
            detected_symptoms.append(symptom)

    # Check for past or potential surgeries in the input text
    for index, row in dataset3.iterrows():
        surgery = str(row['surgery']).lower()
        if surgery in input_text.lower():
            detected_surgery = surgery

    # Check for past or potential tests in the input text
    for index, row in dataset3.iterrows():
        tests = str(row['test']).lower()
        if tests in input_text.lower():
            detected_tests.append(tests)

    detected_symptoms=list(set(detected_symptoms))
    detected_tests = list(set(detected_tests))

    for ent in nlp(input_text).ents:
        if ent.label_ == "PERSON":
            name = ent.text
            age = None
            gender = None

            age_match = re.search(r'\b(\d{1,3})\b\s+years? old', input_text)
            if age_match:
                age = int(age_match.group(1))

            if 'she' in input_text.lower() or 'female' in input_text.lower() or 'girl' in input_text.lower():
                gender = 'Female'
            elif 'he' in input_text.lower() or 'male' in input_text.lower() or 'boy' in input_text.lower():
                gender = 'Male'

            # output.append([detected_diseases, str(detected_symptoms), detected_surgery, str(detected_tests)])

    result = {
       'detected_diseases': detected_diseases,
       'detected_symptoms' : str(detected_symptoms),
       'detected_surgery' : detected_surgery,
       'detected_tests' : str(detected_tests)
    }
    return result

def gladys(input_text):
    # Sample medicines dataset
    medicines_df = pd.read_csv('datasets/A_Z_medicines_dataset_of_India.csv')
    medicines_dataset = list(medicines_df['name'])

    # Immunization dataset
    immunization_df = pd.read_csv('datasets/Immunization.csv', encoding='ISO-8859-1')
    immunization_dataset = list(immunization_df['Vaccine'])

    # Initialize columns
    regular_medicines = []
    last_prescribed_medicines = []
    current_prescribed_medicines = []
    immunization_history = []

    # Split the text into sentences
    sentences = [sentence.lower() for sentence in input_text.split('. ')]

    # Iterate through the sentences
    for sentence in sentences:
        # Check for regular, last prescribed, and current prescribed medicines
        if "regularly taking" in sentence:
            medicine = extract_medicine_names(sentence,medicines_dataset)
            for i in medicine:
                regular_medicines.append(i)
        elif "last time" in sentence:
            medicine = extract_medicine_names(sentence,medicines_dataset)
            for i in medicine:
                last_prescribed_medicines.append(i)

    
        else:
            medicine = extract_medicine_names(sentence,medicines_dataset)
            for i in medicine:
                current_prescribed_medicines.append(i)
        # Check for immunization
            immunization = extract_medicine_names(sentence,immunization_dataset)
            for i in immunization:
                immunization_history.append(i)


    # Convert sets to lists
    regular_medicines = list(regular_medicines)
    last_prescribed_medicines = list(last_prescribed_medicines)
    current_prescribed_medicines = list(current_prescribed_medicines)
    immunization_history = list(immunization_history)

    result = {
        'regular_medicines' : regular_medicines,
        'last_prescribed_medicines' : last_prescribed_medicines,
        'current_prescribed_medicines' : current_prescribed_medicines,
        'immunization_history' : immunization_history
    }

    return result

# res1 = pratham(input_text)
# print(res1)
""" res2 = gladys(input_text)
print(res2) """