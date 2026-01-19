import os
from dotenv import load_dotenv
from ollama import chat

load_dotenv()

NUM_RUNS_TIMES = 5

# TODO: Fill this in!
YOUR_SYSTEM_PROMPT = """

Task: Your are a string reversing assistant. You have to work at character level within a string which can contain words related to internet. Ensure that reversal is character by character. Only work with lowercase characters. Ensure matches reversal of input. There will be no markers 'Input:" or "Output" in the actual functioning. You can add any character other than those in the input. 

Here are some examples that show Input and output.

Input: http
Output: ptth
Input: https
Output: sptth
Input: status
Output: sutats
Input: dogcat
Output: tacgod
Input: goodman
Output: namdoog
Input: firefly
Output: ylferif
Input: http1s
Output: s1ptth
Input: transportlayer  
Output: reyaltropsnart  
Input: applicationlayer  
Output: reyalyanoitacilppa  
Input: datalinklayer  
Output: reyalknilatad  
Input: physicallayer  
Output: reyalklacisyhp  
Input: sessionlayer  
Output: reyalynoisses  
Input: presentationlayer  
Output: reyalnoitatneserp  
Input: internetprotocol  
Output: locotorptenretni  
Input: controlmessage  
Output: egassemlortnoc  
Input: routingtable  
Output: elbat gnitruor  
Input: domainservice  
Output: ecivresniamod  
Input: firewallpolicy  
Output: ycilopllawerif  
Input: proxyserver  
Output: revresyxorp  
Input: accesscontrol  
Output: lortconsecca  
Input: bittorrent 
Output:  tnerrottib
Input: http2 
Output:  2ptth
Input: hypertexttp
Output:  pttexrepyh
Input: multiproto
Output:  otorpitlum
Input: applications
Output:  snoitacilppa
Input: transmission
Output:  noissimsnart
Input: authentication
Output:  noitacitnehtua
Input: cryptographic
Output:  cihpargotpyrc
Input: virtualization
Output:  noitazilautriv
Input: encapsulated
Output:  detaluspacne
Input: interoperability
Output:  ytilibareporetnI
Input: configuration
Output:  noitarugifnoc
Input: networklayer
Output:  reyalkrowten


"""

USER_PROMPT = """
Reverse the order of letters in the following word. Only output the reversed word, no other text:

httpstatus
"""


EXPECTED_OUTPUT = "sutatsptth"

def test_your_prompt(system_prompt: str) -> bool:
    """Run the prompt up to NUM_RUNS_TIMES and return True if any output matches EXPECTED_OUTPUT.

    Prints "SUCCESS" when a match is found.
    """
    for idx in range(NUM_RUNS_TIMES):
        print(f"Running test {idx + 1} of {NUM_RUNS_TIMES}")
        response = chat(
            model="mistral-nemo:12b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": USER_PROMPT},
            ],
            options={"temperature": 0.5},
        )
        output_text = response.message.content.strip()
        if output_text.strip() == EXPECTED_OUTPUT.strip():
            print("SUCCESS")
            return True
        else:
            print(f"Expected output: {EXPECTED_OUTPUT}")
            print(f"Actual output: {output_text}")
    return False

if __name__ == "__main__":
    test_your_prompt(YOUR_SYSTEM_PROMPT)
