import pandas as pd
import os
import datetime
from datetime import timezone
import json
import logging
import sys
from getpass import getpass

import readchar
import requests
from garth.exc import GarthHTTPError

from garminconnect import (
    Garmin,
    GarminConnectAuthenticationError,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError,
)



# Configure debug logging
# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables if defined
email = os.getenv("GARMIN_EMAIL")
password = os.getenv("GARMIN_PASSWORD")
tokenstore = os.getenv("GARMINTOKENS") or "~/.garminconnect"
tokenstore_base64 = os.getenv("GARMINTOKENS_BASE64") or "~/.garminconnect_base64"
api = None

def display_json(api_call, output):
    """Format API output for better readability."""

    dashed = "-" * 20
    header = f"{dashed} {api_call} {dashed}"
    footer = "-" * len(header)

    print(header)

    if isinstance(output, (int, str, dict, list)):
        print(json.dumps(output, indent=4))
    else:
        print(output)

    print(footer)


def get_credentials():
    """Get user credentials."""

    email = input("Login e-mail: ")
    password = getpass("Enter password: ")

    return email, password

def get_mfa():
    """Get MFA."""

    return input("MFA one-time code: ")

def init_api(email, password):
    """Initialize Garmin API with your credentials."""

    try:
        # Using Oauth1 and OAuth2 token files from directory
        print(
            f"Trying to login to Garmin Connect using token data from directory '{tokenstore}'...\n"
        )

        # Using Oauth1 and Oauth2 tokens from base64 encoded string
        # print(
        #     f"Trying to login to Garmin Connect using token data from file '{tokenstore_base64}'...\n"
        # )
        # dir_path = os.path.expanduser(tokenstore_base64)
        # with open(dir_path, "r") as token_file:
        #     tokenstore = token_file.read()

        garmin = Garmin()
        garmin.login(tokenstore)

    except (FileNotFoundError, GarthHTTPError, GarminConnectAuthenticationError):
        # Session is expired. You'll need to log in again
        print(
            "Login tokens not present, login with your Garmin Connect credentials to generate them.\n"
            f"They will be stored in '{tokenstore}' for future use.\n"
        )
        try:
            # Ask for credentials if not set as environment variables
            if not email or not password:
                email, password = get_credentials()

            garmin = Garmin(
                email=email, password=password, is_cn=False, prompt_mfa=get_mfa
            )
            garmin.login()
            # Save Oauth1 and Oauth2 token files to directory for next login
            garmin.garth.dump(tokenstore)
            print(
                f"Oauth tokens stored in '{tokenstore}' directory for future use. (first method)\n"
            )
            # Encode Oauth1 and Oauth2 tokens to base64 string and safe to file for next login (alternative way)
            token_base64 = garmin.garth.dumps()
            dir_path = os.path.expanduser(tokenstore_base64)
            with open(dir_path, "w") as token_file:
                token_file.write(token_base64)
            print(
                f"Oauth tokens encoded as base64 string and saved to '{dir_path}' file for future use. (second method)\n"
            )
        except (
            FileNotFoundError,
            GarthHTTPError,
            GarminConnectAuthenticationError,
            requests.exceptions.HTTPError,
        ) as err:
            logger.error(err)
            return None

    return garmin



# Obtener la lista de ficheros en la carpeta 'data'
sourcedir='arboleaf2garmin/data'
ficheros = os.listdir(sourcedir)

# Filtrar los ficheros para obtener solo los que tienen extensión .xlsx
ficheros_excel = [f for f in ficheros if f.endswith('.xlsx')]

# Leer el primer fichero Excel encontrado
if ficheros_excel:
    df = pd.read_excel(os.path.join(sourcedir, ficheros_excel[0]))   
    df['Tiempo de medición'] = pd.to_datetime(df['Tiempo de medición'],dayfirst=True) 
    # Agrupar por la fecha (sin la hora) y calcular la media de varias columnas
    df['Fecha'] = df['Tiempo de medición'].dt.date
    medias = df.groupby('Fecha')[['Peso(kg)', 'Grasa corporal(%)', 'Agua corporal(%)', 'Grasa visceral', 'Masa ósea(kg)', 'Masa muscular(kg)', 
                                  'TMB(kcal)', 'Edad metabólica', 'IMC']].mean()
    medias_dict = medias.to_dict(orient='index')
    api = init_api(email, password)

    for fecha, valores in medias_dict.items():
        weight = valores['Peso(kg)']
        percent_fat = valores['Grasa corporal(%)']
        percent_hydration = valores['Agua corporal(%)']
        visceral_fat_mass = None
        bone_mass = valores['Masa ósea(kg)']
        muscle_mass = valores['Masa muscular(kg)']
        basal_met = valores['TMB(kcal)']
        active_met = None
        physique_rating = None
        metabolic_age = valores['Edad metabólica']
        visceral_fat_rating = valores['Grasa visceral']
        bmi = valores['IMC']

        # display_json(
        #     f"api.get_body_composition('{fecha.isoformat()}')",
        #     api.get_body_composition(fecha.isoformat()),
        # )
        if len(api.get_body_composition(fecha.isoformat())['dateWeightList'])==0:
            response=api.add_body_composition(
                fecha.isoformat(),
                weight=weight,
                percent_fat=percent_fat,
                percent_hydration=percent_hydration,
                visceral_fat_mass=visceral_fat_mass,
                bone_mass=bone_mass,
                muscle_mass=muscle_mass,
                basal_met=basal_met,
                active_met=active_met,
                physique_rating=physique_rating,
                metabolic_age=metabolic_age,
                visceral_fat_rating=visceral_fat_rating,
                bmi=bmi,
            )

    # Mostrar la media de 'Agua corporal(%)' por fecha 
    # print(medias)
    # print (df)
else:
    print("No se encontraron ficheros Excel en la carpeta 'data'.")

# today = datetime.date.today()




# api.add_body_composition(
#             today.isoformat(),
#             weight=weight,
#             percent_fat=percent_fat,
#             percent_hydration=percent_hydration,
#             visceral_fat_mass=visceral_fat_mass,
#             bone_mass=bone_mass,
#             muscle_mass=muscle_mass,
#             basal_met=basal_met,
#             active_met=active_met,
#             physique_rating=physique_rating,
#             metabolic_age=metabolic_age,
#             visceral_fat_rating=visceral_fat_rating,
#             bmi=bmi,
#         )


# if api:
#     # Add body composition
#     weight = 70.0
#     percent_fat = 15.4
#     percent_hydration = 54.8
#     visceral_fat_mass = 10.8
#     bone_mass = 2.9
#     muscle_mass = 55.2
#     basal_met = 1454.1
#     active_met = None
#     physique_rating = None
#     metabolic_age = 33.0
#     visceral_fat_rating = None
#     bmi = 22.2
#     display_json(
#         f"api.add_body_composition({today.isoformat()}, {weight}, {percent_fat}, {percent_hydration}, {visceral_fat_mass}, {bone_mass}, {muscle_mass}, {basal_met}, {active_met}, {physique_rating}, {metabolic_age}, {visceral_fat_rating}, {bmi})",
#         api.add_body_composition(
#             today.isoformat(),
#             weight=weight,
#             percent_fat=percent_fat,
#             percent_hydration=percent_hydration,
#             visceral_fat_mass=visceral_fat_mass,
#             bone_mass=bone_mass,
#             muscle_mass=muscle_mass,
#             basal_met=basal_met,
#             active_met=active_met,
#             physique_rating=physique_rating,
#             metabolic_age=metabolic_age,
#             visceral_fat_rating=visceral_fat_rating,
#             bmi=bmi,
#         ),
#     )