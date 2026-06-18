# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

import os
import google.auth
from google.adk.tools.openapi_tool import OpenAPIToolset
from pathlib import Path

_, project_id = google.auth.default()
os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

base_dir = Path(__file__).resolve().parent
apispec_file_path = base_dir / "currency-conversion-apispec.json"
with open(apispec_file_path, "r") as f:
    openapi_spec_json_content = f.read()

currency_conversion_toolset = OpenAPIToolset(spec_str=openapi_spec_json_content, spec_str_type="json")


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-flash-latest",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="Answer user questions by using the tools available to you. If the user asks for currency conversion, use the currency_conversion_toolset to convert the currency.",
    tools=[currency_conversion_toolset],
)

app = App(
    root_agent=root_agent,
    name="app",
)
