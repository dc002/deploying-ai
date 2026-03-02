import requests

def get_country_info(country_name: str) -> str:
    try:
        url = f"https://restcountries.com/v3.1/name/{country_name}"
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return (
                "I couldn't find any country information for that name, "
                "but you can try searching again with a different one."
            )

        results = response.json()

        exact_match = []
        other_matches = []

        for item in results:
            common = item.get("name", {}).get("common", "").lower()
            official = item.get("name", {}).get("official", "").lower()

            if common == country_name.lower() or official == country_name.lower():
                exact_match.append(item)
            else:
                other_matches.append(item)

        # Exact match comes before other matches
        ordered_results = exact_match + other_matches

        summaries = []
        for data in ordered_results:
            name = data.get("name", {}).get("common", "Unknown")
            capital = data.get("capital", ["Unknown"])[0]
            region = data.get("region", "Unknown")
            population = data.get("population", "Unknown")
            area = data.get("area", "Unknown")

            borders = data.get("borders", [])
            border_list = ", ".join(borders) if borders else "none"

            currencies = data.get("currencies", {})
            currency_names = ", ".join(
                [c.get("name", "") for c in currencies.values()]
            ) or "Unknown"

            languages = data.get("languages", {})
            language_names = ", ".join(languages.values()) or "Unknown"

            summary = (
                f"{name}:\n"
                f"- Capital: {capital}\n"
                f"- Region: {region}\n"
                f"- Population: {population:,}\n"
                f"- Area: {area:,} square kilometers\n"
                f"- Borders: {border_list}\n"
                f"- Currency: {currency_names}\n"
                f"- Languages: {language_names}\n"
            )

            summaries.append(summary)

        return (
            "Here's what I found based on your search:\n\n"
            + "\n".join(summaries)
            + "\nHope this gives you a helpful overview of the countries that match that name."
        )

    except Exception:
        return (
            "I had trouble reaching the country information service, "
            "but you can try again in a moment."
        )
