Device a plan in a new MD file on how can I integrate the agent folder into this application such that:
1. For each room, one facilitator agent and one english feedback agent is registered as the participants in the room. #file:agents 
2. The English feedback agent goes through the transcript of each participant in each turn and provides a private feedback to the participant in text format in a private modal containing instant feedback on the participant's speaking turn.
3. The facilitator agent does the vocal speaking using TTS in its turn. It takes inputs from the feedback generated and saved by the English feedback agent to reflect on some of the highlighted improvements for the participants for that specific turn. It also acknowledges the different points spoken by the participants, finds common grounds and triggers thinking in a suitable direction for the room.
4. The transcripts and feedback tables in the database are the tables with which these agents should be interacting. #file:models 
5. In order to store identity for separate instances of each of these models, we will create another table named agent. It will store :

agent_id TEXT PRIMARY KEY,
                    room_id TEXT NOT NULL,
                    agent_model TEXT NOT NULL, -- Gemini or Bedrock
                    
                    -- Brainstormed Columns
                    agent_type TEXT DEFAULT 'english',
                    status TEXT DEFAULT 'active',
                    system_prompt TEXT,
                    total_interactions INTEGER DEFAULT 0,
                 
                    
                    -- Metadata
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    
                    -- Foreign Key
                    FOREIGN KEY (room_id) REFERENCES rooms (room_id)

6. We will be using Speech to Text service of Chromium browsers to convert the speech of the participants into transcripts and send them to the backend. The #file:speech-recognition.d.ts and #file:SpeechRecognitionTest.tsx are files related to a tested  POC for this feature. 
7. Also, we will be performing Text to speech for the model using the @zoe-ng/tts package. #file:SpeechRecognitionTest.tsx 
8. What APIs and socket interactions need to be built to connect agents to the room conversation seemlessly?
9. Our discussions will be turn-based. We should leverage this feature to navigate through processing delays by starting to process some 15 seconds earlier before facilitator's turn to speak. Private feedback by the English agent can be async after the turn of that specific participant is over (for whom the feedback is generated).
10. At the end, the English feedback agent will speaks by providing a detailed summary based on its gathered feedbacks for each participant. 
LET US FOCUS ONLY ON THE BACKEND SETUP IN THIS CONVERSATION.
