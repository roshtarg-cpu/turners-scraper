"""Turners.co.nz Car Listings Scraper."""
import asyncio
import re
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from urllib.parse import urljoin, parse_qs, urlparse

import httpx
from apify import Actor
from bs4 import BeautifulSoup


def extract_car_details(soup: BeautifulSoup, url: str) -> Optional[Dict[str, Any]]:
    """Extract car details from a listing page."""
    try:
        # Title
        h1 = soup.find('h1')
        title = h1.get_text(strip=True) if h1 else None
        
        # Extract specs from dt/dd pairs
        specs = {}
        dts = soup.find_all('dt')
        for dt in dts:
            label = dt.get_text(strip=True)
            dd = dt.find_next_sibling('dd')
            if dd:
                value = dd.get_text(strip=True)
                specs[label.lower().replace(' ', '_')] = value
        
        # Price - find BUY NOW price
        price = None
        price_elems = soup.find_all(string=re.compile(r'\$[\d,]+'))
        for p_text in price_elems:
            # Look for the main BUY NOW price
            parent = p_text.find_parent()
            if parent and 'BUY NOW' in parent.get_text():
                match = re.search(r'\$([\d,]+)', p_text)
                if match:
                    price = match.group(1)
                    break
        
        # If no BUY NOW price, try to find any price
        if not price:
            price_match = re.search(r'\$([\d,]+)', soup.get_text())
            if price_match:
                price = price_match.group(1)
        
        # Extract location from specs or search text
        location = specs.get('location') or None
        
        # Images
        images = []
        img_tags = soup.find_all('img', src=re.compile(r'vehicleimages|cars|stock', re.I))
        for img in img_tags:
            src = img.get('src')
            if src and not src.endswith('default-car.png'):
                full_url = urljoin(url, src)
                images.append(full_url)
        
        # Description - try to find main description
        description = None
        desc_container = soup.find(['div', 'section'], class_=re.compile(r'description|details', re.I))
        if desc_container:
            description = desc_container.get_text(strip=True)[:500]
        
        return {
            'url': url,
            'title': title or f"{specs.get('year', '')} {specs.get('vehicle', '')}".strip(),
            'year': specs.get('year'),
            'make': specs.get('vehicle', '').split()[0] if specs.get('vehicle') else None,
            'model': ' '.join(specs.get('vehicle', '').split()[1:]) if specs.get('vehicle') else None,
            'price': price,
            'location': location,
            'odometer': specs.get('odometer'),
            'transmission': specs.get('transmission'),
            'fuelType': specs.get('fuel'),
            'engine': specs.get('engine'),
            'color': specs.get('colour'),
            'bodyStyle': specs.get('body_style'),
            'driveType': specs.get('drive'),
            'seats': specs.get('seats'),
            'origin': specs.get('origin'),
            'wofExpiry': specs.get('wof_expiry'),
            'regExpiry': specs.get('reg_expiry'),
            'description': description,
            'images': images,
            'scrapedAt': datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        Actor.log.error(f"Error extracting car details: {e}")
        return None


async def scrape_listing_page(client: httpx.AsyncClient, page_num: int, page_size: int = 20) -> list:
    """Scrape a single listing page."""
    url = f"https://www.turners.co.nz/Cars/Used-Cars-for-Sale/?sortorder=8,DESC&pagesize={page_size}&pageno={page_num}"
    
    try:
        response = await client.get(url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all car listing links
        car_urls = []
        links = soup.find_all('a', href=re.compile(r'/Cars/Used-Cars-for-Sale/[^/]+/[^/]+/\d+', re.I))
        
        for link in links:
            href = link.get('href')
            if href:
                full_url = urljoin(url, href)
                if full_url not in car_urls:
                    car_urls.append(full_url)
        
        Actor.log.info(f"Found {len(car_urls)} car URLs on page {page_num}")
        return car_urls
        
    except Exception as e:
        Actor.log.error(f"Error scraping listing page {page_num}: {e}")
        return []


async def scrape_car_detail(client: httpx.AsyncClient, url: str) -> Optional[Dict[str, Any]]:
    """Scrape details from a single car listing."""
    try:
        response = await client.get(url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        return extract_car_details(soup, url)
        
    except Exception as e:
        Actor.log.error(f"Error scraping car detail {url}: {e}")
        return None


async def main() -> None:
    """Main scraper function."""
    async with Actor:
        # Get input
        actor_input = await Actor.get_input() or {}
        
        max_results = actor_input.get('maxResults', 10)
        location = actor_input.get('location')
        make = actor_input.get('make')
        model = actor_input.get('model')
        price_min = actor_input.get('priceMin')
        price_max = actor_input.get('priceMax')
        year_min = actor_input.get('yearMin')
        year_max = actor_input.get('yearMax')
        proxy_config = actor_input.get('proxyConfiguration')
        
        Actor.log.info(f"Starting scrape with maxResults={max_results}")
        
        # Set up HTTP client with proxy if configured
        client_kwargs = {
            'follow_redirects': True,
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        }
        
        # Add proxy if configured
        if proxy_config:
            proxy_url = Actor.create_proxy_configuration(proxy_config)
            if proxy_url:
                client_kwargs['proxies'] = proxy_url
                Actor.log.info("Using Apify proxy")
        
        async with httpx.AsyncClient(**client_kwargs) as client:
            # Build search URL with filters
            base_url = "https://www.turners.co.nz/Cars/Used-Cars-for-Sale/?"
            params = []
            
            if location:
                # Note: Would need to map location names to Turners location IDs
                params.append(f"location={location}")
            
            if make:
                params.append(f"make={make}")
            
            if model:
                params.append(f"model={model}")
            
            # Pagination
            scraped_count = 0
            page_num = 1
            page_size = min(20, max_results)  # Turners uses max 20 per page
            
            while scraped_count < max_results:
                # Get car URLs from listing page
                car_urls = await scrape_listing_page(client, page_num, page_size)
                
                if not car_urls:
                    Actor.log.info("No more cars found")
                    break
                
                # Scrape each car
                for url in car_urls:
                    if scraped_count >= max_results:
                        break
                    
                    car_data = await scrape_car_detail(client, url)
                    
                    if car_data:
                        # Apply filters
                        skip = False
                        
                        # Price filter
                        if car_data.get('price'):
                            try:
                                price_val = int(car_data['price'].replace(',', ''))
                                if price_min and price_val < price_min:
                                    skip = True
                                if price_max and price_val > price_max:
                                    skip = True
                            except:
                                pass
                        
                        # Year filter
                        if car_data.get('year'):
                            try:
                                year_val = int(car_data['year'])
                                if year_min and year_val < year_min:
                                    skip = True
                                if year_max and year_val > year_max:
                                    skip = True
                            except:
                                pass
                        
                        if not skip:
                            # Push to dataset
                            await Actor.push_data(car_data)
                            scraped_count += 1
                            
                            if scraped_count % 10 == 0:
                                Actor.log.info(f"Scraped {scraped_count} cars")
                    
                    # Small delay between requests
                    await asyncio.sleep(0.5)
                
                # Move to next page
                page_num += 1
                
                # Avoid infinite loop
                if page_num > 100:
                    break
            
            Actor.log.info(f"Scraping complete. Total cars: {scraped_count}")
            
            # Save task context (MANDATORY per skill)
            await Actor.set_value('SAVED-TASK', {
                'actorId': Actor.get_env().get('actor_id'),
                'actorRunId': Actor.get_env().get('actor_run_id'),
                'defaultDatasetId': Actor.get_env().get('default_dataset_id'),
                'startedAt': Actor.get_env().get('started_at'),
                'input': actor_input,
                'stats': {
                    'itemsScraped': scraped_count,
                    'pagesVisited': page_num - 1,
                    'filters': {
                        'location': location,
                        'make': make,
                        'model': model,
                        'priceRange': f"{price_min}-{price_max}" if price_min or price_max else None,
                        'yearRange': f"{year_min}-{year_max}" if year_min or year_max else None
                    }
                }
            })


if __name__ == '__main__':
    asyncio.run(main())
