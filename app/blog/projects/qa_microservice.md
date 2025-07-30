---
title: Benchmark QA Microservice
description: A brief description of the project
date: 2024-02-24
Author: Federico Caria 
tags: [Data, Visualization, LLMs]
image: /static/assets/images/qa_microservice/_card_bkg.png
demo_link: 
github_link: https:www.github.com
technologies: [Python, Streamlit, Flask, Html/CSS, Bootstrap, JavaScript]
summary: A platofrm to streamline the QA process at Baymard Institute.
---

###### Summary
Built a data processing microservice to automate and enhance quality assurance workflows for e-commerce UX evaluation datasets containing thousands of datapoints.


### 1. Introduction
At Baymard Institute, we conduct heuristic evaluations of e-commerce platforms, generating massive datasets with thousands of evaluation points across multiple sites and platforms. Our QA process had become a bottleneck:

- **Data overwhelm:** Researchers struggled with unwieldy Excel files containing thousands of rows
- **Version control issues:** No tracking of changes, leading to obsolete data being passed between reviewers
- **Inefficient reviews:** Peer reviewers focused on trivial fixes rather than meaningful quality improvements
- **Visual disconnect:** Correcting evaluation data without access to the actual UI screenshots made little sense

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

### 2 Solution
I developed a three-phase solution to transform our manual QA workflow into an automated, visual-first process.

#### 2.1 Google Colab Exploration (Phase 1)
Started by breaking down our manual QA process into discrete, automatable checks. Created focused Python scripts to handle specific validation scenarios:

```
empty_link_judgement = df[(df['Link to Pin'].isna()) &
    (df['Judgement'] != 'not_applicable') &
    (df['Judgement'] != 'not_rated')
][['ID', 'Website', 'Title', 'Gemini URL']]
empty_link_judgement.to_csv('not_pinned.csv', index=False)
```

More omplex cross-referencing scenarios, eg.

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

Each script exported targeted CSV files for specific review tasks, replacing one overwhelming spreadsheet with manageable, focused datasets.


#### 2.2 Streamlit Prototype (Phase 2)
The Colab scripts were well-received but required technical knowledge to run. To democratize access, I built a Streamlit web app that:

- Automated all validation checks through a simple file upload interface
- Generated downloadable CSV reports for each validation category
- Provided immediate visual feedback on data quality issues
- Eliminated the need for colleagues to run code manually

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


#### 2.3 Flask Application (Phase 3) 
Expanding the prototype into a full-featured Flask application with:

- **Visual review interface**: Direct integration with UI screenshots for context-aware data correction
- **Collaborative workflows**: Multi-user support with role-based permissions
- **Advanced analytics**: Quality metrics and trend analysis across projects
- **API integration**: Seamless connection with existing data pipelines

### 3. Technical Implementation
Data Processing: Pandas for efficient dataset manipulation and validation logic
Web Framework: Streamlit for rapid prototyping, Flask for production scaling
Deployment: Cloud-based hosting with automated CI/CD pipeline
Architecture: Modular design allowing independent validation modules

### 4. Impact
- **Time reduction**: What previously took days of manual review now completes in hours
- **Quality improvement**: Systematic validation catches edge cases human reviewers often miss
- **Team adoption**: Non-technical team members can now run complex data validations independently
- **Scalability**: System handles datasets 10x larger than previous manual process

### Key Learnings
Rather than waiting for top-down system changes, I identified an immediate opportunity to leverage existing skills and tools. The iterative approach—from exploratory scripts to user-friendly interface to full application—allowed for continuous feedback and rapid improvement while delivering value at each stage.
The project demonstrates how targeted automation can transform tedious manual processes into efficient, reliable workflows, ultimately improving both data quality and team productivity.






