import re
from typing import Dict, Any, List

def analyze_and_score_lead(requirement: str, budget: str, source: str) -> Dict[str, Any]:
    """
    AI Lead Scoring System.
    Analyzes the requirement description, budget selection, and marketing source
    to calculate a score (0-100), classify the lead (Hot, Warm, Cold), and output insights.
    """
    req_lower = requirement.lower() if requirement else ""
    budget_lower = budget.lower() if budget else ""
    
    score = 40 # Base score
    
    # 1. Budget Score adjustment
    if "100,000" in budget_lower or "100k" in budget_lower:
        score += 35
    elif "50,000" in budget_lower or "50k" in budget_lower:
        score += 25
    elif "25,000" in budget_lower or "25k" in budget_lower:
        score += 15
    elif "5,000" in budget_lower or "10,000" in budget_lower:
        score -= 10
        
    # 2. Requirement urgency and size clues
    high_intent_keywords = ["immediate", "ready to start", "complete renovation", "full villa", "commercial office", "new home", "construction"]
    medium_intent_keywords = ["looking for ideas", "redesign", "kitchen remodel", "bedroom design", "living room styling"]
    low_intent_keywords = ["just curious", "consultation only", "cheap", "paint colors", "price query"]
    
    for kw in high_intent_keywords:
        if kw in req_lower:
            score += 15
            break
            
    for kw in medium_intent_keywords:
        if kw in req_lower:
            score += 5
            break

    for kw in low_intent_keywords:
        if kw in req_lower:
            score -= 15
            break

    # 3. Source scoring
    source_lower = source.lower() if source else ""
    if "referral" in source_lower:
        score += 15
    elif "whatsapp" in source_lower or "instagram" in source_lower:
        score += 5
        
    # Keep score bounded between 0 and 100
    score = max(0, min(100, score))
    
    # 4. Classification
    if score >= 80:
        classification = "Hot"
        insights = f"Highly qualified lead showing immediate demand and prime budget range. Source: {source}. Recommended action: Call within 15 minutes."
    elif score >= 50:
        classification = "Warm"
        insights = f"Moderate interest. The lead has average design scope and matching budget. Source: {source}. Action: Send portfolio and follow up via email."
    else:
        classification = "Cold"
        insights = f"Low budget threshold or weak purchase signals. Lead needs nurturing. Source: {source}. Action: Add to email newsletter list."
        
    return {
        "score": score,
        "classification": classification,
        "insights": insights
    }

def generate_blog_content(title: str, category: str) -> Dict[str, str]:
    """
    AI Blog Generator. Generates outline, summary, and rich content.
    """
    clean_title = title.strip()
    seo_slug = re.sub(r'[^a-zA-Z0-9]+', '-', clean_title.lower()).strip('-')
    
    summary = f"An expert guide exploring the best ways to incorporate premium styling, spatial efficiency, and aesthetics in {category} interior spaces."
    
    content = f"""
    <h2>Elevating Your Space: The Definitive Guide to {clean_title}</h2>
    <p>When it comes to high-end design in the <strong>{category}</strong> sector, details make all the difference. Designing a modern space involves merging luxury textures, ambient lighting, and bespoke furniture layouts.</p>
    
    <h3>Key Elements of Premium {category} Design</h3>
    <ul>
        <li><strong>Spatial Flow:</strong> Craft layout grids that align with focal axes and daylight patterns.</li>
        <li><strong>Premium Textures:</strong> Introduce raw marble, textured plaster wall finishes, and custom millwork.</li>
        <li><strong>Smart Integration:</strong> Conceal smart home automation controls and wire paths cleanly.</li>
    </ul>

    <h3>Implementation Steps</h3>
    <p>To successfully integrate these themes, start by stripping back excess items, planning clear pathways, and curating a cohesive palette of three primary colors and two accent metallics.</p>
    """
    
    return {
        "title": clean_title,
        "slug": seo_slug,
        "summary": summary,
        "content": content.strip(),
        "seo_title": f"{clean_title} | Premium {category} Design Tips",
        "seo_description": summary[:140] + "..."
    }

def generate_seo_tags(title: str, body_text: str) -> Dict[str, str]:
    """
    AI SEO Metadata Generator.
    Calculates dynamic titles, meta descriptions, and tags.
    """
    clean_text = re.sub(r'<[^>]*>', '', body_text)[:150].strip()
    return {
        "seo_title": f"{title} | Luxe Design & Architecture",
        "seo_description": f"{clean_text}... Discover luxury interior trends and solutions by Luxe Design.",
        "og_tags": f"<meta property='og:title' content='{title}' />\n<meta property='og:description' content='{clean_text}' />",
        "schema_markup": {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": title,
            "description": clean_text,
            "publisher": {
                "@type": "LocalBusiness",
                "name": "Luxe Design & Architecture"
            }
        }
    }

def generate_faq_list(service_name: str) -> List[Dict[str, str]]:
    """
    AI FAQ Generator based on service keywords.
    """
    return [
        {
            "question": f"How long does a premium {service_name} project typically take?",
            "answer": f"A comprehensive {service_name} layout and execution takes between 8 to 16 weeks, depending on customization scale and structural modification requirements."
        },
        {
            "question": f"Can I select custom materials and custom millwork?",
            "answer": f"Absolutely. We work directly with bespoke stone quarries, artisan timber workers, and smart home fabricators to curate tailor-made solutions."
        },
        {
            "question": f"Do you coordinate with onsite structural contractors?",
            "answer": "Yes. Our senior designer acts as the project manager, executing structural checks, coordinating layout approvals, and verifying quality control onsite."
        }
    ]

def get_ai_chat_response(messages: List[Dict[str, str]], role: str = "Client") -> str:
    """
    AI Chat Assistant. Responsive to role (Designer or Client) providing tailored interior advice.
    """
    last_message = messages[-1]["content"].lower() if messages else ""
    
    if role == "Admin" or role == "Designer":
        # Business/Designer context
        if "lead" in last_message or "crm" in last_message:
            return "To qualify a lead faster, check the AI Lead Score widget. Hot leads have a score above 80. I recommend scheduling an intro call."
        elif "project" in last_message or "milestone" in last_message:
            return "You can update milestones directly in the Projects view. Setting status to 'Execution' automatically schedules the construction crew notification."
        return "Hello Designer. I can help summarize lead briefs, draft follow-up email reminders, or auto-generate blog schemas. What would you like to build today?"
    else:
        # Client context
        if "invoice" in last_message or "pay" in last_message:
            return "You can view and settle invoices directly under the Payments tab in your Client Portal. Payments support wire transfer and secure card processing."
        elif "status" in last_message or "progress" in last_message:
            return "Your project is currently in the 'Design' phase. The floor plan draft and material sample board are ready for review in your documents section."
        return "Welcome to Luxe Design. I am your project concierge. I can guide you through design timelines, materials approval, and document access. How can I help you?"
