import os
import json
import requests
import io
import zipfile
import mayalabs
from halo import Halo
from .helpers import get_api_key
from .helpers import print_usage_guide


def teach(file_path):
    if not file_path:
        print_usage_guide("teach")
        return

    api_key = get_api_key(show_instructions=True)
    if not api_key:
        return
    mayalabs.api_key = api_key

    if os.path.isfile(file_path):
        # Creating zip in memory using the specified files
        buffer = io.BytesIO()
        with zipfile.ZipFile(
            buffer, mode="w", compression=zipfile.ZIP_DEFLATED
        ) as zip_file:
            zip_file.writestr("recipes/", "")

            zip_file.writestr("recipes/recipe_1/", "")
            zip_file.write(file_path, "recipes/recipe_1/s0.txt")
        zip_data = buffer.getvalue()

        with zipfile.ZipFile(buffer, "r") as zip_ref:
            for file_name in zip_ref.namelist():
                print(file_name)

        # return

        # Checking collision levels
        collision_spinner = Halo(spinner="dots")
        collision_spinner.start()
        headers = {"X-API-KEY": api_key}
        files = {"files": ("filename.zip", io.BytesIO(zip_data))}
        url = "https://api.dev.mayalabs.io/pac/v1/library/skill/verify"
        response = requests.post(url, headers=headers, files=files, timeout=30)
        response_text = json.loads(response.text)
        verification_data = response_text["reference"]["recipes"][0]
        collision_spinner.stop()
        max_mean_collision_score = 0
        for key, value in verification_data.items():
            for i in range(len(value)):
                mean_collision_score = value[i]["mean_collision_score"]
                if mean_collision_score > max_mean_collision_score:
                    max_mean_collision_score = mean_collision_score

        # Checking user's intent to teach
        max_mean_collision_percentage = max_mean_collision_score * 100
        intent_to_teach = "y"
        if max_mean_collision_percentage > 50:
            print(
                f"The uploaded recipe has a clash of {round(max_mean_collision_percentage, 2)}% with an existing recipe."
            )
            intent_to_teach = input("Do you want to teach the recipe or abort? [y/N] ")

        # Teaching
        if intent_to_teach == "y" or intent_to_teach == "Y":
            teaching_spinner = Halo(spinner="dots")
            teaching_spinner.start()
            headers = {"X-API-KEY": api_key}
            files = {"files": open(file_path, "rb")}
            url = "https://api.dev.mayalabs.io/pac/v1/library/recipe/teach"
            response = requests.post(url, headers=headers, files=files, timeout=30)
            teaching_spinner.stop()
            response_text = json.loads(response.text)
            print(response_text)
            # print("Recipe taught! You can now use it your programs.")
        else:
            return
    else:
        print(f"{file_path} does not lead to a file.")
