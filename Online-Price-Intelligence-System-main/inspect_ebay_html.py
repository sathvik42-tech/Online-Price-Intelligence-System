from bs4 import BeautifulSoup

def inspect_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Check for s-item
    s_items = soup.select('.s-item')
    print(f"Total '.s-item' found: {len(s_items)}")
    
    # Check for li.s-item
    li_s_items = soup.select('li.s-item')
    print(f"Total 'li.s-item' found: {len(li_s_items)}")
    
    if s_items:
        print("\nStructure of first .s-item:")
        first_item = s_items[0]
        print(f"Tag: {first_item.name}")
        print(f"Classes: {first_item.get('class')}")
        
        # Check sub-elements
        title = first_item.select_one('.s-item__title')
        print(f"Title element found: {title is not None}")
        if title:
            print(f"Title text: '{title.get_text().strip()}'")
            
        price = first_item.select_one('.s-item__price')
        print(f"Price element found: {price is not None}")
        if price:
            print(f"Price text: '{price.get_text().strip()}'")

    # Check for potential bot detection markers if items are 0
    if len(s_items) == 0:
        print("\nSearching for bot detection markers...")
        if "captcha" in html.lower(): print("- Found 'captcha'")
        if "security" in html.lower(): print("- Found 'security'")
        if "robot" in html.lower(): print("- Found 'robot'")

if __name__ == "__main__":
    inspect_html('ebay_debug_source.html')
