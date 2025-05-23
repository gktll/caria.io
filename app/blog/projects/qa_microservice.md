---
title: Benchmark QA Microservice
description: A brief description of the project
date: 2024-02-24
Author: Federico Caria 
tags: [Data, Visualization, LLMs]
image: /static/assets/images/qa_microservice/_card_bkg.png
demo_link: 
github_link: https:www.github.com
technologies: [Python, Streamlit]
summary: A platofrm to streamline the QA process at Baymard Institute.
---

###### Summary
Building a microapp to streamline and enhance our benchmark QA process.

### 1. Introduction
At Baymard Institute, we specialize in heuristic evaluations of e-commerce platforms, using our refined, user-tested heuristics to deliver powerful UX insights. These evaluations are at the heart of our premium data service, helping our subscribers make informed UX decisions. A typical project might include thousands of datapoints:

- Evaluating anywhere from 5 to 60 sites per batch
- Covering desktop, mobile, and app platforms
- Using industry-specific scenarios with weighted evaluations

With such a vast amount of data, things can quickly become overwhelming. In the beginning, we didn’t have a formal QA process—leading to inconsistencies and errors. Over time, we built a structured system involving project owners and peer reviewers. Initially, the process was basic: researchers manually entered raw data into Excel and self-reviewed their work. Later, we introduced peer QA, which improved accuracy but also brought its own set of challenges.

<div class="post-image-grid">
  <figure class="post-image">
     <img src="/static/assets/images/qa_microservice/baymard_benchmark_viz.png" alt="The benchmark dataset visualization at Baymard">
    <figcaption class="post-image-caption">The premium benchmark dataset. The chart contains thousands of datapoints on site performances put together in 15+ years of research.</figcaption>
  </figure>
  <figure class="post-image">
    <img src="/static/assets/images/qa_microservice/baymard_benchmark_spread.png" alt="Second grid image" style="height: 425.5";>
    <figcaption class="post-image-caption">An example of a typical spreadsheet we used for QA, containing thousands of rows.</figcaption>
  </figure>
</div>

#### 1.1. The Problem
What started as a simple quality check became flawed and time consuming:

- Researchers **struggled with massive, unwieldy Excel files**, pushing Google Docs to its limits;
- **Without version control**, people just could not keep track of the changes and often handed obsolete data to peer reviewers;
- The peer QA process, intended to improve quality, often led to reviewers **fixing trivial issues** instead of enhancing evaluations;
- **Time management** was another challenge as reviews followed rigid deadlines rather than adapting to dataset complexity;
- **The process also took a toll on researchers**, making the final stage of evaluation unexpectedly stressful;
- Finally, since the key content we delivered is essentially visual, **correcting data without direct access to visuals made very little sense**.

#### 1.3.  Solution
While system-level improvements (e.g., version control) weren’t prioritized, I decided to leverag my Python skills to create a tool to support the workflow smartly. The starting point was breaking down our manual QA process into discrete checks and automate each one independently. That was a low hanging fruit that could be done in a few hours of pandas. 
Using Google Colab (hoping colleagues could eventually run these themselves), I created a series of focused scripts to handle the serveal use cases we developed, starting from the most basic. Instead of one overwhelming spreadsheet, each of these checks produces its own targeted CSV file that can be reviewed quickly and efficiently. 

Some scripts are remarkably simple, like those checking for null values (we had two paid researchers enjoying this task back in the days!):

```
empty_link_judgement = df[(df['Link to Pin'].isna()) &
    (df['Judgement'] != 'not_applicable') &
    (df['Judgement'] != 'not_rated')
][['ID', 'Website', 'Title', 'Gemini URL']]
empty_link_judgement.to_csv('not_pinned.csv', index=False)
```

Others scripts handle more complex cross-referencing scenarios, eg.

- Cross-platform consistency checks;
- Validation of scoring logic and weights;
- Heuristics alignment; 
- etc.

Here is an example of a filtering .... 

```
df_temp = df.copy()
df_temp['Guideline'] = df_temp['ID'].apply(lambda id: id[:-1] if pd.notna(id) else id)
inconsistencies = []
for (website, guideline), group in df_temp.groupby(['Website', 'Guideline']):
    if group['Judgement'].nunique() > 1:
        judgements = group[['ID', 'Judgement', 'Gemini URL']].to_dict('records')
        inconsistencies.append({'Website': website, 'Guideline': guideline, 'Judgements': judgements})
inconsistencies_df = pd.DataFrame(inconsistencies)
inconsistencies_df.to_csv('judgement_inconsistencies.csv', index=False)
```

Overall, this quick solution turned out to be surprisingly straightforward - what looked like days of manual work could be automated with a a few hours of Pandas. The goal was simple: sketch the skeleton of an automated process that could perform all necessary checks, apply filters, and process textual scenarios to produce streamlined, actionable documents, and potentially much more. This way researchers wouldn't have to lose their minds on excels and above all, that gave a much structured approach to qa logic.  

### Prototype and Test
I am not a fan of long planning for medium sized projects, it is much easier to plan in front of an actionable thing (possibly staying away from Figma). Ideally the kind of prototypes I aim at have all the functions needed to cover most use cases, including the cool ideas one gets while coding and, where data intensive stuff is needed, I fake the interaction with a bit of Js. 

#### 2.1 Automation Script
Questa volta non c'è stato bisogno data la semplicità. 


#### 2.2. Streamlit App
The little program was very well received, even without solving some key issues like version control and lack of visuals. One more hiccup was the lack of confidence with Colab for whcih I had workmates pinging me on Slack everytime the finished a project to bounce the dataset. One day, after collecting yet more compliants for the visuals issue I thought about a simple solution for this. That sounded like another low hanging fruit, it just needed a find the eassies way to deploy a small microapp: that was Streamlit. 

Stremalit is super fast to get up and running, deploy is a walk in the park if one does not aim at super performance and security. Questo si adatava benissimo al nostro caso di avere un tool to make some checks on the go, given that integration seemed not to be a prioprity for the management. Allora ho scelto questa rotta, 

<!-- Two images side by side with captions -->
<div class="post-image-grid">
  <figure class="post-image">
    <img src="/static/assets/images/qa_microservice/stream_home.png" alt="First grid image">
    <figcaption class="post-image-caption">Caption for first image</figcaption>
  </figure>
  <figure class="post-image">
    <img src="/static/assets/images/qa_microservice/stream_downloads.png" alt="Second grid image">
    <figcaption class="post-image-caption">Caption for second image</figcaption>
  </figure>
</div>

### Takeaways
Rather than waiting others, I took action—finding a practical path forward within existing constraints. Sometimes, the best solution isn’t about choosing between multiple options but recognizing the next step and making it happen.







