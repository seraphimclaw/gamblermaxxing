import requests
import json

def find_undervalued_markets(min_no_prob=0.20, max_no_prob=0.50, limit=10):
    """
    Parcourt les marchés Polymarket ouverts et identifie jusqu'à 10 marchés
    binaires (Oui/Non) dont la probabilité de 'Non' est comprise entre
    min_no_prob et max_no_prob.

    La probabilité de 'Non' est déduite du prix du token 'Non'.
    """
    url = "https://gamma-api.polymarket.com/markets"
    # Nous allons chercher 100 marchés pour nous assurer d'en trouver 10 qui correspondent
    params = {"closed": "false", "limit": 100}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status() # Lève une exception pour les codes d'erreur HTTP
    except requests.exceptions.RequestException as e:
        return f"Erreur lors de la requête API: {e}"

    markets = response.json()
    undervalued_markets = []

    for market in markets:
        # Nous nous concentrons uniquement sur les marchés binaires (2 issues)
        if len(market.get('outcomes', [])) != 2:
            continue
        
        # Le prix est représenté par le champ 'price' sur les objets 'outcomes'
        # Nous devons identifier quel outcome est 'Non'.
        no_outcome = None
        for outcome in market['outcomes']:
            if outcome['title'].upper() == 'NO':
                no_outcome = outcome
                break
        
        if not no_outcome:
            continue
            
        # Le prix représente la probabilité (de 0 à 1)
        no_price = float(no_outcome['price'])
        
        # Vérification du critère : Probabilité de "Non" entre 20% et 50%
        if min_no_prob <= no_price <= max_no_prob:
            # Récupérer la probabilité de Oui pour référence
            yes_price = 1.0 - no_price
            
            undervalued_markets.append({
                "title": market['question'],
                "url": market['url'],
                "prob_non_percent": round(no_price * 100, 2),
                "prob_oui_percent": round(yes_price * 100, 2),
                "volume_usd": market.get('volume_usd', 'N/A')
            })

        if len(undervalued_markets) >= limit:
            break

    if not undervalued_markets:
        return "Aucun marché correspondant aux critères de non-probabilité (20-50%) trouvé."

    output = f"Marchés Polymarket avec Probabilité de NON entre {int(min_no_prob*100)}% et {int(max_no_prob*100)}%:\n"
    for m in undervalued_markets:
        output += f"\n- {m['title']}\n  -> NON: {m['prob_non_percent']}%, OUI: {m['prob_oui_percent']}%\n  -> URL: {m['url']}\n  -> Volume: ${m['volume_usd']}\n"
        
    return output

if __name__ == "__main__":
    result = find_undervalued_markets()
    print(result)

