# PlannerAgent Usage Examples

This document provides detailed examples of how the PlannerAgent works in practice.

## Example 1: Simple Feature Implementation

### User Request
```
"Add a contact form to the homepage"
```

### PlannerAgent Execution

#### Step 1: Think and Analyze
```
Tool: think
Arguments:
{
  "thought": "The user wants to add a contact form to the homepage.
             This requires: 1) understanding the current frontend framework,
             2) creating the form component, 3) adding backend endpoint to handle submissions,
             4) testing the integration. Let me create a plan."
}
```

#### Step 2: Create Plan
```
Tool: create_plan
Arguments:
{
  "goal": "Add a functional contact form to the homepage",
  "steps": [
    {
      "id": "analyze_stack",
      "description": "Analyze the current tech stack and homepage structure",
      "agent_type": "CodeActAgent",
      "inputs": {
        "task": "Examine the homepage file and identify the frontend framework being used"
      },
      "dependencies": []
    },
    {
      "id": "create_component",
      "description": "Create the contact form component",
      "agent_type": "CodeActAgent",
      "inputs": {
        "task": "Create a contact form component with fields for name, email, and message"
      },
      "dependencies": ["analyze_stack"]
    },
    {
      "id": "backend_endpoint",
      "description": "Create backend endpoint to handle form submissions",
      "agent_type": "CodeActAgent",
      "inputs": {
        "task": "Create an API endpoint to receive and process contact form submissions"
      },
      "dependencies": ["analyze_stack"]
    },
    {
      "id": "integrate",
      "description": "Integrate form into homepage",
      "agent_type": "CodeActAgent",
      "inputs": {
        "task": "Add the contact form component to the homepage"
      },
      "dependencies": ["create_component", "backend_endpoint"]
    },
    {
      "id": "test",
      "description": "Test the contact form end-to-end",
      "agent_type": "CodeActAgent",
      "inputs": {
        "task": "Test the contact form submission flow"
      },
      "dependencies": ["integrate"]
    }
  ],
  "context": {
    "task_type": "feature_implementation",
    "estimated_complexity": "medium"
  }
}

Response: "Created execution plan for: Add a functional contact form to the homepage

Steps:
1. Analyze the current tech stack and homepage structure (using CodeActAgent)
2. Create the contact form component (using CodeActAgent)
3. Create backend endpoint to handle form submissions (using CodeActAgent)
4. Integrate form into homepage (using CodeActAgent)
5. Test the contact form end-to-end (using CodeActAgent)"
```

#### Step 3: Execute First Step
```
Tool: delegate_task
Arguments:
{
  "step_id": "analyze_stack",
  "agent_type": "CodeActAgent",
  "task": "Examine the homepage file and identify the frontend framework being used.
          Look for package.json, check imports, and determine if it's React, Vue, or plain HTML/JS."
}

Observation from CodeActAgent:
"Found package.json indicating React application. Homepage is in src/pages/Home.jsx.
 Using React 18 with functional components. Backend is Express.js."
```

#### Step 4: Update Plan with Results
```
Tool: update_plan
Arguments:
{
  "step_id": "analyze_stack",
  "status": "completed",
  "result": "React 18 with functional components, Express.js backend",
  "refinement_reason": "First step completed successfully",
  "refinement_changes": "Confirmed tech stack, proceeding with React component creation"
}
```

#### Step 5: Continue Execution
```
Tool: delegate_task
Arguments:
{
  "step_id": "create_component",
  "agent_type": "CodeActAgent",
  "task": "Create a React functional component for a contact form.
          Include fields for name (text), email (email), and message (textarea).
          Add validation and a submit button. Use modern React patterns with hooks."
}

Observation: "Created ContactForm.jsx component with useState for form data,
              validation, and submission handling."
```

```
Tool: update_plan
Arguments:
{
  "step_id": "create_component",
  "status": "completed",
  "result": "ContactForm component created with validation"
}
```

#### Step 6: Backend Endpoint
```
Tool: delegate_task
Arguments:
{
  "step_id": "backend_endpoint",
  "agent_type": "CodeActAgent",
  "task": "Create an Express.js POST endpoint at /api/contact that accepts
          name, email, and message. Validate inputs and send confirmation email."
}

Observation: "Created /api/contact endpoint with validation.
              Question: Should I integrate with an email service? Which one?"
```

#### Step 7: Handle Unexpected Situation
```
Tool: think
Arguments:
{
  "thought": "The agent raised a good question about email service.
             I should refine the plan to add a step for email service configuration,
             or for now, just log the submissions."
}
```

```
Tool: update_plan
Arguments:
{
  "step_id": "backend_endpoint",
  "status": "completed",
  "result": "Endpoint created, submissions are logged for now",
  "new_steps": [
    {
      "id": "email_config",
      "description": "Configure email service (optional future enhancement)",
      "agent_type": "CodeActAgent",
      "inputs": {
        "task": "Document how to integrate with SendGrid or similar"
      },
      "dependencies": ["test"]
    }
  ],
  "refinement_reason": "Agent asked about email service",
  "refinement_changes": "For now, logging submissions. Added future step for email integration."
}
```

#### Step 8: Continue with Integration
```
Tool: delegate_task
Arguments:
{
  "step_id": "integrate",
  "agent_type": "CodeActAgent",
  "task": "Import and add the ContactForm component to src/pages/Home.jsx.
          Place it in a sensible location on the page."
}

Observation: "Added ContactForm to homepage, styled to match existing design."
```

```
Tool: update_plan
Arguments:
{
  "step_id": "integrate",
  "status": "completed",
  "result": "Form integrated into homepage"
}
```

#### Step 9: Testing
```
Tool: delegate_task
Arguments:
{
  "step_id": "test",
  "agent_type": "CodeActAgent",
  "task": "Test the contact form: 1) Start the dev server, 2) Fill out the form,
          3) Submit and verify the endpoint receives the data, 4) Check validation works."
}

Observation: "All tests passed. Form submits correctly, validation works,
              backend receives data and logs it."
```

```
Tool: update_plan
Arguments:
{
  "step_id": "test",
  "status": "completed",
  "result": "All tests passed successfully"
}
```

#### Step 10: Finish
```
Tool: finish
Arguments:
{
  "summary": "Successfully added a contact form to the homepage.
              The form includes validation, connects to a backend endpoint,
              and all tests pass. Created a future enhancement step for email service integration.",
  "outputs": {
    "files_created": ["src/components/ContactForm.jsx"],
    "files_modified": ["src/pages/Home.jsx", "server/routes/contact.js"],
    "tests_passing": true,
    "future_enhancements": ["Email service integration"]
  }
}
```

---

## Example 2: Bug Investigation and Fix

### User Request
```
"The app crashes when I click the submit button on the registration form"
```

### PlannerAgent Execution

#### Step 1: Create Investigation Plan
```
Tool: create_plan
Arguments:
{
  "goal": "Fix the crash on registration form submission",
  "steps": [
    {
      "id": "reproduce",
      "description": "Reproduce the crash and capture error details",
      "agent_type": "CodeActAgent",
      "inputs": {
        "task": "Run the app and attempt to submit the registration form"
      },
      "dependencies": []
    },
    {
      "id": "analyze_code",
      "description": "Analyze the registration form code",
      "agent_type": "CodeActAgent",
      "inputs": {
        "task": "Examine the registration form component and submission handler"
      },
      "dependencies": ["reproduce"]
    },
    {
      "id": "identify_cause",
      "description": "Identify the root cause of the crash",
      "agent_type": "CodeActAgent",
      "inputs": {
        "task": "Based on the error and code analysis, determine what's causing the crash"
      },
      "dependencies": ["analyze_code"]
    },
    {
      "id": "implement_fix",
      "description": "Implement the fix",
      "agent_type": "CodeActAgent",
      "inputs": {
        "task": "Fix the identified issue"
      },
      "dependencies": ["identify_cause"]
    },
    {
      "id": "verify_fix",
      "description": "Verify the fix works and no regressions",
      "agent_type": "CodeActAgent",
      "inputs": {
        "task": "Test the registration form again and run existing tests"
      },
      "dependencies": ["implement_fix"]
    }
  ]
}
```

#### Step 2: Reproduce Issue
```
Tool: delegate_task
Arguments:
{
  "step_id": "reproduce",
  "agent_type": "CodeActAgent",
  "task": "Start the development server and navigate to the registration form.
          Fill it out and click submit. Capture the error message and stack trace."
}

Observation: "Error reproduced. Stack trace shows:
              'TypeError: Cannot read property map of undefined at RegistrationForm.jsx:42'"
```

#### Step 3: Analyze Code
```
Tool: delegate_task
Arguments:
{
  "step_id": "analyze_code",
  "agent_type": "CodeActAgent",
  "task": "Examine RegistrationForm.jsx, specifically line 42 and surrounding code.
          Look for where 'map' is being called on a potentially undefined value."
}

Observation: "Found the issue at line 42:
              'formFields.map(field => ...)'
              The formFields state is initialized as undefined instead of an empty array."
```

#### Step 4: Plan Refinement Based on Discovery
```
Tool: update_plan
Arguments:
{
  "step_id": "analyze_code",
  "status": "completed",
  "result": "Root cause identified: formFields initialized as undefined",
  "refinement_reason": "Found root cause during analysis",
  "refinement_changes": "Can skip identify_cause step and go straight to fix"
}
```

#### Step 5: Implement Fix
```
Tool: delegate_task
Arguments:
{
  "step_id": "implement_fix",
  "agent_type": "CodeActAgent",
  "task": "In RegistrationForm.jsx, change the useState initialization from
          'const [formFields, setFormFields] = useState(undefined)' to
          'const [formFields, setFormFields] = useState([])'.
          Also add a safety check if needed."
}

Observation: "Fixed the initialization. Also added a defensive check:
              'formFields?.map(...)' for additional safety."
```

#### Step 6: Verify Fix
```
Tool: delegate_task
Arguments:
{
  "step_id": "verify_fix",
  "agent_type": "CodeActAgent",
  "task": "Test the registration form submission again.
          Also run any existing unit tests for the registration component."
}

Observation: "Fix verified! Form now submits without crashing.
              All 12 existing tests pass."
```

#### Step 7: Finish
```
Tool: finish
Arguments:
{
  "summary": "Fixed the registration form crash. The issue was caused by
              formFields being initialized as undefined instead of an empty array,
              causing a TypeError when map was called. Added defensive programming
              with optional chaining as well.",
  "outputs": {
    "files_modified": ["src/components/RegistrationForm.jsx"],
    "root_cause": "Undefined array initialization",
    "fix": "Initialize as empty array and add optional chaining",
    "tests_passing": true
  }
}
```

---

## Example 3: Multi-Agent Coordination

### User Request
```
"Create a blog feature with markdown support"
```

### PlannerAgent Execution

This example shows how PlannerAgent coordinates between CodeActAgent and BrowsingAgent.

#### Step 1: Create Multi-Agent Plan
```
Tool: create_plan
Arguments:
{
  "goal": "Create a blog feature with markdown support",
  "steps": [
    {
      "id": "research_markdown",
      "description": "Research markdown libraries and best practices",
      "agent_type": "BrowsingAgent",
      "inputs": {
        "task": "Search for popular React markdown libraries and their features"
      },
      "dependencies": []
    },
    {
      "id": "analyze_codebase",
      "description": "Analyze current codebase structure",
      "agent_type": "CodeActAgent",
      "inputs": {
        "task": "Examine the project structure and determine where blog components should go"
      },
      "dependencies": []
    },
    {
      "id": "design_schema",
      "description": "Design blog post data model",
      "agent_type": "CodeActAgent",
      "inputs": {
        "task": "Create database schema for blog posts"
      },
      "dependencies": ["analyze_codebase"]
    },
    {
      "id": "implement_backend",
      "description": "Implement backend blog API",
      "agent_type": "CodeActAgent",
      "inputs": {
        "task": "Create CRUD endpoints for blog posts"
      },
      "dependencies": ["design_schema"]
    },
    {
      "id": "implement_editor",
      "description": "Implement markdown editor component",
      "agent_type": "CodeActAgent",
      "inputs": {
        "task": "Create blog post editor with markdown preview"
      },
      "dependencies": ["research_markdown", "implement_backend"]
    },
    {
      "id": "implement_viewer",
      "description": "Implement blog post viewer",
      "agent_type": "CodeActAgent",
      "inputs": {
        "task": "Create component to render markdown blog posts"
      },
      "dependencies": ["research_markdown", "implement_backend"]
    },
    {
      "id": "test_feature",
      "description": "Test the complete blog feature",
      "agent_type": "CodeActAgent",
      "inputs": {
        "task": "Test creating, editing, viewing, and deleting blog posts"
      },
      "dependencies": ["implement_editor", "implement_viewer"]
    }
  ]
}
```

Notice how:
- Steps 1 and 2 can run independently (no dependencies)
- Step 5 depends on BOTH step 1 (research) and step 4 (backend)
- PlannerAgent coordinates between BrowsingAgent (research) and CodeActAgent (implementation)

---

## Example 4: Handling Failures and Recovery

### User Request
```
"Deploy the app to production"
```

### PlannerAgent Execution with Failure Recovery

#### Execution with Failure
```
Tool: create_plan (abbreviated)
...
Steps: build, run_tests, deploy, verify
```

```
Tool: delegate_task
Arguments: { "step_id": "run_tests", "agent_type": "CodeActAgent", "task": "Run all tests" }

Observation: "Tests failed. 3 out of 45 tests failing:
              - test/api/users.test.js - UserAPI.create fails
              - test/api/users.test.js - UserAPI.update fails
              - test/components/UserForm.test.js - form validation fails"
```

#### Recovery Strategy
```
Tool: think
Arguments:
{
  "thought": "Tests are failing. I should not proceed with deployment.
             Instead, I need to refine the plan to:
             1) Investigate the failing tests,
             2) Fix the issues,
             3) Re-run tests,
             4) Only then proceed with deployment."
}
```

```
Tool: update_plan
Arguments:
{
  "step_id": "run_tests",
  "status": "failed",
  "error": "3 tests failing in user-related functionality",
  "new_steps": [
    {
      "id": "investigate_failures",
      "description": "Investigate why user tests are failing",
      "agent_type": "CodeActAgent",
      "inputs": {
        "task": "Examine the failing tests and the code they're testing"
      },
      "dependencies": []
    },
    {
      "id": "fix_issues",
      "description": "Fix the identified issues",
      "agent_type": "CodeActAgent",
      "inputs": {
        "task": "Fix the bugs causing test failures"
      },
      "dependencies": ["investigate_failures"]
    },
    {
      "id": "rerun_tests",
      "description": "Run tests again",
      "agent_type": "CodeActAgent",
      "inputs": {
        "task": "Run the full test suite"
      },
      "dependencies": ["fix_issues"]
    }
  ],
  "refinement_reason": "Tests failed, must fix before deployment",
  "refinement_changes": "Added investigation and fix steps. Deployment will wait until tests pass."
}
```

The plan is now:
1. ~~build~~ (completed)
2. ~~run_tests~~ (failed)
3. investigate_failures (new)
4. fix_issues (new)
5. rerun_tests (new)
6. deploy (blocked until tests pass)
7. verify (blocked)

This shows how PlannerAgent adapts to failures and creates a recovery strategy.

---

## Key Takeaways

1. **Planning is Explicit**: Every step is clearly defined
2. **Feedback Drives Refinement**: Plans adapt based on execution results
3. **Multi-Agent Coordination**: Different agents for different tasks
4. **Error Recovery**: Failures trigger plan refinements
5. **Dependency Management**: Steps execute in correct order
6. **Transparency**: Every decision is visible and logged

The PlannerAgent brings structure and intelligence to complex task execution!
