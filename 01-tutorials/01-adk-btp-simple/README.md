# Tutorial: Building SAP BTP-Powered Agents with Google Cloud Agent Development Kit (ADK)

**Tech Stack**: `Google Cloud ADK`, `Agent Runtime`, `Gemini`, `SAP BTP`, `Python`  
---

## 1. Introduction

### Objective

In this tutorial, you will learn how to build an AI agent using the **Google Cloud Agent Development Kit (ADK)**. We will leverage **SAP BTP** for business logic (in this case, a simple currency conversion API), **Gemini** for serverless reasoning, and deploy the final agent to the fully managed **Gemini Enterprise Agent Platform** for enterprise-grade scalability.

### Goals

* Build and deploy a currency conversion REST API to **SAP BTP**.
* Initialize an agent using the **ADK Python library**.
* Implement tool calls using ADK's out-of-the-box **OpenAPI toolset**.
* Test the agent locally using the **ADK development server**.
* Deploy the agent to the **Gemini Enterprise Agent Platform** and query it via an API.

### Scope

* Single-agent orchestration using ADK.
* Create a Python-based REST API with FastAPI running on SAP BTP.
* Consume the deployed REST API from the ADK agent using ADK's out-of-the-box OpenAPI toolset.
* Deploy to the Agent Engine (serverless) runtime.

### Out of Scope

* Building a custom frontend UI.
* Securing the currency conversion API with an SAP BTP XSUAA service instance (covered in subsequent tutorials).
* Complex SAP BTP service integrations.
* Complex multi-model orchestration or multi-Agent delegation (A2A protocol).

---

## 2. Prerequisites & Setup

Before you begin, ensure you have:

### Google Cloud Resources

* A [Google Cloud Project](https://console.cloud.google.com/projectselector2/home/dashboard) with [billing](https://docs.cloud.google.com/billing/docs/how-to/verify-billing-enabled#confirm_billing_is_enabled_on_a_project) enabled.
* Enabled APIs:
  * [Gemini Enterprise Agents Platform API](https://console.cloud.google.com/flows/enableapi?apiid=aiplatform.googleapis.com)
  * [Compute Engine API](https://console.cloud.google.com/flows/enableapi?apiid=compute.googleapis.com)
  * [Resource Manager API](https://console.cloud.google.com/flows/enableapi?apiid=cloudresourcemanager.googleapis.com)

### SAP BTP Resources

* An [SAP BTP Account](https://account.hana.ondemand.com/).
* The [Cloud Foundry Environment](https://help.sap.com/docs/SAP_CLOUD_PLATFORM/65de2977205c403bbc107264b8eccf4b/a4d3dd7482de4089b6572a63753d0434.html) enabled in your subaccount.
* A [Space](https://help.sap.com/docs/SAP_CLOUD_PLATFORM/65de2977205c403bbc107264b8eccf4b/1a2f6431947846c0a0f95c47a2aca0bd.html) created in your Cloud Foundry organization.

### Local Development Environment

* **uv**: [Installed](https://docs.astral.sh/uv/getting-started/installation/) (with Python 3.10+ [installed using uv](https://docs.astral.sh/uv/guides/install-python/)).
* **gcloud CLI**: [Installed](https://docs.cloud.google.com/sdk/docs/install-sdk) and [authenticated](https://docs.cloud.google.com/sdk/docs/install-sdk#initializing-the-cli).
* **agents-cli**: [Installed](https://google.github.io/agents-cli/).

---

## 3. Architecture Overview

The architecture follows a "Brain-Tools-Runtime" pattern:

1. **The Brain**: Gemini provides high-reasoning capabilities.
2. **The Tool**: A FastAPI application provides a simple REST endpoint for currency conversion. It runs within the SAP BTP Cloud Foundry runtime.
3. **The Orchestrator**: ADK manages the conversation state and tool execution. It also provides a dev UI for rapid local testing.
4. **The Runtime**: Agent Runtime hosts the code as a serverless container and provides an API endpoint for the agent.

![Technical Architecture](assets/architecture.png)

---

## 4. Building the Agent

### Step 1: Create the Currency Conversion API

```shell
# Create a directory to host the source code files for the BTP API
uv init adk-btp-simple-api
cd adk-btp-simple-api
uv add fastapi uvicorn requests cfenv sap-xssec
```

Open `main.py` in the `adk-btp-simple-api` folder and paste the code from [main.py](./adk-btp-simple-api/main.py). We will use the open-source [Frankfurter currency data API](https://frankfurter.dev/) to retrieve exchange rates.

### Step 2: Create the requirements.txt File

```shell
# Ensure you are in the adk-btp-simple-api directory
touch requirements.txt
```

Open `requirements.txt` and paste the contents from [requirements.txt](./adk-btp-simple-api/requirements.txt).

### Step 3: Create the manifest.yml File for SAP BTP Deployment

```shell
# Ensure you are in the adk-btp-simple-api directory
touch manifest.yml
```

Open `manifest.yml` and paste the contents from [manifest.yml](./adk-btp-simple-api/manifest.yml).

### Step 4: Deploy to SAP BTP

```shell
# Ensure you are in the adk-btp-simple-api directory
# Log in to SAP BTP if you aren't already
cf login

cf push
```

Upon successful deployment, you will see output similar to the following. The API is now available at the URL listed under `routes`:

![BTP Deployment Result](assets/sap-btp-deploy.png)

### Step 5: Test the Currency Conversion API

Access the API through your browser using the link below, replacing the placeholder domain with your deployed API's route:
`https://currency-conversion-api-<your-subdomain>.cfapps.us30.hana.ondemand.com/convert?amount=100&from_currency=usd&to_currency=eur`

You should see a JSON response similar to the following:

```json
{
    "amount": 100,
    "base": "USD",
    "date": "2026-06-15",
    "rates": {
        "EUR": 86.15
    }
}
```

### Step 6: Create an Agent Project

Run the `agents-cli create` command to start a new agent project. This creates a new directory named `adk-btp-simple-agent` containing boilerplate agent code.

> [!IMPORTANT]
> Replace the placeholders with your actual settings:
> * **`YOUR_PROJECT_ID`**: Your Google Cloud project ID (e.g., `my-demo-project`).
> * **`YOUR_GOOGLE_CLOUD_REGION`**: Your Google Cloud region (e.g., `us-central1`).

```shell
cd ..
# Make sure you are in the parent directory (adk-btp-simple)
agents-cli create adk-btp-simple-agent --prototype --yes
cd adk-btp-simple-agent
agents-cli install
```

### Step 7: Download the OpenAPI Spec for the SAP BTP API

Retrieve the OpenAPI spec for the currency conversion API by visiting the URL below (replace the subdomain matching your setup):
`https://currency-conversion-api-xxxxxx.cfapps.us30.hana.ondemand.com/apispec.json`

Save the JSON response as `currency-conversion-apispec.json` in the `adk-btp-simple-agent/app` folder. Alternatively, you can run the following `curl` command (updating the URL with your route) to download it directly:

```shell
cd app
# Make sure you are in the adk-btp-simple-agent/app directory
curl https://currency-conversion-api-xxxxxx.cfapps.us30.hana.ondemand.com/apispec.json >> currency-conversion-apispec.json
```

### Step 8: Update the Agent to Use the API as a Tool

Out of the box, ADK supports calling REST APIs using the [OpenAPI toolset](https://adk.dev/tools-custom/openapi-tools/). Open `agent.py` in the `adk-btp-simple-agent/app` folder and update it with the code from [agent.py](./adk-btp-simple-agent/app/agent.py).

### Step 9: Run the Agent Locally and Test

Run the `agents-cli playground` command to start the local development server and access the interactive playground UI:

```shell
cd ..
# Ensure you are in the adk-btp-simple-agent directory
agents-cli playground --port 8000
```

Upon successful startup, you will see output similar to the following in your terminal:

![](assets/adk_web.png)

Open your browser and navigate to `http://localhost:8000/`. Select `app` from the **Select an App** dropdown. Once the playground UI launches, you can converse with your agent (e.g., query *'How much is $100 in Euros?'*).

![](assets/adk_web_ui.png)

---

## 5. Deploying the Agent to Google Cloud Agent Engine

Deploying ADK agents to Google Cloud Agent Engine is documented in the [Agent Engine Deployment Guide](https://google.github.io/adk-docs/deploy/agent-engine/). The steps below walk you through deploying via the [Agents CLI Deployment](https://adk.dev/deploy/agent-runtime/agents-cli/) process.

### Step 1: Prepare the Agent for Deployment

```shell
# Make sure you are in the adk-btp-simple-agent directory
agents-cli scaffold enhance --deployment-target agent_runtime
```

### Step 2: Deploy the Agent to Agent Engine

Deploy the agent to the Agent Engine using the `agents-cli deploy` CLI command. This command packages your code, builds a container image, and deploys it. The process may take several minutes. Ensure you run this from the project root directory (`adk-btp-simple-agent`).

> [!IMPORTANT]
> Replace the placeholders with your actual settings:
> * **`YOUR_PROJECT_ID`**: Your Google Cloud project ID.
> * **`YOUR_GOOGLE_CLOUD_REGION`**: Your Google Cloud region (e.g., `us-central1`).

```shell
PROJECT_ID=YOUR_PROJECT_ID
LOCATION_ID=YOUR_GOOGLE_CLOUD_REGION

uv lock

agents-cli deploy \
        --project=$PROJECT_ID \
        --region=$LOCATION_ID
```

A successful deployment will output details similar to the following:

![](assets/agent_engine_deploy.png)

---

## 6. Testing the Deployed Agent

You can test the deployed agent by launching the Console Playground link returned in the deployment output:

![](assets/agent_engine_playground.png)

---

## 7. Summary

In this tutorial, you learned how to:

- Build a production-ready AI agent using the **Google Cloud Agent Development Kit (ADK)**.
- Use the OpenAPI toolsets in ADK to invoke a REST endpoint on **SAP BTP**.
- Package and deploy the agent to the fully managed **Agent Runtime** for enterprise-grade scalability.
- Test the agent using the **Agent Runtime playground**.

---

## 8. Resources

* [Google Cloud Agent Development Kit](https://google.github.io/adk-docs/)  
* [Gemini Enterprise Agent Platform - Agent Runtime](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/runtime)  
* [Generative AI on Gemini Enterprise Agent Platform](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/learn/overview)