import json
import httpx
import asyncio
from fastapi import FastAPI
from pydantic import BaseModel


class dataset(BaseModel):
    application: str
    focus: str
    cloud: str
    data: str


timeout = httpx.Timeout(
    connect=10.0,
    read=120.0,
    write=10.0,
    pool=10.0
)


async def judge(ai_responses, cloud, prompt):
    j_prompt = f"""
            Assume yourself a senior FinOps and Solution Architect specialized in {cloud}.

            You have the following architecture responses for the problem:
            {prompt}

            Responses:
            {ai_responses}

            Rules:
            - Be unbiased
            - Select the best solution with future potential
            - Mention which model you choose
"""

    j_model = "mistralai/devstral-2512:free"

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": "Bearer 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",
                "Content-Type": "application/json",
            },
            json={
                "model": j_model,
                "messages": [{"role": "user", "content": j_prompt}]
            }
        )

    data = response.json()
    return data["choices"][0]["message"]["content"]


async def data_sending(main_prompt, model, client):
    response = await client.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": "",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",
            "X-Title": "aiinfra-prototype"
        },

        data=json.dumps({
            "model": f"{model}",
            "messages": [{
                "role": "user",
                "content": f"{main_prompt}"

            }]
        })
    )

    data = response.json()
    final_data = data['choices'][0]['message']['content']
    return {
        "model": model,
        "response": final_data
    }


ai = FastAPI()


@ai.post("/testing")
async def ai_func(Payload: dataset):
    requiremnt = Payload.application
    focus = Payload.focus
    cloud = Payload.cloud
    prompt = Payload.data

    models = ["meta-llama/llama-3.3-70b-instruct:free", "xiaomi/mimo-v2-flash:free"]

    main_prompt = f""" ou are a Senior Cloud Solutions Architect specialized in {cloud}

                                Design a cloud architecture for the following problem:
                                {prompt}

                                Constraints:
                                - Application type: {requiremnt}
                                - Primary focus: {focus}

                                Hard Architectural Rules (MANDATORY):

                                - Start with a single-cloud design
                                - Introduce multicloud ONLY if it improves reliability, scale, or performance if user want any specific cloud than dont use multicloud 
                                - If multicloud is used, assign ONE clear responsibility per cloud
                                - Data must have ONE primary storage location
                                - Compute must run in ONE cloud per execution
                                - Do NOT duplicate the same layer across multiple clouds
                                - Do NOT mix clouds without a strong technical reason


                                Strict Rules:
                                - Use ONLY bullet points
                                - NO storytelling
                                - NO assumptions
                                - NO pricing
                                - NO code
                                - Explain each service in ONE short line (purpose only)
                                - Explain how services connect using "->"
                                - Do NOT list optional or unused services
                                - Prefer minimal services over many

                                Required Output Format (DO NOT CHANGE):

                                Auth:
                                - <service>: <purpose> -> <connected service>

                                API:
                                - <service>: <purpose> -> <connected service>

                                Compute:
                                - <service>: <purpose> -> <connected service>

                                Database:
                                - <service>: <purpose> -> <connected service>

                                Monitoring:
                                - <service>: <purpose>

                                Extra (ONLY if required):
                                - <service>: <purpose>"""

    async with httpx.AsyncClient(timeout=timeout) as client:
        task = [data_sending(main_prompt, model, client) for model in models]
        result = await asyncio.gather(*task, return_exceptions=True)

        ai_responses = result

    judge_res = await judge(ai_responses, cloud, prompt)

    return {
        "models_output": ai_responses,
        "judge_decision": judge_res
    }









