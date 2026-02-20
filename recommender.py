from database import FalkorDBClient

def suggest_technologies(input_name: str):
    """
    Suggests technologies based on similar projects in FalkorDB.
    """
    falkor_client = FalkorDBClient()
    
    # Use toLower for case-insensitive matching
    query = """
    MATCH (p:Project)-[:USES]->(t:Technology) 
    WHERE toLower(p.name) CONTAINS toLower($name) 
    RETURN t.name AS tag, count(t) AS score 
    ORDER BY score DESC 
    LIMIT 5
    """
    
    params = {"name": input_name}
    print(f"DEBUG: Searching FalkorDB for: '{input_name}'")
    
    try:
        result = falkor_client.graph.query(query, params)
        suggestions = []
        
        # result is a ResultSet that can be iterated
        for row in result.result_set:
            # Each row is a list of returned values [t.name, count(t)]
            tech_name = row[0]
            if isinstance(tech_name, bytes):
                tech_name = tech_name.decode('utf-8')
            
            suggestions.append({
                "technology": str(tech_name), 
                "score": int(row[1])
            })
            
        print(f"DEBUG: Found {len(suggestions)} suggestions for '{input_name}'")
        return suggestions
    except Exception as e:
        print(f"ERROR: FalkorDB query failed: {e}")
        return []
