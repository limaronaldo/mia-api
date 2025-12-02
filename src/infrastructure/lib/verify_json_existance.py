import json
import re


# Added debug flag and print statements
def verify_json_existence(text: str, debug: bool = False) -> bool:
    """
    Verifies if a string contains valid JSON content, potentially embedded
    within other text, handling Python-style single quotes and literals
    (True, False, None). Uses raw_decode for robustness.

    Args:
        text (str): The input string to check for JSON content.
        debug (bool): If True, print debugging information.

    Returns:
        bool: True if valid JSON is found, False otherwise.
    """
    if debug:
        print(f"\n--- Verifying: '{text[:100]}...'")
    # Optional: Remove known prefixes like "AI: " if necessary
    text = re.sub(r"^AI:\s*", "", text)
    if debug:
        print(f"Text after prefix removal: '{text[:100]}...'")

    # Find all indices where a potential JSON object or array might start
    potential_starts = [match.start() for match in re.finditer(r"[{[]", text)]
    if debug:
        print(f"Potential start indices: {potential_starts}")

    if not potential_starts:
        # Optimization: if no '{' or '[' chars exist, impossible to have JSON
        if debug:
            print("No potential start characters found.")
        return False

    decoder = json.JSONDecoder()

    for i in potential_starts:
        if debug:
            print(f"\nChecking potential start at index: {i}")
        substring = text[i:]
        # Limit substring printing for very long strings if needed
        if debug:
            print(f"  Substring: '{substring[:200]}...'")

        # --- Pre-processing for JSON compatibility ---
        temp_str = re.sub(r"\bTrue\b", "true", substring)
        temp_str = re.sub(r"\bFalse\b", "false", temp_str)
        temp_str = re.sub(r"\bNone\b", "null", temp_str)
        # Check if literals were actually replaced for debugging
        if debug and temp_str != substring:
            print(f"  After literal replacement: '{temp_str[:200]}...'")
        else:
            if debug:
                print(f"  No literals replaced.")

        temp_str_quotes_fixed = temp_str.replace("'", '"')
        # Check if quotes were actually replaced for debugging
        if debug and temp_str_quotes_fixed != temp_str:
            print(f"  After quote replacement: '{temp_str_quotes_fixed[:200]}...'")
        else:
            if debug:
                print(f"  No single quotes found to replace.")
        # --- End Pre-processing ---

        try:
            # Attempt to decode JSON from the start of the processed substring
            obj, end_index = decoder.raw_decode(temp_str_quotes_fixed)
            if debug:
                print(
                    f"  raw_decode successful! Parsed object type: {type(obj)}, End index: {end_index}"
                )

            # Check if the decoded object is a dictionary or a list
            if isinstance(obj, (dict, list)):
                if debug:
                    print("  Valid JSON (dict or list) found. Returning True.")
                return True
            else:
                if debug:
                    print(
                        f"  raw_decode succeeded but result is not dict or list (Type: {type(obj)})."
                    )

        except json.JSONDecodeError as e:
            # Log the specific error and the string that caused it
            if debug:
                print(
                    f"  json.JSONDecodeError: {e}. String was: '{temp_str_quotes_fixed[:200]}...'"
                )
            # Continue the loop to check the next potential starting point.
            continue
        except Exception as e:
            # Catch any other unexpected errors
            if debug:
                print(f"  Unexpected Exception: {type(e).__name__}: {e}")
            continue

    if debug:
        print(
            "--- Verification complete. No valid JSON found starting at any potential index."
        )
    return False


# --- Example Usage ---
if __name__ == "__main__":
    test_string_new = """Claro! Vou verificar novamente as opções de lazer do condomínio Terras de São José, onde a casa MB16155 está localizada. Um momento, por favor. 🧐{'name': 'get_property_by_reference', 'arguments': '{"reference": "MB16155"}'}
Tool: {"hits": [{"id": "03d03877-4ed3-4347-97e0-e36a0adb9d77", "ref": "MB16155", "agency_code": "MB", "property_type_code": "26", "property_type": "Casas de Condomínio ", "business_type_code": "V", "use_type_code": "R", "origin_type_code": "1", "is_launch": "0", "zip_code": "13306385", "street_name": "CONDOMÍNIO", "address": "Terras de São José", "number": null, "sql_id": null, "location": "0101000020E61000004ADA43B1CB9A3BC0F246414B325048C0", "reference": null, "city_code": "9260", "city": "Itu", "state": "SP", "region": "Condomínio Terras de São José", "neighborhood": "Condomínio Terras de São José", "neighborhood_code": "19972", "region_code1": null, "region_code2": null, "region_code3": null, "value": "7200000", "is_for_sale": "1", "sale_value": "7200000", "sale_value_per_m2": "12100.8", "is_for_rent": "0", "rent_value": "0", "rent_value_per_m2": "0", "condo_fee": "1795.25", "iptu": "659.73", "bedrooms": null, "suites": null, "parking_spaces": null, "total_area": "2476", "usable_area": "595", "size": null, "promotion": "\"Casa de vidro\" \nLuxuosa casa com 595m² de área construída, agregados com 6 suítes + espaço para home theater, cozinha totalmente planejada com equipamentos de última geração, área de serviço com lavanderia equipada, dormitório para funcionário com banheiro.\nAla social com sala de estar, sala de jantar, living, ambientes amplos e bem iluminados. \nÁrea gourmet equipada, deck, fogo de chão, piscina de borda infinita com cascata complementam a parte externa do imóvel. \nGaragem coberta e descoberta para vários veículos.\nConclusão da obra prevista para setembro/2023.\n", "unit_details": "Acesso 24 Horas, Área de Serviço, Churrasqueira, Cozinha Americana, Dependência de Empregados, Ducha, Fogão, Home Theater, Lavabo, Piscina, Piso Frio, Quintal, Sala de Estar, Sala de Jantar, Vista Exterior", "condo_details": "Academia, Área de Estar Externa, Área de Lazer, Campo de Futebol, Campo de Golfe, Guarita, Heliponto, Infra-Internet, Jardim, Lago, Portaria 24Hrs, Quadra de Tênis, Segurança 24 Horas, Sistema de Segurança", "tag": null, "with_photos": "1", "with_text": "1", "with_financing": "-1", "entry_value": null, "installment_value": null, "status": "1", "living_rooms": null, "professional_code": null, "development": "Terra de São José II", "complement": "Al. Das Bapebas", "video": null, "payment_conditions": null, "surroundings": null, "classification_code": null, "bathrooms": null, "exclusivity": "0", "on_call": "0", "remaining": "0", "accepts_swap": "-1", "has_income": "-1", "building_name": null, "title": "CASA ESPETACULAR | 6 SUÍTES | 8 VAGAS | 595M²", "print_text": null, "publication_date": "2025-04-01 08:36:07+00", "publication_agency_code": "MB", "photo_quantity": "16", "iptu_type": "Mensal", "system_rule": "2", "photo_change_date": "2023-11-07 09:06:26+00", "property_status": "SemPromo", "registration_date": "2023-06-30 11:15:16+00", "available_for_seasonal_rental": "0", "seasonal_rental_value": "0", "capacity": null, "disabled_property": "0", "rental_period": null, "furniture_status": null, "unit_features": "/348/340/31/91/10/95/68/73/337/16/101/35/430/346/460/", "condo_features": "/285/118/22/294/3/23/54/439/34/356/20/18/436/446/", "previous_code": null, "development_photo_change_date": null, "residential": "S", "commercial": "N", "rural": "N", "industrial": "N", "simplified_type_code": "1", "simplified_type": "CASA", "elevator_quantity": null, "created_at": "2023-06-30 11:15:16+00", "updated_at": "2023-11-07 09:06:26+00", "description": null, "active": "TRUE", "commercial_neighborhood": null, "new_title": "Casa Exclusiva em Condomínio Terras de São José com 6 Suítes e 2.476 m²"}], "query": "", "processingTimeMs": 1, "limit": 20, "offset": 0, "estimatedTotalHits": 1}
AI: Com certeza! As opções de lazer disponíveis no condomínio Terras de São José são:

*   Academia 💪
*   Área de Estar Externa 🌳
*   Área de Lazer 🎉
*   Campo de Futebol ⚽
*   Campo de Golfe ⛳
*   Heliponto 🚁
*   Jardim 🌷
*   Lago 🏞️
*   Quadra de Tênis 🎾

O condomínio também oferece infraestrutura de segurança completa. 🛡️

Posso ajudar com mais alguma informação? 😊"""

    print("\nTesting the new problematic case with debug=True:")
    result_new = verify_json_existence(test_string_new, debug=True)
    status_new = (
        "PASSED (Detected JSON)" if result_new else "FAILED (Did not detect JSON)"
    )
    print(f"\nFinal Result for new case: {result_new} - {status_new}")

    print("-" * 30)

    # You can add other test cases here as needed
    # test_ai_string = "Com certeza! Posso buscar opções de casas em condomínio na cidade de Itu para você. 🏘️ Só um momento.{'name': 'search_properties', 'arguments': '{\"query\": \"casas de condom\\u00ednio em Itu\"}'}"
    # print("\nTesting the previous problematic case with debug=True:")
    # result_ai = verify_json_existence(test_ai_string, debug=True)
    # status_ai = "PASSED" if result_ai else "FAILED"
    # print(f"\nFinal Result for previous case: {result_ai} - {status_ai}")
