<p align="center" style="margin: 10px;">
    <img src="docs/n8n.webp" alt="n8n Logo" width="20%" style="padding:8px;">
    <img src="docs/Instagram_logo_2016.svg.webp" alt="Instagram Logo" width="20%" style="padding:8px;">
</p>


# Agentic AI Instagram Scraper

Self hosted AI workflow for scraping instagram reels (audio and description), extracting, summaries, and categories, then stored for quick viewing later.

While planning an upcoming trip to Bali, I found myself endlessly watching Reels with recommendations: Where to eat, where to stay, travel tips, safety advice, but I was never revisiting them. So I decided to see if I could try build a self-hosted, agentic AI pipeline to organize that information automatically! Here’s how it works:

- Submit Reels to scrape as a link in a Google form.
- Scrapes the description and transcribe the audio.
- Extracts and categorise the information with a AI LLM
- Saves the research in the relevant categories google sheet

<br>
<p align="center"><img src="docs/demo%20full.gif" alt="Reel URL Form" width="90%"></p>

## Technologies:

The workflow was built with a tool called n8n, a low code/no code agentic workflow building tool. I combined this with a python library called Instaloader to scrape the reel video and description while the video was transcription was done with OpenAI’s Whisper python library.


- **n8n** A low-code workflow orchestrator  
- **Instaloader** Python library for scraping Instagram content served with Flask 
- **OpenAI Whisper** Local audio-to-text transcription served with Flask  
- **LLMs** GPT-4.1-mini, also explored self-hosted models with OLlama  
- **Docker & Docker Compose** Simple containerised deployment for my home server  
- **Google Sheets API** Data storage and trigger source

## Workflow Walk-through

### 1. Submit Reel URL  
A Google Form collects new Reel links, feeding into a “Form responses” sheet. n8n polls this sheet every 5 minutes for new entries. For simplicity the user just ticks if they want audio transcription. A "Scraped" coloumn in the table stops rescrapping.

<p align="center"><img src="docs/Bali Reels Input Form.png" alt="Reel URL Form" width="60%"></p>

### 2. Scrape Reel  
Next Instaloader downloads the video and description saving the video localy for later transcription. This service was containerised and served with Flask for modularity and reusability. 

### 3. Optionalionaly Transcribe Audio  
If the user selected to “Scrape Audio?” in the form we transcribe the audio of the downloaded video. A libarary called fast-whisper based on openAIs Whisper transcribes was used and im impressed with its speed an accuracy on my home servers cpu.

<p align="center"><img src="docs/Transcript Node UI.png" alt="Whisper Node" width="70%"></p>

### 4. AI Information Extraction  
The combined description + transcript is sent to an LLM with a prompt that:
- Identifies each actionable item.
- Assigns exactly one of:  
  - Food & Drink
  - Accommodations
  - Activities & Attractions
  - Info & Other  
- Outputs valid JSON matching the required schema.

<p align="center"><img src="docs/Transcript AI Output Node UI.png" alt="AI Output Node" width="70%"></p>


<details>

<summary> System Prompt: ...</summary>

```
You are an expert at reading social-media content and extracting structured data. We are going on holiday and this is research.

• Identify every distinct piece of actionable information in the description and transcript (e.g., a hotel mention, a restaurant, a safety tip) and output each as a separate items[] entry.
• Assign each entry exactly one category: "Food & Drink", "Accommodations", "Activities & Attractions", or "Info & Other". 
• These are the catagories and their descriptions
- - Food & Drink are **ONLY spesific locations to eat and drink** e.g "Sam's beach bar bali". The type is: "Restaurants", "Cafes" etc 
- - Accommodations is places to stay: Hotels, Hostles, etc
- - Activities & Attractions are things to do: Bars, Beaches, Clubs, Snorkling etc
- - Info & Other are pices of infomation, often includes tips and tricks etc
• Take into context the rest description and transcript for categorising each item. E.g If the whole content is about "10 Safety Tips", all items will likely be "Info & Other" catergory
• For each category, include only the sheet-specific fields plus a notes field that may be as long as needed to capture all relevant details.
• Do not invent extra keys or categories.
• Return only valid JSON matching the schema.
```

</details>



### 5. Save to Google Sheets  
n8n loops over each JSON item and, via a Switch node, routes it to the appropriate sheet tab. A brief Wait node handles API rate limits.

<p align="center"><img src="docs/Scraped Info & Other.png" alt="AI Output Node" width="70%"></p>


## Results


Overall im quite impressed with the results. This is the results from about 20 scrape reels totalling about 2p in cost. I am impressed with the amount of infomation extracted. The info is only as good as the video it comes from but the AI was generaly very good at seporating and summarising the info. It struggled a bit sometimes with catagorising, I especaly had issue with food and drink hygeen tips being put in Food & Drink but I didnt spend long on prompt engineering and im sure I could have achived better results here with some expermentation.

<p align="center"><img src="docs/Scraped Activites & Atttractions.png" alt="AI Output Node" width="70%"></p>

Row 6 in the Scraped Info & Other, for example, seems to be a Tour Contact advert. And some of the entries above arent very descriptive. 

However building up this database in info has allow me to see what info pops up a lot, especaly good for place recomendations. Ultimatly this data will most likely be most usefull put back into a more powerfull LLM such as GPT4o to cleanup and further summaries. 

### Self-hosted VS Cloud LLMs

I tried a veriaty of models selfhosted and through api tokens. I found ChatGPT-4.1-nano struggled with catagorisation so switch to the mini model for a compramise of cost and accuracy. I tried Self hosted models such as TinyLLama which ran well ok my server's cpu but wasnt very accurate. Llama 3.1 with about 4B tokens worked ok on my PC's gpu but was too slow on my servers cup. Overall I found this model to also struggle with classification a little as well as sticking to the json schema.

## Challenges

No project is worth it without some challengase. While this went relativly sommthle these were some of the sticking points:

### AI Limitations: 
Occasionally, even GPT-4.1-mini struggled with accurate categorization, especially with foreign names and locations. It sometimes mistook adverts as relevant content.

### Self-Hosting
Though n8n offers a cloud-hosted option, I opted for self-hosting primarily for three reasons:

- **Cost Efficiency:** I wanted to avoid ongoing subscription costs even though it seems n8n has a generous free tier.
- **Learning:** Hosting it myself offered opportunities to deepen my understanding of networking, server management
- **Privacy:** data privacy, not so much necessary for this, but maybe for future other projects.

Initial setup of n8n was straightforward using Docker Compose, although configuring the network infrastructure to securely expose the services to the internet (necessary for connecting with Google Sheets APIs) was a bit fiddly. Ironicaly, it became as much a DevOps and networking project as it was an AI endeavour. Overall though I would defo recommend it as it was a lot of fun to self-host and a good learning exercise.

### Research Is Only As Good As Your Data
When i paid colser attention picking reels to scraper it did hilight how many were mostly just advatising or the same advice repeated. Finding good reels to scrape became more difficult than getting the infomation from them.

## Thoughts On n8n

### Pros:
- Visual interface for quickly seeing and undersanding your workflows.
- Visual debugging tools made testing very easy.
- Lots of prebuilt tools and integrations.

### Cons:

- Node interface sometimes feels more tedious than hand-coding.
- Large workflows quickly become cumbersome.

The primary goal of this project was to experiment with n8n and have a go with this seeminly fun visual tool to harnis the wonders of AI. While I enjoyed it I dont think this low code/no code tool is quite aimed at at me and I am looking into other code solutions such as Langcain and Langgraph for future projects.
