from pydantic_ai import RunContext
import httpx
import os
from datetime import datetime
import json
import re


async def web_search(ctx: RunContext[str], query: str) -> str:
    """
    Search the web for information using multiple sources.
    
    Args:
        ctx: The run context
        query: The search query to look up
    
    Returns:
        Formatted search results with relevant information
    """
    try:
        headers = {
            "User-Agent": "ResearchAgent/1.0 (Educational Project; Python/httpx)"
        }
        async with httpx.AsyncClient(follow_redirects=True, timeout=15.0, headers=headers) as client:
            results = []
            
            # Method 1: Try DuckDuckGo Instant Answer API first (most reliable)
            try:
                ddg_api_response = await client.get(
                    "https://api.duckduckgo.com/",
                    params={
                        "q": query,
                        "format": "json",
                        "no_html": 1,
                        "skip_disambig": 1
                    }
                )
                
                if ddg_api_response.status_code == 200:
                    ddg_data = ddg_api_response.json()
                    
                    # Get abstract text
                    abstract = ddg_data.get("Abstract", "")
                    heading = ddg_data.get("Heading", "")
                    abstract_url = ddg_data.get("AbstractURL", "")
                    
                    if abstract:
                        results.append(f"**{heading or 'Search Result'}**\n")
                        results.append(abstract)
                        if abstract_url:
                            results.append(f"\n🔗 {abstract_url}\n")
                    
                    # Get related topics
                    related = ddg_data.get("RelatedTopics", [])
                    if related and not abstract:
                        results.append("**Related Information:**\n")
                        count = 0
                        for topic in related[:5]:
                            if isinstance(topic, dict):
                                if "Text" in topic:
                                    results.append(f"{count + 1}. {topic['Text']}")
                                    if "FirstURL" in topic:
                                        results.append(f"   🔗 {topic['FirstURL']}\n")
                                    count += 1
                                elif "Topics" in topic:
                                    # Handle nested topics
                                    for subtopic in topic["Topics"][:3]:
                                        if isinstance(subtopic, dict) and "Text" in subtopic:
                                            results.append(f"{count + 1}. {subtopic['Text']}")
                                            if "FirstURL" in subtopic:
                                                results.append(f"   🔗 {subtopic['FirstURL']}\n")
                                            count += 1
                            if count >= 5:
                                break
            except Exception as e:
                pass
            
            # Method 2: Try Wikipedia OpenSearch API
            if len(results) < 2:
                try:
                    wiki_response = await client.get(
                        "https://en.wikipedia.org/w/api.php",
                        params={
                            "action": "opensearch",
                            "search": query,
                            "limit": 5,
                            "namespace": 0,
                            "format": "json"
                        }
                    )
                    
                    if wiki_response.status_code == 200:
                        wiki_data = wiki_response.json()
                        if len(wiki_data) >= 4 and wiki_data[1]:
                            titles = wiki_data[1]
                            descriptions = wiki_data[2]
                            urls = wiki_data[3]
                            
                            # Only add if we have meaningful descriptions
                            has_descriptions = any(desc for desc in descriptions if desc)
                            
                            if has_descriptions:
                                if not results or "Wikipedia" not in "\n".join(results):
                                    results.append(f"\n**Wikipedia Results:**\n")
                                for i in range(min(len(titles), 3)):
                                    if titles[i] and descriptions[i]:  # Only add if has description
                                        results.append(f"{i+1}. **{titles[i]}**")
                                        results.append(f"   {descriptions[i]}")
                                        if i < len(urls) and urls[i]:
                                            results.append(f"   🔗 {urls[i]}\n")
                except Exception as e:
                    pass
            
            # Method 3: Try to get Wikipedia page extract for more detailed info
            if len(results) < 2:
                try:
                    # First try to search for relevant titles
                    search_response = await client.get(
                        "https://en.wikipedia.org/w/api.php",
                        params={
                            "action": "opensearch",
                            "search": query,
                            "limit": 1,
                            "namespace": 0,
                            "format": "json"
                        }
                    )
                    
                    search_term = query
                    if search_response.status_code == 200:
                        search_data = search_response.json()
                        if len(search_data) >= 2 and search_data[1]:
                            # Use the first search result title
                            search_term = search_data[1][0]
                    
                    # Now get the extract for that page
                    extract_response = await client.get(
                        "https://en.wikipedia.org/w/api.php",
                        params={
                            "action": "query",
                            "format": "json",
                            "prop": "extracts|info",
                            "exintro": True,
                            "explaintext": True,
                            "inprop": "url",
                            "titles": search_term,
                            "redirects": 1
                        }
                    )
                    
                    if extract_response.status_code == 200:
                        extract_data = extract_response.json()
                        pages = extract_data.get("query", {}).get("pages", {})
                        for page_id, page in pages.items():
                            if page_id != "-1" and "extract" in page:
                                title = page.get("title", "")
                                extract = page.get("extract", "")
                                url = page.get("fullurl", f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}")
                                if extract and len(extract) > 50:  # Only if meaningful content
                                    # Limit extract to first 600 characters
                                    extract = extract[:600] + "..." if len(extract) > 600 else extract
                                    if not results:
                                        results.append(f"**{title}**\n")
                                    else:
                                        results.append(f"\n**{title}**\n")
                                    results.append(extract)
                                    results.append(f"\n🔗 {url}\n")
                except Exception as e:
                    pass
            
            # Method 4: Use DuckDuckGo HTML scraping (simplified)
            if not results:
                try:
                    ddg_response = await client.get(
                        "https://html.duckduckgo.com/html/",
                        params={"q": query},
                        headers={
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                        },
                        timeout=10.0
                    )
                    
                    if ddg_response.status_code == 200:
                        html = ddg_response.text
                        # Simple regex to extract result snippets
                        snippet_pattern = r'<a class="result__snippet"[^>]>(.?)</a>'
                        snippets = re.findall(snippet_pattern, html, re.DOTALL)[:3]
                        
                        if snippets:
                            results.append("**Web Results:**\n")
                            for i, snippet in enumerate(snippets, 1):
                                # Clean HTML tags
                                clean_snippet = re.sub(r'<[^>]+>', '', snippet)
                                clean_snippet = clean_snippet.strip()
                                if clean_snippet:
                                    results.append(f"{i}. {clean_snippet[:200]}")
                except Exception as e:
                    pass
            
            if results:
                return "\n".join(results)
            else:
                return f"Unable to find detailed information for '{query}'. The search did not return results. Try rephrasing your query."
                
    except Exception as e:
        return f"Search error: {str(e)[:150]}"


async def save_research(ctx: RunContext[str], topic: str, content: str) -> str:
    """
    Save research findings and agent's response to a file. Use this when the user 
    explicitly asks to save, store, or keep research information.
    
    IMPORTANT: The 'content' parameter should include:
    - The complete research summary you prepared
    - All key findings and facts discovered
    - Sources and URLs referenced
    
    Args:
        ctx: The run context
        topic: The research topic or title (e.g., "Chetan Bhagat's first book")
        content: Your complete research response with all findings, facts, and sources
    
    Returns:
        Confirmation message with file location
    
    Example:
        topic = "Quantum Computing"
        content = "Quantum computing uses quantum mechanics...
                   Key findings:
                   1. Uses qubits instead of bits
                   2. Applications in cryptography
                   Sources: [wikipedia links]"
    """
    try:
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_topic = "".join(c if c.isalnum() or c in (' ', '') else '' for c in topic)
        safe_topic = safe_topic.replace(' ', '_')[:50]  # Limit length
        filename = f"logs/research_{safe_topic}_{timestamp}.txt"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"Research Topic: {topic}\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 70 + "\n\n")
            f.write(content)
            f.write("\n\n" + "=" * 70)
            f.write(f"\nSaved: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return f"✅ Research saved successfully to: {filename}"
        
    except Exception as e:
        return f"❌ Error saving research: {str(e)}"


async def get_date_time(ctx: RunContext[str]) -> str:
    """
    Get the current date and time.
    
    Args:
        ctx: The run context
    
    Returns:
        Current date and time formatted as a string
    """
    now = datetime.now()
    return f"📅 Current date and time: {now.strftime('%A, %B %d, %Y at %I:%M:%S %p')}"