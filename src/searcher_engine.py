import time

def search_news(browser, search_phrase):
    """
    Searches for news on a website using the given search phrase.

    Args:
        browser (Selenium): The Selenium browser instance used for automation.
        search_phrase (str): The search phrase to input into the search field.
    
    Raises:
        Exception: If the search button or search field cannot be found or interacted with.
    """
    time.sleep(10)
    
    search_field = dynamic_searchbar(browser)

    if search_field is None:
        button_found = browser.execute_javascript("""
            const logs = [];
            logs.push('Searching for SVGs...');
            const svgs = document.querySelectorAll('svg');
            logs.push('SVGs found: ' + svgs.length);
            
            for (const svg of svgs) {
                const attributes = svg.attributes;
                let isSearchIcon = false;
                for (const attr of attributes) {
                    logs.push('SVG attribute: ' + attr.name + ', ' + attr.value);
                    if (attr.value.includes('search')) {
                        isSearchIcon = true;
                        break;
                    }
                }
                if (isSearchIcon) {
                    let button = svg.closest('button, a, div[role="button"], span[role="button"]');
                    if (button) {
                        logs.push('Found search icon, clicking button...');
                        const event = new MouseEvent('click', {
                            view: window,
                            bubbles: true,
                            cancelable: true
                        });
                        button.dispatchEvent(event);
                        return {logs: logs, clicked: true};
                    }
                }
            }
            
            logs.push('Searching for button with data-testid...');
            let button = document.querySelector('button[data-testid="search-button"]');
            if (button) {
                logs.push('Found search button, attempting to click...');
                const event = new MouseEvent('click', {
                    view: window,
                    bubbles: true,
                    cancelable: true
                });
                button.dispatchEvent(event);

                if (button.offsetParent !== null && !button.disabled) {
                    logs.push('Button is visible and enabled, clicked successfully.');
                    return {logs: logs, clicked: true};
                } else {
                    logs.push('Button is not visible or enabled.');
                }
            } else {
                logs.push('Search button not found.');
            }

            return {logs: logs, clicked: false};
        """)

        # Log all messages generated during the JavaScript execution
        for log in button_found['logs']:
            print(log)

        if not button_found['clicked']:
            raise Exception("Search button not found or not interactable")
        
        time.sleep(10)

        search_field = dynamic_searchbar(browser)

        if search_field is None:
            raise Exception("Search field not found")

    time.sleep(10)
    browser.input_text(search_field, search_phrase)
    time.sleep(10)
    browser.press_keys(search_field, 'ENTER')
    time.sleep(10)


def dynamic_searchbar(browser):
    """
    Dynamically finds the search bar on the web page.

    Args:
        browser (Selenium): The Selenium browser instance used for automation.
    
    Returns:
        WebElement: The search field element if found, otherwise None.
    """
    search_field = browser.execute_javascript("""
    function findSearchField() {
        const inputs = document.querySelectorAll('input');
        for (const input of inputs) {
            if (input.placeholder && input.placeholder.toLowerCase().includes('search')) {
                return input;
            }
            if (input.title && input.title.toLowerCase().includes('search')) {
                return input;
            }
        }
        return null;
    }
    return findSearchField();
    """)
    
    return search_field