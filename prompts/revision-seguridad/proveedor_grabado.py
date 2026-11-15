import pathlib

BASE = pathlib.Path(__file__).parent

def call_api(prompt, options, context):
    vars_dict = context.get("vars", {})
    case_id = vars_dict.get("id", "C1")
    if "<codigo" in prompt:
        version = "v3"
    elif "Revisa el código y reporta vulnerabilidades en JSON" in prompt:
        version = "v2"
    else:
        version = "v1"
    ruta = BASE / "grabaciones" / version / f"{case_id}.txt"
    return {"output": ruta.read_text(encoding="utf-8")}
