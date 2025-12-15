# Prompts for Claude

## GENERATE SPECS

We're going to discuss the specification for a software project. The project details are contained in `BRIEF.md`.

IMPORTANT: The Brief contains the details fro the FULL project. I want you to create a project for me that is just the FIRST STEP towards this full vision i.e. that is PHASE 1, the MVP. Leave the brief as it is - but from this point on, we will concern ourselves with implementing PHASE 1 ONLY.

First start by confirming, and improving where possible, the functional specification so that it is clear, detailed and complete. There should be no ambiguity about what the application should do. Where appropriate, you should also confirm HOW the AI agent application should work. In this respect, we should leverage the full capabilities of the AI orchestration framework that we are using so that code is as simple and abstracted as possible. Remember, the scope of our work is PHASE ONE ONLY.

Then, ask me one question at a time so we can develop thorough, step-by-step technical specifications. Each question should build on my previous answers, and our end goal is to have a detailed specification I can hand off to a developer. This will be built in only a few hours with Claude Code so try and keep the conversation short, apply KISS principles and use logical inference based on previous answers when possible. Remember, the scope of our work is PHASE ONE ONLY.

We should cover: language (ask this first), frameworks, libraries, package managers, styling choices, data structure options (SQL/NoSQL/Graph) BEFORE data storage, architecture, project structure, components, interfaces, design patterns, error handling, UI features, user experience, coding standards, naming conventions, agreed principles, version control, commit standards, testing and documentation requirements. Ask the questions that are RELEVANT for the application that we are building. If there is already some degree of technology specification in BRIEF.md, use this as an opportunity to confirm the choices and make recommendations.

IMPORTANT: we are looking to create an application that leverages the VER~Y LATEST thinking about how to build effective agent systems.

Do not wrap up until you have answers from me for each of these topics. There will be three outputs at the end: a functional spec, an architectural spec, and our code standards specification for `CLAUDE.md`, review the template for this file currently in the repo to understand what we must cover. DO NOT CREATE THESE DOCUMENTS YET - focus on gathering all of the information needed.

**Important**: When asking questions about technical choices, present 2-3 specific options with brief explanations rather than leaving it open-ended. Explain the pros and cons of each option, and also make your own recommendation with a justification. This speeds up decision-making. When there are more viable options available, verbalize this and ask if I want to see more options. Only one question at a time, stay within scope, and don't generate anything until requested.


## SPEC WRAP-UP

Now that we've wrapped up the brainstorming process, compile our findings into three comprehensive, developer-ready specifications:

1. **FUNCTIONAL.md** - Complete functional requirements
2. **ARCHITECTURE.md** - Detailed project architecture
3. **CLAUDE.md** - Compact standards and guidelines

For `CLAUDE.md`, follow the existing template but ensure each section includes specific, actionable directives that we can reference explicitly during development. Be very concise, this should be a compact standards document you will refer to each time you write any code.

Make each specification modular and cross-referenced so developers can quickly find relevant information when prompted to check these files. Do not repeat yourself.


## GENERATE TO-DO

Review `CLAUDE.md` first to understand our standards. Then review `FUNCTIONAL.md` and `ARCHITECTURE.md` to understand what we're building.

Break the project down into manageable, atomic to-do tasks that:

- Build on each other logically
- Are small enough to complete in one session

IMPORTANT: Make the FIRST task a review of the existing code base. i believe that there are some existing references (e.g. to Firecrawler?) that do not relate to the project we are building. Scour everything carefully and make sure it's all what we need for this project and this project only. 

Create `TO-DO.md` with:

1. Clear statements of each task in implementation order
2. Clear dependencies between to-do tasks
3. Explicit prerequisites listed

Each to-do task should be numbered sequentially, and include:

- Brief description
- Specific deliverables
- Dependencies (if any)
- Definition of done

**Important**: Order to-do tasks by dependency, ensuring you can work efficiently and logically through them in order.


## IMPLEMENTATION

> [!NOTE]
> Implement one task at a time. 
> Use HISTORY.md to record progress/status at the conclusion of each task. 
> Always clear context window after updating HISTORY.md.

**First, review `CLAUDE.md` to understand our project standards and workflow.**

Then refresh your memory by checking `HISTORY.md`. Review `ARCHITECTURE.md` to understand what we are building.

We are working through `IMPLEMENTATION-PLAN.md` and are on Step 24.

**Before implementing anything:**

1. Confirm you understand the current task requirements
2. Ask if you should reference any specific standards from `CLAUDE.md`
3. Only implement what's specified in this task

As you implement, explain:

- How the code works and why it meets our requirements
- How it aligns with our `ARCHITECTURE.md`
- Why it complies with our standards in `CLAUDE.md`

Now, here is the next task to complete:

### Step 24: Configure GitHub Secrets

**Goal:** Set up secrets for GCP authentication

**Actions:**

**Manual steps in GitHub:**

1. **Create GCP Service Account:**
```bash
# In terminal
export PROJECT_ID=$(gcloud config get-value project)

# Create service account
gcloud iam service-accounts create github-actions \
    --display-name="GitHub Actions"

# Grant permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"

# Create key
gcloud iam service-accounts keys create ~/gcp-key.json \
    --iam-account=github-actions@${PROJECT_ID}.iam.gserviceaccount.com

# Display key (copy for next step)
cat ~/gcp-key.json
```

2. **Add secrets to GitHub:**
   - Go to: https://github.com/YOUR-ORG/uk-curriculum-ontology/settings/secrets/actions
   - Click "New repository secret"
   - Add `GCP_SA_KEY`: Paste contents of ~/gcp-key.json
   - Add `GCP_PROJECT_ID`: Your GCP project ID

3. **Clean up local key:**
```bash
rm ~/gcp-key.json
```

**Test:**
```bash
# Push code to trigger workflow
git push origin main

# Or manually trigger deploy-fuseki workflow from GitHub Actions UI
# Actions tab → Deploy Fuseki to Cloud Run → Run workflow
```

**Success Criteria:**
- ✅ Service account created
- ✅ Secrets added to GitHub
- ✅ Workflow can authenticate with GCP
- ✅ Deployment succeeds

**Commit:** Not needed (GitHub configuration)

```

### DEPENDENCY CHECK

Before starting this task [`TASK_NUMBER`], check `TO-DO.md` for dependencies. Then:

1. Verify all prerequisite tasks are complete
2. Confirm our implementation aligns with dependent tasks
3. Check if any shared interfaces or data structures need coordination with your teammate
4. Flag any potential conflicts with work in progress

Only proceed when dependencies are satisfied and coordination is clear.


### CONTEXT RESET

    Now we will reset the context window, before we do so:

    1. Create/update a `HISTORY.md` file summarizing our progress
    2. List completed tasks with key implementation details
    3. Note any important decisions or patterns established
    4. Mention any deviations from original specs and why
    5. Save current state of key variables/configurations
    6. If applicable, update `CLAUDE.md` with any learned standards picked up from the review process
    7. If there have been significant changes, update `FUNCTIONAL.md` or `ARCHITECTURE.md` as required
    8. Update IMPLEMENTATION-PLAN.md with any changes to what has been completed and show completed items with ticks
    9. **IMPORTANT**: Be concise, don't repeat yourself, double check and remove duplication/reduce where possible

    DO NOT CREATE ANY NEW .md FILES FOR DOCUMENTATION - UPDATE THE EXISTING .md FILES.
    After creating/updating these files, I'll reset the context window and we'll continue with a fresh session.



### FINAL DOCUMENTATION CHECK

Now double check ALL documentation - HISTORY.md, ARCHITECTURE.md, FUNCTIONAL.md, TO-DO.md and CLAUDE.md.
They must each be VERY well-written and explained. Professional grade documentation - but readable and understandable by a junior member of staff.

Make sure that all of the DOCUMENTATION is CONSISTENT, CONCISE and ACCURATE. All content must be RELEVANT and relate directly to the application implementation.

Finally, ensure that the README.md is the best possible README - PROFESSIONAL, INFORMATIVE, RELEVANT. 